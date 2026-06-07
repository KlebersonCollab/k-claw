import pytest
from tools import registry
from infra.agent_loader import agent_loader

def test_sub_agent_delegation_infrastructure():
    # 1. Verify loader can find our test agents
    available = agent_loader.list_available_agents()
    ids = [a['id'] for a in available]
    assert "coder" in ids
    assert "researcher" in ids

    # 2. Verify tool registration
    assert "delegate_to_agent" in registry.tools
    # In the new registry, permissions and approval are properties of the descriptor
    assert registry.tools["delegate_to_agent"].permissions_required == "read"
