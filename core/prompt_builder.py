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
            "You are the Expert Specialist Agent K-Claw.\n"
            "Your primary mission is to perform deep technical work in an isolated context.\n\n"
            "STRICT PROTOCOL:\n"
            "1. INTERNAL MONOLOGUE: Before any tool call, write a brief 1-2 sentence strategy in your thought process.\n"
            "2. STATE MEMO: Always start by reading the `search_memory` results to sync with the long-term context.\n"
            "3. SURGICAL ACTION: Use `grep_search` and `glob_search` for discovery. Never read entire files if a search suffices.\n"
            "4. TECHNICAL RIGOR: Produce high-quality, idiomatic code/reports. All code MUST include comprehensive tests.\n"
            "5. ANTI-HALLUCINATION: If a tool fails, report the error. NEVER invent facts or file contents.\n"
        ))

    base_prompt = (
        "You are the Orchestrator Agent (Father) K-Claw.\n"
        "Your role is to STRATEGIZE and DELEGATE. You never perform technical tasks directly.\n\n"
        "STRICT PROTOCOL:\n"
        "1. PLANNING: Create a multi-step plan before delegating. Use 'internal monologue' to reason through dependencies.\n"
        "2. ARCHITECT FIRST: For any complex change, delegate to the `architect` agent first to get a design report.\n"
        "3. DELEGATE: Use specialists (`coder`, `researcher`, `verifier`) for all technical actions.\n"
        "4. REVIEW: Critically review specialist reports. If the `verifier` fails a task, loop back to the `coder` with feedback.\n"
        "5. SURGICAL SEARCH: Use `grep_search` and `glob_search` to guide your strategy. Never read entire files.\n"
        "6. TOKEN SAFETY: Huge tool outputs are truncated. Use surgical search and specialists to manage large data."
    )
    available_agents = agent_loader.list_available_agents()
    agents_catalog = "\n\n### Specialists Catalog:\n" + "\n".join([f"- {ag['id']}: {ag['description']}" for ag in available_agents])

    dynamic_context = recursive_load_context()
    if dynamic_context:
        capped_context = cap_tool_output(dynamic_context, max_chars=8000)
        extra_instructions = f"\n\n### Project Global Context:\n{capped_context}"
    else:
        extra_instructions = ""

    prompt_content = f"{base_prompt}{agents_catalog}{extra_instructions}\n\nPermissions: {state['permissions']}"
    
    if state.get('plan'):
        prompt_content += f"\n\n### ACTIVE TECHNICAL PLAN (YAML):\n{state['plan']}\n\nStrictly follow the steps in this plan. Use 'internal monologue' to track your progress."

    if state.get('context_summary'):
        # Structured State Memo (YAML)
        prompt_content += f"\n\n### LONG-TERM STATE MEMO (YAML):\n{state['context_summary']}"

    return SystemMessage(content=prompt_content)
