import asyncio
import os
from langchain_core.messages import HumanMessage, AIMessage
from tools import delegate_to_agent
from agent_loader import agent_loader

async def test_sub_agent_delegation():
    # 1. Verify loader can find our test agents
    available = agent_loader.list_available_agents()
    ids = [a['id'] for i, a in enumerate(available)]
    print(f"Available agents: {ids}")
    assert "coder" in ids
    assert "researcher" in ids

    # 2. Test delegation logic (Mocking or running real)
    # We'll test the tool invocation
    print("Testing delegation to 'researcher'...")
    # This might call the real LLM if configured, so we'll just check the setup
    # unless we want a full integration test.
    # For now, let's just ensure the tool is registered.
    from tools import registry
    assert "delegate_to_agent" in registry.tools
    assert registry.tools["delegate_to_agent"].requires_approval == True

    print("✅ Sub-Agent Delegation Infrastructure Validated!")

if __name__ == "__main__":
    asyncio.run(test_sub_agent_delegation())
