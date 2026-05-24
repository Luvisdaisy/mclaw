import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from mclaw.agents.state import AgentState
from mclaw.llm.config import LLMConfig
from mclaw.llm.provider import create_llm, llm_invoke
from mclaw.prompts.crash_diagnosis import CRASH_DIAGNOSIS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def run_diagnoser(state: AgentState) -> dict:
    """Diagnose a crash from the executor error context or crash log text.

    Uses a single LLM call to classify crash root cause.
    If memory system is active (Stage 3+), checks cached cases first.
    """
    logger.info("Diagnoser invoked with error: %s", state.error)

    crash_context = _build_crash_context(state)

    # Stage 3+: Check memory cache before LLM call
    if state.stage >= 3:
        cached = await _check_memory_cache(crash_context)
        if cached:
            state.diagnosis = cached
            state.memory_hits = [cached]
            state.done = True
            logger.info("Memory cache hit, skipping LLM call")
            return {"diagnosis": cached, "done": True, "memory_hit": True}

    diagnosis = await _llm_diagnose(crash_context, state)
    state.diagnosis = diagnosis
    state.done = True

    return {"diagnosis": diagnosis, "done": True}


async def _check_memory_cache(crash_context: str) -> dict | None:
    """Check ChromaDB memory cache for similar crash cases."""
    try:
        from mclaw.memory.embedder import get_embedding
        from mclaw.memory.retriever import CaseRetriever
        from mclaw.memory.store import MemoryStore

        embedding = await get_embedding(crash_context)
        store = MemoryStore()
        retriever = CaseRetriever(store)

        hits = retriever.find_similar(embedding, threshold=0.65, top_k=1)
        if hits:
            return hits[0]["diagnosis"]
    except Exception as e:
        logger.info("Memory cache unavailable: %s", e)

    return None


async def _llm_diagnose(crash_context: str, state: AgentState) -> dict:
    """Perform LLM-based crash diagnosis."""
    config = LLMConfig()
    llm = create_llm(config)

    messages = [
        SystemMessage(content=CRASH_DIAGNOSIS_SYSTEM_PROMPT),
        HumanMessage(content=f"""Analyze this Minecraft issue and output a JSON diagnosis.

Error context:
```
{crash_context[:8000]}
```

Referenced mods: {', '.join(state.mod_info_cache.keys()) if state.mod_info_cache else 'unknown'}
"""),
    ]

    response = await llm_invoke(llm, messages)
    raw = response.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return _extract_diagnosis_json(raw)


def _build_crash_context(state: AgentState) -> str:
    """Build a crash description from the current agent state."""
    parts = [f"Error: {state.error}"] if state.error else []

    if state.compatibility_results:
        for r in state.compatibility_results:
            if not r.get("compatible", True):
                parts.append(f"Compatibility issue: {r.get('mod')} — {r.get('reason')}")

    if not parts:
        parts.append(f"User query: {state.user_query}")

    return "\n".join(parts)


def _extract_diagnosis_json(text: str) -> dict:
    """Extract diagnosis JSON from potentially malformed LLM output."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "category": "unknown",
            "confidence": 0.0,
            "summary": "Failed to parse diagnosis",
            "suspicious_mods": [],
        }
