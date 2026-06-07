import pytest
from langchain_core.messages import HumanMessage, AIMessage
from core.harness import harness
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_hitl_interrupt():
    session_id = "test-hitl-session"
    config = {"configurable": {"thread_id": session_id}}

    # Mock get_model to force a tool call response
    mock_model = MagicMock()
    # Mock a response that triggers 'write_file'
    mock_response = AIMessage(
        content="",
        tool_calls=[{
            "name": "write_file",
            "args": {"path": "test.txt", "content": "Olá"},
            "id": "call_1"
        }]
    )
    mock_model.ainvoke = AsyncMock(return_value=mock_response)
    mock_model.bind_tools.return_value = mock_model

    with patch('core.model_caller.get_model', return_value=mock_model):
        # 1. Setup state
        state = {
            "messages": [HumanMessage(content="Escreva 'Olá' no arquivo test.txt")],
            "context_budget": 10,
            "max_iterations": 5,
            "iteration_count": 0,
            "session_id": session_id,
            "permissions": "write",
            "context_summary": "",
            "incognito": False,
            "yolo": False
        }

        # Invoke. LangGraph should interrupt because write_file requires approval
        # and we are NOT in YOLO mode.
        await harness.ainvoke(state, config=config)

        # Check if we are at an interrupt
        snapshot = harness.get_state(config)
        # In the actual graph, it should pause BEFORE executing tools
        assert "tools" in snapshot.next
