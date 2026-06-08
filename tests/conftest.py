"""Shared fixtures for all test suites."""

import os
import sys
import tempfile
import shutil
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage


# ── Path setup ────────────────────────────────────────────────────────────────
# Ensure project root is in path (pytest.ini sets pythonpath, but be safe)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ── Mock Model Fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def mock_model():
    """Return a mock LLM model that returns a simple AIMessage."""
    model = MagicMock()
    model.ainvoke = AsyncMock(return_value=AIMessage(content="Test response"))
    model.bind_tools.return_value = model
    return model


@pytest.fixture
def mock_model_with_tool_call():
    """Return a mock LLM model that returns a tool call response."""
    model = MagicMock()
    response = AIMessage(
        content="",
        tool_calls=[{
            "name": "read_file",
            "args": {"path": "test.txt"},
            "id": "call_1"
        }]
    )
    model.ainvoke = AsyncMock(return_value=response)
    model.bind_tools.return_value = model
    return model


@pytest.fixture
def mock_model_with_write_tool_call():
    """Return a mock LLM model that returns a write_file tool call."""
    model = MagicMock()
    response = AIMessage(
        content="",
        tool_calls=[{
            "name": "write_file",
            "args": {"path": "test.txt", "content": "Hello"},
            "id": "call_1"
        }]
    )
    model.ainvoke = AsyncMock(return_value=response)
    model.bind_tools.return_value = model
    return model


@pytest.fixture
def mock_model_with_delegate_tool_call():
    """Return a mock LLM model that returns a delegate_to_agent tool call."""
    model = MagicMock()
    response = AIMessage(
        content="",
        tool_calls=[{
            "name": "delegate_to_agent",
            "args": {"agent_id": "coder", "mission": "Write a function"},
            "id": "call_1"
        }]
    )
    model.ainvoke = AsyncMock(return_value=response)
    model.bind_tools.return_value = model
    return model


@pytest.fixture
def mock_model_empty_response():
    """Return a mock LLM model that returns an empty content response."""
    model = MagicMock()
    model.ainvoke = AsyncMock(return_value=AIMessage(content=""))
    model.bind_tools.return_value = model
    return model


@pytest.fixture
def mock_model_error():
    """Return a mock LLM model that raises an exception."""
    model = MagicMock()
    model.ainvoke = AsyncMock(side_effect=Exception("Model API error"))
    model.bind_tools.return_value = model
    return model


# ── State Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def clean_state():
    """Return a minimal HarnessState dict."""
    return {
        "messages": [],
        "context_budget": 50,
        "max_iterations": 10,
        "iteration_count": 0,
        "session_id": "test-session",
        "permissions": "read",
        "context_summary": "",
        "incognito": False,
        "yolo": False,
    }


@pytest.fixture
def state_with_messages():
    """Return a HarnessState with some messages."""
    return {
        "messages": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
            HumanMessage(content="What's the weather?"),
        ],
        "context_budget": 50,
        "max_iterations": 10,
        "iteration_count": 2,
        "session_id": "test-session-with-msgs",
        "permissions": "write",
        "context_summary": "",
        "incognito": False,
        "yolo": False,
    }


@pytest.fixture
def state_with_scratchpad():
    """Return a HarnessState with a scratchpad containing a tool call."""
    return {
        "messages": [HumanMessage(content="Read the file")],
        "scratchpad": [
            AIMessage(
                content="",
                tool_calls=[{
                    "name": "read_file",
                    "args": {"path": "test.txt"},
                    "id": "call_1"
                }]
            )
        ],
        "context_budget": 50,
        "max_iterations": 10,
        "iteration_count": 1,
        "session_id": "test-session-scratchpad",
        "permissions": "read",
        "context_summary": "",
        "incognito": False,
        "yolo": False,
    }


@pytest.fixture
def state_incognito():
    """Return a HarnessState in incognito mode."""
    return {
        "messages": [HumanMessage(content="Secret message")],
        "context_budget": 50,
        "max_iterations": 10,
        "iteration_count": 0,
        "session_id": "test-incognito",
        "permissions": "read",
        "context_summary": "",
        "incognito": True,
        "yolo": False,
    }


@pytest.fixture
def state_yolo():
    """Return a HarnessState in YOLO mode."""
    return {
        "messages": [HumanMessage(content="Do something dangerous")],
        "context_budget": 50,
        "max_iterations": 10,
        "iteration_count": 0,
        "session_id": "test-yolo",
        "permissions": "execute",
        "context_summary": "",
        "incognito": False,
        "yolo": True,
    }


# ── Temp Directory Fixtures ───────────────────────────────────────────────────

@pytest.fixture
def temp_dir():
    """Create a temporary directory and clean up after test."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def temp_project_dir(temp_dir):
    """Create a temporary project directory with basic structure."""
    # Create basic project files
    Path(temp_dir, "AGENTS.md").write_text("# Test Agent\nYou are a test agent.")
    Path(temp_dir, "README.md").write_text("# Test Project")
    Path(temp_dir, "main.py").write_text("print('hello')")
    Path(temp_dir, "src").mkdir()
    Path(temp_dir, "src", "app.py").write_text("# App code")
    Path(temp_dir, "src", "utils.py").write_text("# Utils code")
    Path(temp_dir, ".git").mkdir()
    Path(temp_dir, ".git", "config").write_text("[core]")
    Path(temp_dir, ".venv").mkdir()
    Path(temp_dir, ".venv", "lib").mkdir()
    Path(temp_dir, "__pycache__").mkdir()
    Path(temp_dir, "__pycache__", "module.cpython-313.pyc").write_text("")
    return temp_dir


# ── DB Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_db_path(temp_dir):
    """Return a path for a temporary database."""
    return os.path.join(temp_dir, "test_harness.db")


# ── Hook Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def hook_manager():
    """Return a fresh HookManager instance."""
    from core.hooks import HookManager
    return HookManager()


@pytest.fixture
def blocking_hook():
    """Return a pre-tool hook that blocks all tools."""
    async def block_all(tool_name, tool_args, context):
        from core.hooks import HookResult
        return HookResult(allowed=False)
    return block_all


@pytest.fixture
def allowing_hook():
    """Return a pre-tool hook that allows all tools."""
    async def allow_all(tool_name, tool_args, context):
        from core.hooks import HookResult
        return HookResult(allowed=True)
    return allow_all


@pytest.fixture
def modifying_hook():
    """Return a pre-tool hook that modifies arguments."""
    async def modify_args(tool_name, tool_args, context):
        from core.hooks import HookResult
        return HookResult(allowed=True, modified_args={"modified": True})
    return modify_args


@pytest.fixture
def audit_log_hook():
    """Return a post-tool hook that logs calls to a list."""
    calls = []
    async def audit_log(tool_name, tool_args, result, context):
        calls.append({"tool": tool_name, "args": tool_args, "result": result})
    audit_log.calls = calls
    return audit_log


# ── Context Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_context_cache():
    """Clear the context cache before each test."""
    from core.utils import _CONTEXT_CACHE
    _CONTEXT_CACHE["data"] = None
    _CONTEXT_CACHE["timestamp"] = 0
    yield
    _CONTEXT_CACHE["data"] = None
    _CONTEXT_CACHE["timestamp"] = 0


@pytest.fixture(autouse=True)
def clear_prompt_cache():
    """Clear the system prompt cache before each test."""
    from core.prompt_builder import _SYS_PROMPT_CACHE
    _SYS_PROMPT_CACHE.clear()
    yield
    _SYS_PROMPT_CACHE.clear()


@pytest.fixture(autouse=True)
def clear_ui_context():
    """Clear the UI context vars before each test."""
    from core.ui_interface import _UI_VAR, _SESSION_ID_VAR
    _UI_VAR.set(None)
    _SESSION_ID_VAR.set(None)
    yield
    _UI_VAR.set(None)
    _SESSION_ID_VAR.set(None)
