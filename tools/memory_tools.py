"""Ferramentas de memória de contexto (decoradas com @tool do LangChain)."""

from __future__ import annotations

from typing import Optional

from langchain_core.tools import tool

from core.utils import cap_tool_output


def escape_rich(text):
    return text.replace("[", "[[").replace("]", "]]")


@tool
def search_memory(query: str, layer: str = "L1", target_id: Optional[int] = None) -> str:
    """Layered search in past conversation history.

    L1 (cheap):  IDs + short snippets only
    L2 (medium): Summary / first 500 chars for a target_id
    L3 (full):   Complete content for a target_id
    """
    from infra.persistence import SessionLogger

    logger = SessionLogger("search_service")

    try:
        if layer == "L1":
            fts_results = logger.search_messages(query, limit=3)
            semantic_results = logger.semantic_search(query, limit=3)
            output = ["### L1 Memory Index (cheap lookup):"]
            seen_ids: set = set()
            for r in fts_results:
                snippet = str(r["content"])[:60].replace("\n", " ")
                output.append(f"- ID: {r['rowid']} | KW | {escape_rich(snippet)}...")
                seen_ids.add(r["rowid"])
            for r in semantic_results:
                if r["rowid"] not in seen_ids:
                    snippet = str(r.get("summary") or "")[:60]
                    output.append(f"- ID: {r['rowid']} | Vec | {escape_rich(snippet)}...")
                    seen_ids.add(r["rowid"])
            if not fts_results and not semantic_results:
                output.append(f"No results found for '{query}'.")
            return cap_tool_output("\n".join(output), max_chars=1500)

        elif layer == "L2":
            if target_id is None:
                return "Error: target_id is required for L2 layer."
            detail = logger.get_memory_detail(int(target_id))
            if detail:
                output = [f"### L2 Summary (ID: {target_id}):"]
                output.append(f"Content snippet:\n{escape_rich(str(detail['content'])[:400])}")
                return cap_tool_output("\n".join(output), max_chars=1500)
            return f"Memory {target_id} not found."

        elif layer == "L3":
            if target_id is None:
                return "Error: target_id is required for L3 layer."
            detail = logger.get_memory_detail(int(target_id))
            if detail:
                return cap_tool_output(
                    f"### L3 Full Content (ID: {target_id})\nContent:\n{detail['content']}",
                    max_chars=2000,
                )
            return f"Memory {target_id} not found."

        return f"Unknown layer: {layer!r}. Use 'L1', 'L2', or 'L3'."
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def fetch_memory_detail(memory_id: int) -> str:
    """Retrieves full content of a specific memory by ID (Layer 3)."""
    from infra.persistence import SessionLogger

    logger = SessionLogger("search_service")
    detail = logger.get_memory_detail(memory_id)
    if detail:
        return cap_tool_output(
            f"### Memory Detail (ID: {memory_id})\nContent:\n{detail['content']}",
            max_chars=2000,
        )
    return f"Memory {memory_id} not found."


@tool
def forget_session(session_id_to_forget: str) -> str:
    """Deletes data associated with a session ID."""
    from infra.persistence import SessionLogger

    logger = SessionLogger("admin_service")
    logger.delete_memory_by_session(session_id_to_forget)
    return f"Session {session_id_to_forget} has been forgotten."
