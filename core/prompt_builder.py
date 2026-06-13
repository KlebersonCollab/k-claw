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
    
    # Shared elements: Blackboard and State Memo
    shared_context = ""
    if state.get('context_summary'):
        shared_context += f"\n\n### LONG-TERM STATE MEMO (YAML):\n{state['context_summary']}"

    if state.get('blackboard'):
        bb_content = "\n".join([f"- {k}: {v}" for k, v in state['blackboard'].items()])
        shared_context += f"\n\n### GLOBAL BLACKBOARD (Shared Discoveries):\n{bb_content}"

    if is_sub_agent:
        return SystemMessage(content=(
            "You are the Expert Specialist Agent K-Claw.\n"
            "Your primary mission is to perform deep technical work in an isolated context.\n\n"
            "STRICT PROTOCOL:\n"
            "1. INTERNAL MONOLOGUE: Before any tool call, write a brief 1-2 sentence strategy in your thought process.\n"
            "2. BLACKBOARD AWARENESS: Always check the `GLOBAL BLACKBOARD` below. These are facts already discovered by other agents. Do NOT rediscovover them.\n"
            "3. SURGICAL ACTION: Use `grep_search` and `glob_search` for discovery. Never read entire files if a search suffices.\n"
            "4. TECHNICAL RIGOR: Produce high-quality, idiomatic code/reports. All code MUST include comprehensive tests.\n"
            "5. ANTI-HALLUCINATION: If a tool fails, report the error. NEVER invent facts or file contents.\n"
            f"{shared_context}"
        ))

    base_prompt = (
        "You are the Orchestrator Agent (Father) K-Claw.\n"
        "Your role is to STRATEGIZE and DELEGATE. You never perform technical tasks directly.\n\n"
        "REASONING 2.0 PROTOCOL:\n"
        "1. PLANNING & PIVOTING: Follow your Technical Plan. If findings contradict the plan, say 'Preciso ajustar o plano' to trigger a PIVOT.\n"
        "2. BLACKBOARD UPDATE: When you receive new technical facts from specialists, synthesize them in your next response to update the Global Blackboard.\n"
        "3. EPISTEMOLOGICAL CHECK: Before any technical action (write/execute), you MUST list your ASSUMPTIONS. Verify premises before acting.\n"
        "4. ACTION OVER TALK: When you decide to delegate, call `delegate_to_agent` IMMEDIATELY. Do not explain unless necessary.\n"
        "5. ARCHITECT FIRST: Delegate to `architect` for design reports on complex changes.\n"
        "6. REVIEW & LOOP: Critically review specialist reports. If `verifier` fails, loop back to `coder` with feedback.\n"
        "7. SURGICAL SEARCH: Use `grep_search` and `glob_search` to guide your strategy.\n"
        "8. NO EMPTY RESPONSES: Always provide a response or call a tool."
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
        prompt_content += f"\n\n### ACTIVE TECHNICAL PLAN (YAML):\n{state['plan']}"

    prompt_content += shared_context

    return SystemMessage(content=prompt_content)
