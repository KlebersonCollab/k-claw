import os
import asyncio
from datetime import datetime
from typing import Literal, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from state import HarnessState
from tools import registry, classify_shell_command, risk_level_value
from persistence import SessionLogger
from dotenv import load_dotenv
from agent_loader import agent_loader
from utils import get_model, redact_sensitive_info, recursive_load_context, estimate_tokens, cap_tool_output
from ui_interface import get_ui, EventType
from hooks import hook_manager

load_dotenv()

# System prompt cache: session_id -> (permissions, context_summary, SystemMessage)
_SYS_PROMPT_CACHE: Dict[str, tuple] = {}

def _build_cache_key(state: HarnessState) -> str:
    """Build a cache key from session_id + fields that affect the prompt."""
    return f"{state['session_id']}:{state['permissions']}:{hash(state.get('context_summary', ''))}"

def get_cached_system_prompt(state: HarnessState) -> SystemMessage:
    """Return cached system prompt or build and cache it.

    The prompt is rebuilt only when session_id, permissions, or context_summary change.
    This avoids reconstructing the full prompt (with agent catalog and context files)
    on every single turn.
    """
    cache_key = _build_cache_key(state)
    if cache_key in _SYS_PROMPT_CACHE:
        return _SYS_PROMPT_CACHE[cache_key][2]

    sys_msg = _do_assemble_system_prompt(state)
    _SYS_PROMPT_CACHE[cache_key] = (state['permissions'], state.get('context_summary', ''), sys_msg)
    return sys_msg

def invalidate_system_prompt_cache(session_id: str) -> None:
    """Invalidate all cached prompts for a given session (e.g. after compaction)."""
    keys_to_remove = [k for k in _SYS_PROMPT_CACHE if k.startswith(f"{session_id}:")]
    for k in keys_to_remove:
        del _SYS_PROMPT_CACHE[k]

async def emit_event(event_type: EventType, data: Dict[str, Any] = None):
    ui = get_ui()
    if ui:
        await ui.on_event(event_type, data or {})

def _do_assemble_system_prompt(state: HarnessState) -> SystemMessage:
    is_sub_agent = state['session_id'].startswith("sub-")

    if is_sub_agent:
        return SystemMessage(content=(
            "You are a Specialist Sub-Agent. Focus strictly on your technical mission.\n"
            f"Permissions: {state['permissions']}\n"
            "ANTI-HALLUCINATION: If a tool fails, report the error. NEVER guess contents.\n"
            "TOKEN EFFICIENCY: Your output will be truncated if too large. Be concise."
        ))

    base_prompt = (
        "You are the Orchestrator Agent (Father).\n"
        "STRICT PROTOCOL:\n"
        "1. DELEGATE ALL technical tasks (reading/writing files, shell commands, research) to the appropriate specialist.\n"
        "2. You are responsible for identifying WHICH specialist is needed and providing a detailed MISSION briefing.\n"
        "3. Review the specialist's REPORT and relay the conclusion to the user.\n"
        "4. ANTI-HALLUCINATION: Never invent file contents or tool results. If delegation fails, report the error.\n"
        "5. TOKEN SAFETY: Huge tool outputs are truncated. Use specialists to analyze large data."
    )
    available_agents = agent_loader.list_available_agents()
    agents_catalog = "\n\n### Specialists:\n" + "\n".join([f"- {ag['id']}: {ag['description']}" for ag in available_agents])

    dynamic_context = recursive_load_context()
    if dynamic_context:
        capped_context = cap_tool_output(dynamic_context, max_chars=2000)
        extra_instructions = f"\n\n### Project Context:\n{capped_context}"
    else:
        extra_instructions = ""

    prompt_content = f"{base_prompt}{agents_catalog}{extra_instructions}\n\nPermissions: {state['permissions']}"
    if state.get('context_summary'):
        capped_memo = cap_tool_output(state['context_summary'], max_chars=2000)
        prompt_content += f"\n\n### State Memo:\n{capped_memo}"

    return SystemMessage(content=prompt_content)

async def call_model(state: HarnessState):
    agent_name = "Orchestrator" if not state['session_id'].startswith("sub-") else f"Specialist {state['session_id'].split('-')[1]}"

    await emit_event(EventType.THINKING_START, {"agent": agent_name, "session_id": state['session_id']})

    model = get_model()
    sys_msg = get_cached_system_prompt(state)

    scratchpad = state.get("scratchpad", [])
    messages_for_llm = [sys_msg] + state["messages"] + scratchpad

    authorized_tools = registry.get_langchain_tools(state["permissions"])
    model_with_tools = model.bind_tools(authorized_tools)
    response = await model_with_tools.ainvoke(messages_for_llm)

    await emit_event(EventType.THINKING_END, {"agent": agent_name})

    clean_content = redact_sensitive_info(response.content) if response.content else ""

    if response.tool_calls:
        new_scratchpad = scratchpad + [response]
        return {
            "scratchpad": new_scratchpad,
            "iteration_count": state["iteration_count"] + 1,
        }
    else:
        if not state.get("incognito", False):
            logger = SessionLogger(state["session_id"])
            # Log minimal event info instead of full response string
            logger.log_event("model_call", {"has_content": bool(clean_content), "tool_calls": len(response.tool_calls)})
            log_response = response.copy()
            log_response.content = clean_content
            logger.log_messages([log_response])

        return {
            "messages": [response],
            "scratchpad": None,
            "iteration_count": state["iteration_count"] + 1,
        }

def should_continue(state: HarnessState) -> Literal["tools", "compact", "__end__"]:
    scratchpad = state.get("scratchpad", [])

    # Use max_iterations from state (default to 25 if not present)
    max_iters = state.get("max_iterations", 25)
    if state["iteration_count"] > max_iters: return "__end__"

    if scratchpad and scratchpad[-1].tool_calls:
        # Include scratchpad in token count to detect long turns
        token_count = estimate_tokens(state["messages"] + scratchpad)
        # Increased message threshold to 50 to allow more turns before summarizing
        if token_count > 35000 or len(state["messages"]) > state.get("context_budget", 50):
            return "compact"
        return "tools"

    return "__end__"

async def compact_context(state: HarnessState):
    await emit_event(EventType.COMPACTION_START)
    model = get_model()
    to_prune = state["messages"][:-4]

    compaction_prompt = "Produce a highly technical State Memo (DECISIONS, STATUS, PENDING, CONTEXT)."
    memo_request = [SystemMessage(content=compaction_prompt), HumanMessage(content=f"History:\n{to_prune}")]
    resp = await model.ainvoke(memo_request)
    state_memo = resp.content

    logger = SessionLogger(state["session_id"])
    try: logger.create_long_term_memory(content=str(to_prune), summary=state_memo)
    except: pass

    # Invalidate system prompt cache since context_summary changed
    invalidate_system_prompt_cache(state["session_id"])

    await emit_event(EventType.COMPACTION_END, {"memo": state_memo})
    return {
        "messages": state["messages"][-4:],
        "context_summary": state_memo
    }

async def execute_tools(state: HarnessState):
    scratchpad = state.get("scratchpad", [])
    last_message = scratchpad[-1]
    tool_messages = []
    logger = SessionLogger(state["session_id"])
    ui = get_ui()
    yolo_mode = state.get("yolo", False)

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]; tool_args = tool_call["args"]
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
            if ui: approved = await ui.request_approval(tool_name, tool_args)
            else: approved = False
            if not approved:
                tool_messages.append(ToolMessage(tool_call_id=tool_call["id"], content="ERROR: Denied by user."))
                continue

        # EXECUTION
        await emit_event(EventType.TOOL_START, {"tool": tool_name, "args": tool_args})
        if desc:
            try: result = await desc.handler.ainvoke(tool_args)
            except Exception as e: result = f"Error: {str(e)}"
        else: result = f"Error: Tool {tool_name} not found."

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

    if not state.get("incognito", False): logger.log_messages(tool_messages)

    new_scratchpad = scratchpad + tool_messages
    return {"scratchpad": new_scratchpad}
