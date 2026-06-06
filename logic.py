import os
import asyncio
from datetime import datetime
from typing import Literal, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.markup import escape
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from state import HarnessState
from tools import registry, classify_shell_command, risk_level_value
from persistence import SessionLogger
from dotenv import load_dotenv
from agent_loader import agent_loader
from utils import get_model, redact_sensitive_info, recursive_load_context, cap_tool_output, estimate_tokens
from ui_interface import get_ui, EventType
from hooks import hook_manager

load_dotenv()
console = Console()

async def emit_event(event_type: EventType, data: Dict[str, Any] = None):
    ui = get_ui()
    if ui:
        await ui.on_event(event_type, data or {})

def assemble_system_prompt(state: HarnessState) -> SystemMessage:
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
        "1. DELEGATE ALL technical tasks to specialists.\n"
        "2. Review the specialist's REPORT and relay the conclusion.\n"
        "3. TOKEN SAFETY: Huge tool outputs are truncated. Use specialists to analyze large data."
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
    sys_msg = assemble_system_prompt(state)

    # Combine main history and current scratchpad for the LLM
    scratchpad = state.get("scratchpad", [])
    messages_for_llm = [sys_msg] + state["messages"] + scratchpad

    authorized_tools = registry.get_langchain_tools(state["permissions"])
    model_with_tools = model.bind_tools(authorized_tools)
    response = await model_with_tools.ainvoke(messages_for_llm)

    await emit_event(EventType.THINKING_END, {"agent": agent_name})

    clean_content = redact_sensitive_info(response.content) if response.content else ""

    # If the response has tool calls, it's an intermediate step -> goes to scratchpad
    if response.tool_calls:
        # We append the AI's tool request to the scratchpad
        new_scratchpad = scratchpad + [response]
        return {
            "scratchpad": new_scratchpad,
            "iteration_count": state["iteration_count"] + 1,
        }
    else:
        # If no tools are called, it's the final answer -> goes to messages, and we clear the scratchpad
        if not state.get("incognito", False):
            logger = SessionLogger(state["session_id"])
            logger.log_event("model_call", {"response": redact_sensitive_info(str(response))})
            log_response = response.copy()
            log_response.content = clean_content
            logger.log_messages([log_response])

        return {
            "messages": [response],
            "scratchpad": None, # Clear scratchpad
            "iteration_count": state["iteration_count"] + 1,
        }

def should_continue(state: HarnessState) -> Literal["tools", "compact", "__end__"]:
    # The condition is now based on the scratchpad, as tools are only in the scratchpad
    scratchpad = state.get("scratchpad", [])

    if state["iteration_count"] > 25: return "__end__"

    if scratchpad and scratchpad[-1].tool_calls:
        # PROACTIVE COMPACTION: Check token weight instead of just message count
        token_count = estimate_tokens(state["messages"])
        # If context > 15k tokens (~60k chars), force compaction before next tool
        if token_count > 15000 or len(state["messages"]) > state["context_budget"]:
            return "compact"
        return "tools"

    return "__end__"

async def compact_context(state: HarnessState):
    await emit_event(EventType.COMPACTION_START)
    model = get_model()
    # Keep only the last 4 messages to really prune the context
    to_prune = state["messages"][:-4]

    compaction_prompt = "Produce a highly technical State Memo (DECISIONS, STATUS, PENDING, CONTEXT)."
    memo_request = [SystemMessage(content=compaction_prompt), HumanMessage(content=f"History:\n{to_prune}")]
    resp = await model.ainvoke(memo_request)
    state_memo = resp.content

    logger = SessionLogger(state["session_id"])
    try: logger.create_long_term_memory(content=str(to_prune), summary=state_memo)
    except: pass

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

        # HITL Verification
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

        # Execution
        await emit_event(EventType.TOOL_START, {"tool": tool_name, "args": tool_args})
        if desc:
            try: result = await desc.handler.ainvoke(tool_args)
            except Exception as e: result = f"Error: {str(e)}"
        else: result = f"Error: Tool {tool_name} not found."

        # TOOL OUTPUT CAPPING (The Token Guardrail)
        capped_result = cap_tool_output(str(result))
        clean_result = redact_sensitive_info(capped_result)

        if not state.get("incognito", False):
            logger.log_event("tool_execution", {"tool": tool_name, "result": clean_result})

        await emit_event(EventType.TOOL_END, {"tool": tool_name, "result": clean_result})
        tool_messages.append(ToolMessage(tool_call_id=tool_call["id"], content=clean_result))

    if not state.get("incognito", False): logger.log_messages(tool_messages)

    # Tool results go to the scratchpad, not the main messages list
    new_scratchpad = scratchpad + tool_messages
    return {"scratchpad": new_scratchpad}
