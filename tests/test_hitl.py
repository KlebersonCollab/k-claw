import pytest
from langchain_core.messages import HumanMessage, AIMessage
from core.harness import harness
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_hitl_approval_called():
    session_id = "test-hitl-session"
    config = {"configurable": {"thread_id": session_id}}

    # 1. Mock UI and Model
    mock_ui = MagicMock()
    mock_ui.request_approval = AsyncMock(return_value=True)
    mock_ui.on_event = AsyncMock() # Must be AsyncMock

    mock_model = MagicMock()
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

    # 2. Patch components
    from core.ui_interface import set_ui
    set_ui(mock_ui)

    with patch('core.model_caller.get_model', return_value=mock_model):
        with patch('core.tool_executor.SessionLogger'):
            # 3. Setup state
            state = {
                "messages": [HumanMessage(content="Escreva 'Olá' no arquivo test.txt")],
                "context_budget": 10,
                "max_iterations": 5,
                "iteration_count": 0,
                "session_id": session_id,
                "permissions": "write",
                "context_summary": "",
                "incognito": True,
                "yolo": False
            }

            # 4. Invoke
            await harness.ainvoke(state, config=config)

            # 5. Verify request_approval was called
            assert mock_ui.request_approval.called
            args = mock_ui.request_approval.call_args[0]
            assert args[0] == "write_file"
            assert args[1]["path"] == "test.txt"
