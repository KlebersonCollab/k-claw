from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import HarnessState
from logic import call_model, should_continue, execute_tools, compact_context

# Initialize memory saver for persistence
checkpointer = MemorySaver()

def create_harness():
    workflow = StateGraph(HarnessState)

    # Add Nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", execute_tools)
    workflow.add_node("compact", compact_context)

    # Set Entry Point
    workflow.add_edge(START, "agent")

    # Add Conditional Edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )

    # Edge from compact back to tools
    workflow.add_edge("compact", "tools")

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
