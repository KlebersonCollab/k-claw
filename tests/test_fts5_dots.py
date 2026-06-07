import pytest
from infra.persistence import SessionLogger
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_fts5_sanitization():
    logger = SessionLogger("test-fts5-dots")
    # 1. Log a message with a filename
    logger.log_messages([HumanMessage(content="Analyzing the AGENTS.md file.")])

    # 2. Search for the filename (this used to crash with dots if not quoted)
    results = logger.search_messages("AGENTS.md")
    assert len(results) > 0
    assert "AGENTS.md" in results[0]["content"]

@pytest.mark.asyncio
async def test_fts5_injection_safety():
    logger = SessionLogger("test-fts5-injection")
    logger.log_messages([HumanMessage(content="Normal message")])

    # 3. Test for potential injection/logic escape
    results = logger.search_messages('Normal" OR "1"="1')
    assert len(results) == 0
