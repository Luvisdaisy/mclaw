import logging

from langgraph.graph import END, StateGraph

from mclaw.agents.executor import run_executor
from mclaw.agents.planner import run_planner
from mclaw.agents.state import AgentState

logger = logging.getLogger(__name__)


def _route_after_planner(state: AgentState) -> str:
    if not state.tasks:
        return END
    return "executor"


def _route_after_executor(state: AgentState) -> str:
    if state.done:
        return END
    if state.error and state.stage >= 2:
        return "diagnoser"
    return "executor"


def build_stage1_graph() -> StateGraph:
    """Build a StateGraph with Planner → Executor nodes."""
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", run_planner)
    workflow.add_node("executor", run_executor)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "executor")
    workflow.add_conditional_edges("executor", _route_after_executor, {
        "executor": "executor",
        END: END,
    })

    return workflow.compile()


def build_stage2_graph() -> StateGraph:
    """Build a StateGraph with Planner → Executor → Diagnoser routing."""
    from mclaw.agents.diagnoser import run_diagnoser  # deferred import

    workflow = StateGraph(AgentState)

    workflow.add_node("planner", run_planner)
    workflow.add_node("executor", run_executor)
    workflow.add_node("diagnoser", run_diagnoser)

    workflow.set_entry_point("planner")
    workflow.add_conditional_edges("planner", _route_after_planner, {
        "executor": "executor",
        END: END,
    })
    workflow.add_conditional_edges("executor", _route_after_executor, {
        "executor": "executor",
        "diagnoser": "diagnoser",
        END: END,
    })
    workflow.add_edge("diagnoser", END)

    return workflow.compile()
