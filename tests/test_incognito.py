import pytest
from infra.persistence import SessionLogger
from core.model_caller import call_model
from langchain_core.messages import HumanMessage, AIMessage
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_incognito_mode():
    session_id = "incognito-test-session"

    # AsyncMock is required for ainvoke
    mock_model = MagicMock()
    mock_response = AIMessage(content="Hello")
    mock_model.ainvoke = AsyncMock(return_value=mock_response)
    mock_model.bind_tools.return_value = mock_model

    with patch('core.model_caller.get_model', return_value=mock_model):
        # 1. Normal mode
        state_normal = {
            "messages": [HumanMessage(content="This should be logged")],
            "iteration_count": 0, "session_id": session_id, "permissions": "read",
            "context_summary": "", "incognito": False, "max_iterations": 1
        }
        await call_model(state_normal)

        logger = SessionLogger(session_id)
        history = logger.get_message_history()
        assert len(history) > 0
        len_before = len(history)

        # 2. Incognito mode
        state_incognito = {
            "messages": [HumanMessage(content="This should NOT be logged")],
            "iteration_count": 0, "session_id": session_id, "permissions": "read",
            "context_summary": "", "incognito": True, "max_iterations": 1
        }
        await call_model(state_incognito)

        history_after = logger.get_message_history()
        # It should remain the same as before the second call
        assert len(history_after) == len_before
