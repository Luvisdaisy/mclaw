import logging

from mclaw.agents.state import AgentState

logger = logging.getLogger(__name__)


async def run_executor(state: AgentState) -> dict:
    """Iterate through tasks and execute each one using available tools.

    For Stage 1, this is a simplified executor that processes tasks
    linearly and delegates to MC Platform tools.
    """
    if state.current_task_index >= len(state.tasks):
        state.done = True
        return {"done": True}

    task = state.tasks[state.current_task_index]
    logger.info("Executing task %d/%d: %s", state.current_task_index + 1, len(state.tasks), task.description)

    try:
        result = await _execute_task(task, state)
        task.result = result
        task.status = "completed"
    except Exception as e:
        logger.error("Task failed: %s", e)
        task.status = "failed"
        task.result = str(e)
        state.error = str(e)

    state.current_task_index += 1
    if state.current_task_index >= len(state.tasks):
        state.done = True

    return {"current_task_index": state.current_task_index, "done": state.done, "error": state.error}


async def _execute_task(task, state: AgentState) -> str:
    """Execute a single task using the named tool."""
    tool_name = task.tool

    if tool_name == "query_mod":
        from mclaw.mc_platform.mod_query import query_mod
        info = await query_mod(task.description)
        if info.found:
            state.mod_info_cache[info.name] = {
                "name": info.name,
                "versions": info.versions,
                "loaders": info.loaders,
                "source": info.source,
            }
            return f"Found {info.name} on {info.source}: versions={info.versions}, loaders={info.loaders}"
        return f"Mod not found: {task.description}"

    if tool_name == "check_compatibility":
        from mclaw.mc_platform.compatibility import check_compatibility
        mod_name = task.description
        mod_data = state.mod_info_cache.get(mod_name, {})
        result = check_compatibility(
            mod_name=mod_name,
            mod_loaders=mod_data.get("loaders", []),
            mod_versions=mod_data.get("versions", []),
            target_mc_version=state.target_mc_version,
            target_loader=state.target_loader,
        )
        state.compatibility_results.append({
            "mod": mod_name,
            "compatible": result.compatible,
            "reason": result.reason,
            "warnings": result.warnings,
        })
        if result.compatible:
            return f"Compatible: {mod_name}"
        return f"Incompatible: {result.reason}"

    return f"Task noted: {task.description}"
