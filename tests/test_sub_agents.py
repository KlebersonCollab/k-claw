import pytest
from tools import registry
from infra.agent_loader import agent_loader


def test_sub_agent_delegation_infrastructure():
    # 1. Verify loader can find our test agents
    available = agent_loader.list_available_agents()
    ids = [a['id'] for a in available]
    assert "coder" in ids
    assert "researcher" in ids
    assert "verifier" in ids

    # 2. Verify tool registration
    assert "delegate_to_agent" in registry.tools
    # In the new registry, permissions and approval are properties of the descriptor
    assert registry.tools["delegate_to_agent"].permissions_required == "read"


def test_verifier_agent_configuration():
    """Verify that the verifier agent is configured correctly."""
    config = agent_loader.load_agent("verifier")

    # Name and description
    assert config["name"] == "Verifier"
    assert "verificação" in config["description"].lower() or "verification" in config["description"].lower()

    # Permissions: verifier should be read-only
    assert config["permissions"] == "read"

    # Max iterations
    assert config["max_iterations"] == 10

    # Skills
    assert "python-patterns" in config["skills"]

    # Tools: verifier should have read and execute tools but NOT write tools
    allowed_tools = config["tools"]
    assert "list_directory" in allowed_tools
    assert "read_file" in allowed_tools
    assert "run_shell" in allowed_tools
    assert "grep_search" in allowed_tools
    assert "glob_search" in allowed_tools
    assert "search_memory" in allowed_tools
    assert "fetch_memory_detail" in allowed_tools

    # Critical: verifier must NOT have write permissions or write tools
    assert "write_file" not in allowed_tools
    assert "replace_string" not in allowed_tools
    assert "forget_session" not in allowed_tools


def test_verifier_prompt_contains_protocol():
    """Verify that the verifier prompt follows the verification protocol."""
    config = agent_loader.load_agent("verifier")
    instructions = config["instructions"]

    # Must contain verification protocol elements
    assert "VERIFICATION PROTOCOL" in instructions or "Verification Protocol" in instructions
    assert "STATUS" in instructions
    assert "PASS" in instructions or "pass" in instructions
    assert "FAIL" in instructions or "fail" in instructions
    assert "CHECKS" in instructions or "checks" in instructions
    assert "ISSUES" in instructions or "issues" in instructions
    assert "RECOMMENDATIONS" in instructions or "recommendations" in instructions
    assert "ANTI-HALLUCINATION" in instructions
    assert "{{mission}}" in instructions
