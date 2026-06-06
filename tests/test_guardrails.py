import asyncio
from utils import cap_tool_output, estimate_tokens
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def test_guardrails():
    # 1. Test Capping
    huge_content = "A" * 5000
    capped = cap_tool_output(huge_content, max_chars=1000)
    print(f"Capped length: {len(capped)}")
    assert len(capped) < 1500
    assert "TRUNCATED" in capped

    # 2. Test Token Estimation
    msgs = [
        HumanMessage(content="Hello world"), # ~11 chars -> 2.75 tokens
        AIMessage(content="I am an AI assistant here to help."), # ~34 chars -> 8.5 tokens
    ]
    tokens = estimate_tokens(msgs)
    print(f"Estimated tokens: {tokens}")
    assert tokens > 5 and tokens < 15

    print("✅ Token Guardrail Logic Validated!")

if __name__ == "__main__":
    test_guardrails()
