"""System prompt assembly and caching - builds and caches prompts for orchestrator and sub-agents."""

from typing import Dict
from langchain_core.messages import SystemMessage
from .state import HarnessState
from infra.agent_loader import agent_loader
from .utils import cap_tool_output, recursive_load_context


# ── System Prompt Cache ──────────────────────────────────────────────────────

# Cache structure: session_id -> (permissions, context_summary, SystemMessage)
_SYS_PROMPT_CACHE: Dict[str, tuple] = {}


def _build_cache_key(state: HarnessState) -> str:
    """Build a cache key from session_id + fields that affect the prompt."""
    return f"{state['session_id']}:{state['permissions']}:{hash(state.get('context_summary', ''))}"


def get_cached_system_prompt(state: HarnessState) -> SystemMessage:
    """Return cached system prompt or build and cache it.

    The prompt is rebuilt only when session_id, permissions, or context_summary change.
    """
    cache_key = _build_cache_key(state)
    if cache_key in _SYS_PROMPT_CACHE:
        return _SYS_PROMPT_CACHE[cache_key][2]

    sys_msg = assemble_system_prompt(state)
    _SYS_PROMPT_CACHE[cache_key] = (state['permissions'], state.get('context_summary', ''), sys_msg)
    return sys_msg


def invalidate_system_prompt_cache(session_id: str) -> None:
    """Invalidate all cached prompts for a given session."""
    keys_to_remove = [k for k in _SYS_PROMPT_CACHE if k.startswith(f"{session_id}:")]
    for k in keys_to_remove:
        del _SYS_PROMPT_CACHE[k]


# ── System Prompt Assembly ───────────────────────────────────────────────────

def assemble_system_prompt(state: HarnessState) -> SystemMessage:
    """Assemble the system prompt based on the current state.

    Args:
        state: The current harness state.

    Returns:
        A SystemMessage with the assembled prompt.
    """
    is_sub_agent = state['session_id'].startswith("sub-")

    if is_sub_agent:
        return SystemMessage(content=(
            "You are a Specialist Sub-Agent K-Claw. Focus strictly on your technical mission.\n"
            f"Permissions: {state['permissions']}\n"
            "ANTI-HALLUCINATION: If a tool fails, report the error. NEVER guess contents.\n"
            "TOKEN EFFICIENCY: Your output will be truncated if too large. Be concise."
        ))

    base_prompt = (
        "You are the Orchestrator Agent (Father) K-Claw.\n"
        "STRICT PROTOCOL:\n"
        "1. SURGICAL SEARCH: Use `grep_search` and `glob_search` to find relevant code or information. NEVER read entire files if you can search for patterns.\n"
        "2. DELEGATE technical tasks (reading/writing files, shell commands, research) to the appropriate specialist.\n"
        "3. You are responsible for identifying WHICH specialist is needed and providing a detailed MISSION briefing.\n"
        "4. Review the specialist's REPORT and relay the conclusion to the user.\n"
        "5. ANTI-HALLUCINATION: Never invent file contents or tool results. If delegation fails, report the error.\n"
        "6. TOKEN SAFETY: Huge tool outputs are truncated. Use surgical search and specialists to manage large data."
    )
    available_agents = agent_loader.list_available_agents()
    agents_catalog = "\n\n### Specialists:\n" + "\n".join([f"- {ag['id']}: {ag['description']}" for ag in available_agents])

    dynamic_context = recursive_load_context()
    if dynamic_context:
        capped_context = cap_tool_output(dynamic_context, max_chars=8000)
        extra_instructions = f"\n\n### Project Context:\n{capped_context}"
    else:
        extra_instructions = ""

    prompt_content = f"{base_prompt}{agents_catalog}{extra_instructions}\n\nPermissions: {state['permissions']}"
    if state.get('context_summary'):
        capped_memo = cap_tool_output(state['context_summary'], max_chars=2000)
        prompt_content += f"\n\n### State Memo:\n{capped_memo}"

    return SystemMessage(content=prompt_content)
