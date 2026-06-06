import asyncio
from persistence import SessionLogger
from langchain_core.messages import HumanMessage

async def verify_fts5_sanitization():
    logger = SessionLogger("test-fts5-dots")
    # 1. Log a message with a filename
    logger.log_messages([HumanMessage(content="Analyzing the AGENTS.md file.")])

    # 2. Search for the filename (this used to crash)
    print("Testing search for 'AGENTS.md'...")
    try:
        results = logger.search_messages("AGENTS.md")
        print(f"Results: {results}")
        assert len(results) > 0
        print("✅ FTS5 Sanitization Validated!")
    except Exception as e:
        print(f"❌ FTS5 Sanitization Failed: {str(e)}")
        raise e

if __name__ == "__main__":
    asyncio.run(verify_fts5_sanitization())
