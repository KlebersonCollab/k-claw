"""Model invocation - handles calling the LLM with tools and processing responses."""

import asyncio
from typing import Dict, Optional

from langchain_core.messages import AIMessage
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from tools import registry

from .model_config import get_model
from .prompt_builder import get_cached_system_prompt
from .state import HarnessState
from .ui_interface import EventType, get_ui, set_current_session_id
from .utils import redact_sensitive_info
from infra.persistence import SessionLogger


async def emit_event(event_type: EventType, data: dict = None) -> None:
    """Emit an event to the current UI.

    Args:
        event_type: The type of event to emit.
        data: Optional data to include with the event.
    """
    ui = get_ui()
    if ui:
        await ui.on_event(event_type, data or {})


async def call_model(state: HarnessState) -> dict:
    """Call the LLM model with the current state and return the response.

    Args:
        state: The current harness state.

    Returns:
        Updated state dict with messages and scratchpad.
    """
    set_current_session_id(state['session_id'])
    agent_name = "Orchestrator" if not state['session_id'].startswith("sub-") else f"Specialist {state['session_id'].split('-')[1]}"

    await emit_event(EventType.THINKING_START, {"agent": agent_name, "session_id": state['session_id']})

    model = get_model()
    sys_msg = get_cached_system_prompt(state)

    scratchpad = state.get("scratchpad", [])
    messages_for_llm = [sys_msg] + state["messages"] + scratchpad

    authorized_tools = registry.get_langchain_tools(state["permissions"])
    model_with_tools = model.bind_tools(authorized_tools)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ValueError, Exception)), # Retrying on general exceptions as well for robustness
        reraise=True
    )
    async def _invoke_with_retry():
        try:
            res = await model_with_tools.ainvoke(messages_for_llm)
            if not res.content and not res.tool_calls:
                # LLM returned empty response without tool calls - this is usually a glitch
                # or a misunderstanding of the prompt. We should treat it as an error to allow retry.
                raise ValueError(f"LLM returned an empty response for session {state['session_id']}")
            return res
        except ValueError as e:
            # specifically check for 502/503/504 style errors from provider
            err_msg = str(e)
            if "502" in err_msg or "503" in err_msg or "504" in err_msg or "Provider returned error" in err_msg or "empty response" in err_msg:
                raise e # retry
            raise e # reraise if not a transient error

    response = await _invoke_with_retry()

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
