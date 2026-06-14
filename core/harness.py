from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from .state import HarnessState
from .model_caller import call_model
from .planner import plan_task
from .reflection import reflect_on_action
from .post_mortem import run_post_mortem
from .dialog_control import should_continue
from .tool_executor import execute_tools
from .compaction import compact_context

# Initialize memory saver for persistence
checkpointer = MemorySaver()

async def handle_limit(state: HarnessState) -> dict:
    """Handle reaching the iteration limit."""
    scratchpad = state.get("scratchpad", [])
    last_intent = ""
    if scratchpad:
        last_msg = scratchpad[-1]
        if isinstance(last_msg, AIMessage):
            if last_msg.tool_calls:
                last_intent = f"Attempting tools: {[tc['name'] for tc in last_msg.tool_calls]}"
            if last_msg.content:
                last_intent += f" | {last_msg.content}"
    
    warning = (
        f"\n\n[SYSTEM STOP] Max iterations reached ({state.get('max_iterations', 50)}). "
        "The task was terminated for safety. Some steps might be missing.\n"
        f"Last known intent: {last_intent}"
    )
    return {
        "messages": [AIMessage(content=warning)],
        "scratchpad": None
    }

def should_plan(state: HarnessState) -> str:
    """Decide if we should go to planning or agent node."""
    if not state.get("plan"):
        return "planner"
    return "agent"

def create_harness():
    workflow = StateGraph(HarnessState)

    # Add Nodes
    workflow.add_node("planner", plan_task)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", execute_tools)
    workflow.add_node("compact", compact_context)
    workflow.add_node("reflection", reflect_on_action)
    workflow.add_node("post_mortem", run_post_mortem)
    workflow.add_node("limit_handler", handle_limit)

    # Set Entry Point with conditional routing
    workflow.add_conditional_edges(
        START,
        should_plan,
        {"planner": "planner", "agent": "agent"}
    )

    # Edge from planner to agent
    workflow.add_edge("planner", "agent")

    # Add Conditional Edges from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "compact": "compact",
            "reflection": "reflection",
            "planner": "planner",
            "limit_handler": "limit_handler",
            "__end__": "post_mortem"
        }
    )

    # Edge from limit_handler to post_mortem
    workflow.add_edge("limit_handler", "post_mortem")

    # Edge from post_mortem to actual end
    workflow.add_edge("post_mortem", END)

    # Edge from reflection back to agent
    workflow.add_edge("reflection", "agent")

    # Edge from compact back to agent
    workflow.add_edge("compact", "agent")

    # Edge from tools back to agent
    workflow.add_edge("tools", "agent")

    from tools import registry, set_harness_refs

    # Compile a single robust harness without low-level interrupts
    # HITL is now handled at the node level for better sub-agent support
    compiled_harness = workflow.compile(
        checkpointer=checkpointer
    )

    # Provide the reference to tools
    set_harness_refs(compiled_harness)

    return compiled_harness

harness = create_harness()
