import os
import asyncio
from datetime import datetime
from typing import Literal
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.markup import escape
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from state import HarnessState
from tools import registry
from persistence import SessionLogger
from dotenv import load_dotenv
from agent_loader import agent_loader
from utils import get_model, redact_sensitive_info, recursive_load_context

load_dotenv()
console = Console()

def assemble_system_prompt(state: HarnessState) -> SystemMessage:
    is_sub_agent = state['session_id'].startswith("sub-")

    # 1. SPECIALIST PROMPT (Ultra-Light)
    if is_sub_agent:
        return SystemMessage(content=(
            "You are a Specialist Sub-Agent. Focus strictly on your technical mission.\n"
            f"Permissions: {state['permissions']}\n"
            "ANTI-HALLUCINATION: If a tool fails, report the error. NEVER guess contents."
        ))

    # 2. ORCHESTRATOR PROMPT (Pure Orchestration)
    base_prompt = (
        "You are the Orchestrator Agent (Father).\n"
        "STRICT PROTOCOL:\n"
        "1. DELEGATE ALL technical tasks (reading/writing files, shell commands, research) to the appropriate specialist.\n"
        "2. You are responsible for identifying WHICH specialist is needed and providing a detailed MISSION briefing.\n"
        "3. Review the specialist's REPORT and relay the conclusion to the user.\n"
        "4. ANTI-HALLUCINATION: Never invent file contents or tool results. If delegation fails, report the error."
    )
    available_agents = agent_loader.list_available_agents()
    agents_catalog = "\n\n### Specialists:\n" + "\n".join([f"- {ag['id']}: {ag['description']}" for ag in available_agents])

    dynamic_context = recursive_load_context()
    extra_instructions = f"\n\n### Context:\n{dynamic_context}" if dynamic_context else ""

    prompt_content = f"{base_prompt}{agents_catalog}{extra_instructions}\n\nPermissions: {state['permissions']}"
    if state.get('context_summary'):
        prompt_content += f"\n\n### State Memo:\n{state['context_summary']}"

    return SystemMessage(content=prompt_content)

async def call_model(state: HarnessState):
    agent_name = "Orchestrator" if not state['session_id'].startswith("sub-") else f"Specialist {state['session_id'].split('-')[1]}"
    with console.status(f"[bold cyan]{agent_name} is thinking...[/bold cyan]"):
        model = get_model()
        sys_msg = assemble_system_prompt(state)
        messages = [sys_msg] + state["messages"]
        authorized_tools = registry.get_langchain_tools(state["permissions"])
        model_with_tools = model.bind_tools(authorized_tools)
        response = await model_with_tools.ainvoke(messages)

    clean_content = redact_sensitive_info(response.content) if response.content else ""
    if not state.get("incognito", False):
        logger = SessionLogger(state["session_id"])
        log_response = response.copy()
        log_response.content = clean_content
        logger.log_messages([log_response])
    return {"messages": [response], "iteration_count": state["iteration_count"] + 1}

def should_continue(state: HarnessState) -> Literal["tools", "compact", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    if state["iteration_count"] > 25: return "__end__"
    if last_message.tool_calls:
        if len(messages) > state["context_budget"]: return "compact"
        return "tools"
    return "__end__"

async def compact_context(state: HarnessState):
    with console.status("[bold yellow]Compacting...[/bold yellow]"):
        model = get_model()
        to_prune = state["messages"][:-5]
        memo_request = [SystemMessage(content="Produce a technical State Memo."), HumanMessage(content=f"History:\n{to_prune}")]
        resp = await model.ainvoke(memo_request)
        state_memo = resp.content
        logger = SessionLogger(state["session_id"])
        try: logger.create_long_term_memory(content=str(to_prune), summary=state_memo)
        except: pass
        return {"messages": state["messages"][-5:], "context_summary": state_memo}

async def execute_tools(state: HarnessState):
    last_message = state["messages"][-1]
    tool_messages = []
    logger = SessionLogger(state["session_id"])
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]; tool_args = tool_call["args"]
        desc = registry.tools.get(tool_name)
        if desc and desc.requires_approval:
            console.print("\n")
            console.print(Panel(f"[bold red]⚠️ Verification Needed[/bold red]\n[yellow]Tool:[/yellow] {tool_name}\n[yellow]Args:[/yellow] {escape(str(tool_args))}", title="Action Pending", border_style="red"))
            approved = await asyncio.to_thread(Confirm.ask, f"Allow {tool_name}?")
            if not approved:
                tool_messages.append(ToolMessage(tool_call_id=tool_call["id"], content="ERROR: Execution denied by user."))
                continue
        if tool_name != "delegate_to_agent":
            console.print(f"[dim green]Executing {tool_name}...[/dim green]")
        if desc:
            try: result = await desc.handler.ainvoke(tool_args)
            except Exception as e: result = f"Error: {str(e)}"
        else: result = f"Error: Tool {tool_name} not found."
        clean_result = redact_sensitive_info(str(result))
        if not state.get("incognito", False):
            logger.log_event("tool_execution", {"tool": tool_name, "result": clean_result})
        tool_messages.append(ToolMessage(tool_call_id=tool_call["id"], content=clean_result))
    if not state.get("incognito", False): logger.log_messages(tool_messages)
    return {"messages": tool_messages}
