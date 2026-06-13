"""Post-Mortem node - extracts lessons learned after a task is completed."""

from langchain_core.messages import SystemMessage, HumanMessage
from .state import HarnessState
from .model_config import get_model
from .ui_interface import EventType
from .model_caller import emit_event
from infra.persistence import SessionLogger


async def run_post_mortem(state: HarnessState) -> dict:
    """Analyze the session history to extract technical lessons (Golden Rules).

    Args:
        state: The current harness state.

    Returns:
        Empty dict (results are persisted to LTM).
    """
    if state["iteration_count"] < 5:
        # Don't run post-mortem for trivial sessions
        return {}

    await emit_event(EventType.THINKING_START, {"agent": "Evaluator"})
    model = get_model()

    pm_prompt = (
        "You are the Technical Evaluator K-Claw.\n"
        "The task is complete. Analyze the entire session history and extract 'GOLDEN RULES' for future use.\n\n"
        "Rules should focus on:\n"
        "- TECHNICAL LESSONS: Specific discoveries about the codebase (e.g., 'File X requires trigger Y').\n"
        "- PROCESS IMPROVEMENTS: What worked or didn't work in this specific task.\n\n"
        "FORMAT: Return a concise YAML list of rules."
    )

    messages = [
        SystemMessage(content=pm_prompt),
        HumanMessage(content=f"History Summary:\n{state.get('context_summary', 'N/A')}\n\nFinal Messages:\n{state['messages'][-5:]}")
    ]

    try:
        resp = await model.ainvoke(messages)
        lessons = resp.content.strip()

        if not state.get("incognito", False):
            logger = SessionLogger(state["session_id"])
            # We persist this as a 'Golden Rule' type memory
            logger.create_long_term_memory(
                content=lessons,
                summary="Technical Post-Mortem: Golden Rules extracted from session."
            )
            print(f"\n[Evaluator] Golden Rules extracted and persisted to Long-Term Memory.")
    except Exception as e:
        print(f"[Evaluator] Failed to run post-mortem: {e}")

    await emit_event(EventType.THINKING_END, {"agent": "Evaluator"})
    return {}
