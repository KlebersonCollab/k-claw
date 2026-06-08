"""Unit tests for core/prompt_builder.py — system prompt assembly and caching."""

import os
import pytest
from unittest.mock import patch
from langchain_core.messages import SystemMessage
from core.prompt_builder import (
    assemble_system_prompt,
    get_cached_system_prompt,
    invalidate_system_prompt_cache,
    _SYS_PROMPT_CACHE,
    _build_cache_key,
)


class TestBuildCacheKey:
    """Test cache key building."""

    def test_same_state_same_key(self, clean_state):
        key1 = _build_cache_key(clean_state)
        key2 = _build_cache_key(clean_state)
        assert key1 == key2

    def test_different_permissions_different_key(self, clean_state):
        key1 = _build_cache_key(clean_state)
        state2 = {**clean_state, "permissions": "write"}
        key2 = _build_cache_key(state2)
        assert key1 != key2

    def test_different_session_different_key(self, clean_state):
        key1 = _build_cache_key(clean_state)
        state2 = {**clean_state, "session_id": "other-session"}
        key2 = _build_cache_key(state2)
        assert key1 != key2


class TestAssembleSystemPrompt:
    """Test system prompt assembly."""

    def test_returns_system_message(self, clean_state):
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            result = assemble_system_prompt(clean_state)
        assert isinstance(result, SystemMessage)

    def test_contains_agent_instructions(self, clean_state):
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            result = assemble_system_prompt(clean_state)
        assert "Orchestrator" in result.content

    def test_sub_agent_session_detection(self):
        state = {
            "messages": [],
            "permissions": "read",
            "context_summary": "",
            "session_id": "sub-test-session",
        }
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            result = assemble_system_prompt(state)
        assert "Specialist Sub-Agent" in result.content

    def test_context_summary_in_prompt(self):
        state = {
            "messages": [],
            "permissions": "read",
            "context_summary": "Previous context summary here",
            "session_id": "test-session",
        }
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            result = assemble_system_prompt(state)
        assert "Previous context summary here" in result.content


class TestGetCachedSystemPrompt:
    """Test system prompt caching."""

    def test_caches_prompt(self, clean_state):
        _SYS_PROMPT_CACHE.clear()
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            result1 = get_cached_system_prompt(clean_state)
        assert len(_SYS_PROMPT_CACHE) == 1

    def test_returns_cached_on_second_call(self, clean_state):
        _SYS_PROMPT_CACHE.clear()
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            result1 = get_cached_system_prompt(clean_state)
            result2 = get_cached_system_prompt(clean_state)
        assert result1 is result2

    def test_rebuild_on_permission_change(self, clean_state):
        _SYS_PROMPT_CACHE.clear()
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            get_cached_system_prompt(clean_state)
            state2 = {**clean_state, "permissions": "write"}
            get_cached_system_prompt(state2)
        assert len(_SYS_PROMPT_CACHE) == 2


class TestInvalidateSystemPromptCache:
    """Test cache invalidation."""

    def test_invalidates_session(self, clean_state):
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            get_cached_system_prompt(clean_state)
        invalidate_system_prompt_cache(clean_state["session_id"])
        # All keys starting with session_id should be gone
        remaining = [k for k in _SYS_PROMPT_CACHE if k.startswith(f"{clean_state['session_id']}:")]
        assert len(remaining) == 0

    def test_does_not_affect_other_sessions(self):
        state1 = {"session_id": "session-1", "permissions": "read", "context_summary": ""}
        state2 = {"session_id": "session-2", "permissions": "read", "context_summary": ""}
        _SYS_PROMPT_CACHE.clear()
        with patch("core.prompt_builder.recursive_load_context", return_value=""):
            get_cached_system_prompt(state1)
            get_cached_system_prompt(state2)
        invalidate_system_prompt_cache("session-1")
        remaining = [k for k in _SYS_PROMPT_CACHE if k.startswith("session-2:")]
        assert len(remaining) == 1
