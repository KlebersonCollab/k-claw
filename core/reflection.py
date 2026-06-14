"""Reflection node - validates agent responses against the plan and catches missing tool calls."""

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from .state import HarnessState
from .ui_interface import EventType
from .model_caller import emit_event
import os


async def reflect_on_action(state: HarnessState) -> dict:
    """Analyze the last agent response for missing actions or plan deviations.
    Also enforces the EPISTEMOLOGICAL LOCK for destructive tools.

    Args:
        state: The current harness state.

    Returns:
        A dictionary that can trigger a self-correction message if needed.
    """
    scratchpad = state.get("scratchpad", [])
    if not scratchpad or not isinstance(scratchpad[-1], AIMessage):
        return {}

    last_msg = scratchpad[-1]
    content = last_msg.content or ""
    
    # EPISTEMOLOGICAL LOCK: Block destructive tools if path not verified
    if last_msg.tool_calls:
        verified_paths = state.get("verified_paths", set())
        destructive_tools = ["write_file", "replace_string", "run_shell"]
        lock_violations = []

        for tc in last_msg.tool_calls:
            if tc["name"] in destructive_tools:
                path = tc["args"].get("path") or tc["args"].get("file_path")
                if path:
                    from .dialog_control import is_path_verified
                    is_dir = tc["name"] not in ["write_file", "replace_string"]
                    if not is_path_verified(path, verified_paths, is_directory_op=is_dir):
                        lock_violations.append(
                            f"EPISTEMOLOGICAL VIOLATION: You are trying to use '{tc['name']}' on '{path}', "
                            "but you haven't verified this path yet. You MUST use 'read_file', 'grep_search' or "
                            "'list_directory' to establish a factual baseline before modifying any file."
                        )

        if lock_violations:
            await emit_event(EventType.THINKING_START, {"agent": "Epistemological Lock"})
            error_messages = [
                ToolMessage(
                    tool_call_id=tc["id"], 
                    content=f"ERROR: Epistemological Lock engaged. You must verify '{tc['args'].get('path')}' before acting."
                ) for tc in last_msg.tool_calls
            ]
            
            nudge = HumanMessage(content="\n\n".join(lock_violations))
            await emit_event(EventType.THINKING_END, {"agent": "Epistemological Lock"})
            return {
                "scratchpad": scratchpad + error_messages + [nudge],
                "iteration_count": state["iteration_count"] + 1
            }

    # Standard reflection (intent/validation)
    intent_keywords = ["vou solicitar", "delegar", "solicitar ao", "call the", "delegate to", "i will", "preciso envolver"]
    action_keywords = ["escrever", "alterar", "deletar", "executar", "write", "modify", "delete", "execute"]

    has_intent = any(kw in content.lower() for kw in intent_keywords)
    requires_validation = any(kw in content.lower() for kw in action_keywords)
    
    if (has_intent or requires_validation) and not last_msg.tool_calls:
        await emit_event(EventType.THINKING_START, {"agent": "Reflection"})
        
        correction_parts = []
        if has_intent:
            correction_parts.append(
                "ACTION REQUIRED: You expressed intent to act but didn't call a tool. "
                "Execute the tool call immediately (e.g., `delegate_to_agent`)."
            )
        
        if requires_validation:
            correction_parts.append(
                "EPISTEMOLOGICAL CHECK: Before performing this technical action, "
                "you MUST explicitly list your ASSUMPTIONS (premises). "
                "Verify file paths and module structure in the `GLOBAL BLACKBOARD` or via `grep_search` before acting."
            )
            
        await emit_event(EventType.THINKING_END, {"agent": "Reflection"})
        return {
            "scratchpad": scratchpad + [HumanMessage(content="\n\n".join(correction_parts))],
            "iteration_count": state["iteration_count"] + 1
        }

    return {}
