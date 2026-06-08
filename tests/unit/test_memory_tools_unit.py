"""Unit tests for tools/memory_tools.py — memory search and retrieval."""

import pytest
from unittest.mock import patch, MagicMock
from tools import search_memory, fetch_memory_detail


class TestSearchMemory:
    """Test search_memory tool."""

    @pytest.mark.asyncio
    async def test_l1_search_returns_results(self):
        with patch("infra.persistence.SessionLogger") as mock_logger_cls:
            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger
            mock_logger.search_messages.return_value = [
                {"rowid": 1, "content": "Test message about servers", "session_id": "s1", "role": "human"}
            ]
            mock_logger.semantic_search.return_value = []

            result = search_memory.invoke({"query": "server", "layer": "L1"})
            assert "ID: 1" in result
            assert "Test message" in result

    @pytest.mark.asyncio
    async def test_l1_no_results(self):
        with patch("infra.persistence.SessionLogger") as mock_logger_cls:
            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger
            mock_logger.search_messages.return_value = []
            mock_logger.semantic_search.return_value = []

            result = search_memory.invoke({"query": "nonexistent", "layer": "L1"})
            assert "No results found" in result

    @pytest.mark.asyncio
    async def test_l2_requires_target_id(self):
        result = search_memory.invoke({"query": "test", "layer": "L2"})
        assert "Error" in result
        assert "target_id" in result

    @pytest.mark.asyncio
    async def test_l2_returns_detail(self):
        with patch("infra.persistence.SessionLogger") as mock_logger_cls:
            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger
            mock_logger.get_memory_detail.return_value = {
                "content": "Detailed memory content about servers"
            }

            result = search_memory.invoke({"query": "test", "layer": "L2", "target_id": 1})
            assert "L2 Summary" in result
            assert "Detailed memory content" in result

    @pytest.mark.asyncio
    async def test_l3_requires_target_id(self):
        result = search_memory.invoke({"query": "test", "layer": "L3"})
        assert "Error" in result
        assert "target_id" in result

    @pytest.mark.asyncio
    async def test_l3_returns_full_content(self):
        with patch("infra.persistence.SessionLogger") as mock_logger_cls:
            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger
            mock_logger.get_memory_detail.return_value = {
                "content": "Full memory content here"
            }

            result = search_memory.invoke({"query": "test", "layer": "L3", "target_id": 1})
            assert "L3 Full Content" in result
            assert "Full memory content" in result


class TestFetchMemoryDetail:
    """Test fetch_memory_detail tool."""

    @pytest.mark.asyncio
    async def test_returns_memory_detail(self):
        with patch("infra.persistence.SessionLogger") as mock_logger_cls:
            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger
            mock_logger.get_memory_detail.return_value = {
                "content": "Memory content here"
            }

            result = fetch_memory_detail.invoke({"memory_id": 1})
            assert "Memory content here" in result

    @pytest.mark.asyncio
    async def test_memory_not_found(self):
        with patch("infra.persistence.SessionLogger") as mock_logger_cls:
            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger
            mock_logger.get_memory_detail.return_value = None

            result = fetch_memory_detail.invoke({"memory_id": 999})
            assert "not found" in result
