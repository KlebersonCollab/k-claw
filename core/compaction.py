"""Context compaction - summarizes conversation history to reduce token usage."""

from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from .state import HarnessState
from .model_config import get_model
from infra.persistence import SessionLogger
from .ui_interface import EventType
from .prompt_builder import invalidate_system_prompt_cache
from .model_caller import emit_event


async def compact_context(state: HarnessState) -> dict:
    """Compact the conversation context by summarizing older messages.

    Args:
        state: The current harness state.

    Returns:
        Updated state with RemoveMessages to prune history and new context summary.
    """
    messages = state.get("messages", [])
    to_keep_count = 10

    if len(messages) <= to_keep_count:
        return {}

    await emit_event(EventType.COMPACTION_START)
    model = get_model()

    # Prune everything except the last 10 messages
    to_prune = messages[:-to_keep_count]

    compaction_prompt = (
        "Produce a highly technical, structured STATE MEMO in YAML format to preserve long-term context.\n"
        "FIELDS:\n"
        "- PROJECT_MAP: Key files/modules discovered and their purpose.\n"
        "- ACTIVE_GOALS: Current objectives and their completion status.\n"
        "- DECISION_LOG: Key architectural or technical choices made and why.\n"
        "- KNOWLEDGE_GAPS: Information or files still needed to complete the mission.\n"
        "- TENTATIVES: List of failed attempts or commands to avoid repeating.\n\n"
        "Return ONLY the YAML block."
    )
    memo_request = [SystemMessage(content=compaction_prompt), HumanMessage(content=f"History to summarize:\n{to_prune}")]
    resp = await model.ainvoke(memo_request)
    state_memo = resp.content.strip()
    if "```yaml" in state_memo:
        state_memo = state_memo.split("```yaml")[1].split("```")[0].strip()
    elif "```" in state_memo:
        state_memo = state_memo.split("```")[1].split("```")[0].strip()

    logger = SessionLogger(state["session_id"])
    try:
        logger.create_long_term_memory(content=str(to_prune), summary=state_memo)
    except Exception:
        pass

    # Invalidate system prompt cache since context_summary changed
    invalidate_system_prompt_cache(state["session_id"])

    # Create RemoveMessage objects for all pruned messages
    # Note: messages from state should have IDs assigned by LangGraph
    removals = [RemoveMessage(id=m.id) for m in to_prune if getattr(m, 'id', None)]

    await emit_event(EventType.COMPACTION_END, {"memo": state_memo})
    return {
        "messages": removals,
        "context_summary": state_memo
    }
