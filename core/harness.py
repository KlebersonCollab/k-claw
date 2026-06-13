from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
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
            "__end__": "post_mortem"
        }
    )

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
