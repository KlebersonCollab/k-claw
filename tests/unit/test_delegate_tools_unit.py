import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from tools.delegate_tools import delegate_to_agent
from langchain_core.messages import AIMessage

@pytest.mark.asyncio
async def test_delegate_to_agent_success():
    # Mock harness reference and agent loader
    mock_harness = MagicMock()
    mock_harness.ainvoke = AsyncMock(return_value={
        "messages": [AIMessage(content="Specialist Report")]
    })

    mock_config = {
        "instructions": "You are a specialist. Mission: {{mission}}",
        "permissions": "read",
        "skills": [],
        "tools": [],
        "max_iterations": 5
    }

    with patch("tools.delegate_tools._HARNESS_REF", mock_harness):
        with patch("infra.agent_loader.agent_loader.load_agent", return_value=mock_config):
            with patch("core.ui_interface.get_current_session_id", return_value="parent-session"):
                result = await delegate_to_agent.ainvoke({
                    "agent_id": "coder",
                    "mission": "Fix bug"
                })
                assert "TECHNICAL REPORT FROM SPECIALIST" in result
                assert "Specialist Report" in result

@pytest.mark.asyncio
async def test_delegate_to_agent_no_harness():
    with patch("tools.delegate_tools._HARNESS_REF", None):
        result = await delegate_to_agent.ainvoke({
            "agent_id": "coder",
            "mission": "test"
        })
        assert "Error: Harness not initialized" in result

@pytest.mark.asyncio
async def test_delegate_to_agent_exception():
    with patch("tools.delegate_tools._HARNESS_REF", MagicMock()):
        with patch("infra.agent_loader.agent_loader.load_agent", side_effect=Exception("Load error")):
            result = await delegate_to_agent.ainvoke({
                "agent_id": "bad-agent",
                "mission": "test"
            })
            assert "Error delegating to sub-agent" in result
            assert "Load error" in result
