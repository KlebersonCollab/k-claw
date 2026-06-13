"""Tool execution - handles tool calls from the agent with approval and hooks."""

from langchain_core.messages import ToolMessage
from .state import HarnessState
from tools import registry, classify_shell_command, risk_level_value
from infra.persistence import SessionLogger
from .ui_interface import get_ui, EventType, set_current_session_id
from .hooks import hook_manager
from .utils import redact_sensitive_info, cap_tool_output
from .model_caller import emit_event


async def execute_tools(state: HarnessState) -> dict:
    """Execute tool calls from the last message in the scratchpad.

    Handles:
    - YOLO mode injection for sub-agents
    - Pre-tool hooks
    - Human-in-the-loop approval
    - Tool execution with error handling
    - Output capping and redaction
    - Post-tool hooks

    Args:
        state: The current harness state.

    Returns:
        Updated state with tool results in scratchpad.
    """
    set_current_session_id(state['session_id'])
    scratchpad = state.get("scratchpad", [])
    last_message = scratchpad[-1]
    tool_messages = []
    logger = SessionLogger(state["session_id"])
    ui = get_ui()
    yolo_mode = state.get("yolo", False)

    blackboard_updates = {}

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        desc = registry.tools.get(tool_name)

        # YOLO Injection
        if tool_name == "delegate_to_agent":
            tool_args["parent_yolo"] = yolo_mode

        # PRE-TOOL HOOKS
        hook_result = await hook_manager.run_pre_tool(
            tool_name, tool_args,
            {"session_id": state["session_id"], "permissions": state["permissions"]}
        )

        if not hook_result.allowed:
            tool_messages.append(ToolMessage(tool_call_id=tool_call["id"], content=f"ERROR: Tool '{tool_name}' denied by hook."))
            continue

        tool_args = hook_result.modified_args

        # HITL DECISION
        needs_approval = False
        if not yolo_mode and desc and desc.requires_approval:
            needs_approval = True
            if tool_name == "run_shell":
                risk = classify_shell_command(tool_args.get("command", ""))
                if risk != "full" and risk_level_value(risk) <= risk_level_value(state["permissions"]):
                    needs_approval = False

        if needs_approval:
            if ui:
                approved = await ui.request_approval(tool_name, tool_args)
            else:
                approved = False
            if not approved:
                tool_messages.append(ToolMessage(tool_call_id=tool_call["id"], content="ERROR: Denied by user."))
                continue

        # EXECUTION
        await emit_event(EventType.TOOL_START, {"tool": tool_name, "args": tool_args})
        if desc:
            try:
                # Inject workspace_path from state if not already in args
                if "workspace_path" not in tool_args and state.get("workspace_path"):
                     tool_args["workspace_path"] = state["workspace_path"]
                result = await desc.handler.ainvoke(tool_args)
                
                # INTERCEPT BLACKBOARD UPDATES
                if isinstance(result, str) and result.startswith("__BLACKBOARD_UPDATE__:"):
                    import json
                    payload = json.loads(result.split("__BLACKBOARD_UPDATE__:")[1])
                    blackboard_updates.update(payload)
                    result = f"Successfully updated blackboard with keys: {list(payload.keys())}"

            except Exception as e:
                result = f"Error: {str(e)}"
        else:
            result = f"Error: Tool {tool_name} not found."

        # Capping ensures ALL tool outputs are truncated if too large
        capped_result = cap_tool_output(str(result))
        clean_result = redact_sensitive_info(capped_result)

        if not state.get("incognito", False):
            # Reduced log verbosity: Don't log full content in event
            logger.log_event("tool_execution", {"tool": tool_name, "status": "completed"})

        await emit_event(EventType.TOOL_END, {"tool": tool_name, "result": clean_result})

        # POST-TOOL HOOKS
        await hook_manager.run_post_tool(
            tool_name, tool_args, clean_result,
            {"session_id": state["session_id"]}
        )

        tool_messages.append(ToolMessage(tool_call_id=tool_call["id"], content=clean_result))

    if not state.get("incognito", False):
        logger.log_messages(tool_messages)

    new_scratchpad = scratchpad + tool_messages
    
    return_state = {"scratchpad": new_scratchpad}
    if blackboard_updates:
        return_state["blackboard"] = blackboard_updates
        
    return return_state
