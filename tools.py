import os
import subprocess
from typing import Callable, Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from utils import redact_sensitive_info, path_filter

# --- Classificação Dinâmica de Comandos Shell por Nível de Risco ---
_SHELL_COMMAND_RISK: Dict[str, set] = {
    # read-only commands — safe, never destructive
    "read": {
        "ls", "cat", "grep", "find", "echo", "pwd", "head", "tail",
        "wc", "less", "more", "diff", "file", "stat", "which",
        "whoami", "date", "uname", "type", "env",
    },
    # workspace commands — modify files but not the system
    "write": {
        "cp", "mv", "mkdir", "touch", "tee", "sort", "uniq",
        "sed", "awk", "pip", "uv", "npm", "node", "python", "python3",
        "git", "npx", "make",
    },
    # full access commands — destructive/system-level
    "full": {
        "rm", "sudo", "chmod", "chown", "kill", "shutdown",
        "mkfs", "dd", "iptables", "useradd", "usermod", "passwd",
    },
}


def classify_shell_command(command: str) -> str:
    """Classify a shell command by risk level.

    Args:
        command: Raw shell command string.

    Returns:
        'read' (safe inspection), 'write' (file modification), or 'full' (destructive/system).
        Unknown commands default to 'write' (workspace) as a safe middle ground.
    """
    base = command.strip().split()[0] if command.strip() else ""
    if base in _SHELL_COMMAND_RISK["full"]:
        return "full"
    if base in _SHELL_COMMAND_RISK["read"]:
        return "read"
    if base in _SHELL_COMMAND_RISK["write"]:
        return "write"
    # Unknown commands default to workspace level (safe middle ground)
    return "write"


def risk_level_value(level: str) -> int:
    """Convert a risk level string to a numeric value for comparison.

    Hierarchy: read (1) < write (2) < full/execute (3)
    """
    return {"read": 1, "write": 2, "full": 3, "execute": 3}.get(level, 2)


class ToolDescriptor(BaseModel):
    name: str
    description: str
    permissions_required: str  # "read", "write", "execute"
    handler: Any
    requires_approval: bool = False


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolDescriptor] = {}

    def register(
        self,
        name: str,
        description: str,
        permissions: str,
        handler: Any,
        requires_approval: bool = False,
    ):
        self.tools[name] = ToolDescriptor(
            name=name,
            description=description,
            permissions_required=permissions,
            handler=handler,
            requires_approval=requires_approval,
        )

    def get_langchain_tools(self, current_permissions: str) -> List[Any]:
        available_tools = []
        for desc in self.tools.values():
            if self._has_permission(current_permissions, desc.permissions_required):
                available_tools.append(desc.handler)
        return available_tools

    def _has_permission(self, current: str, required: str) -> bool:
        hierarchy = {"read": 1, "write": 2, "execute": 3}
        return hierarchy.get(current, 0) >= hierarchy.get(required, 0)


registry = ToolRegistry()

# --- Global Reference for Delegation (Late Binding) ---
_HARNESS_REF = None


def set_harness_refs(h_ref):
    global _HARNESS_REF
    _HARNESS_REF = h_ref


# --- Built-in Primitives ---


@tool
def list_directory(path: str = ".") -> str:
    """Lists files and directories at a given path, respecting project ignore rules."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."
        items = os.listdir(path)
        visible_items = []
        for item in items:
            item_path = os.path.join(path, item)
            if not path_filter.is_ignored(item_path):
                type_suffix = "/" if os.path.isdir(item_path) else ""
                visible_items.append(f"{item}{type_suffix}")
        return "\n".join(sorted(visible_items)) if visible_items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def read_file(path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """Reads a file from disk with optional line-range pagination (1-based indexing)."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."
        if os.path.isdir(path):
            return f"Error: {path} is a directory. Use list_directory instead."

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)
        if start_line is not None or end_line is not None:
            s = (start_line - 1) if start_line else 0
            e = end_line if end_line else total_lines
            content = "".join(lines[s:e])
            return f"--- Lines {s + 1} to {min(e, total_lines)} of {total_lines} ---\n{content}"

        return "".join(lines)
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def edit_file(path: str, start_line: int, end_line: int, content: str) -> str:
    """Surgically replaces a range of lines (start_line to end_line, inclusive, 1-based) with new content."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        s = start_line - 1
        e = end_line  # Slice e is exclusive, but our end_line is inclusive

        lines[s:e] = [content + ("\n" if not content.endswith("\n") else "")]

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return f"Successfully updated {path} from line {start_line} to {end_line}."
    except Exception as e:
        return f"Error editing file: {str(e)}"


@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file (WARNING: Overwrites entire file)."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {path} written successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def run_shell(command: str) -> str:
    """Executes a bash command."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool
def search_memory(
    query: str, layer: str = "L1", target_id: Optional[int] = None
) -> str:
    """Layered search in past conversation history.

    Token-efficient multi-layer search protocol:
      L1 (cheap):  IDs + short snippets only
      L2 (medium): Summary / first 500 chars for a target_id
      L3 (full):   Complete content for a target_id

    Args:
        query: Search query string (used in L1; ignored in L2/L3).
        layer: 'L1' (index), 'L2' (summary), or 'L3' (full content).
        target_id: Memory rowid — required for L2 and L3.

    Returns:
        Formatted search results layer.
    """
    from persistence import SessionLogger

    logger = SessionLogger("search_service")

    if layer == "L1":
        # Cheap: IDs + snippets only
        fts_results = logger.search_messages(query)
        semantic_results = logger.semantic_search(query, limit=5)
        output = ["### L1 Memory Index (cheap lookup):"]
        seen_ids: set = set()
        from utils import escape_rich
        for r in fts_results[:5]:
            snippet = r["content"][:80].replace("\n", " ")
            output.append(f"- ID: {r['rowid']} | KW | {escape_rich(snippet)}...")
            seen_ids.add(r["rowid"])
        for r in semantic_results[:5]:
            if r["rowid"] not in seen_ids:
                snippet = (r.get("summary") or "")[:80]
                output.append(
                    f"- ID: {r['rowid']} | Vec | score={r['score']:.2f} | {escape_rich(snippet)}..."
                )
                seen_ids.add(r["rowid"])
        if not fts_results and not semantic_results:
            output.append(f"No results found for '{query}'.")
        output.append(
            "\nUse search_memory(query, layer='L2', target_id=X) for summary."
        )
        output.append("Use fetch_memory_detail(id) for full content (L3).")
        return "\n".join(output)

    elif layer == "L2":
        if target_id is None:
            return "Error: target_id is required for L2 layer."
        detail = logger.get_memory_detail(int(target_id))
        from utils import escape_rich
        if detail:
            output = [f"### L2 Summary (ID: {target_id}):"]
            output.append(f"Session: {detail.get('session_id', 'unknown')}")
            output.append(f"Content:\n{escape_rich(detail['content'][:500])}")
            output.append("\nUse fetch_memory_detail(id) for full content (L3).")
            return "\n".join(output)
        return f"Memory {target_id} not found."

    elif layer == "L3":
        if target_id is None:
            return "Error: target_id is required for L3 layer."
        detail = logger.get_memory_detail(int(target_id))
        if detail:
            return f"### L3 Full Content (ID: {target_id})\nContent:\n{detail['content']}"
        return f"Memory {target_id} not found."

    return f"Unknown layer: {layer!r}. Use 'L1', 'L2', or 'L3'."


@tool
def fetch_memory_detail(memory_id: int) -> str:
    """Retrieves full content of a specific memory by ID (Layer 3)."""
    from persistence import SessionLogger

    logger = SessionLogger("search_service")
    detail = logger.get_memory_detail(memory_id)
    if detail:
        return (
            f"### Memory Detail (ID: {memory_id})\nContent:\n{detail['content']}"
        )
    return f"Memory {memory_id} not found."


@tool
def forget_session(session_id_to_forget: str) -> str:
    """Deletes data associated with a session ID."""
    from persistence import SessionLogger

    logger = SessionLogger("admin_service")
    logger.delete_memory_by_session(session_id_to_forget)
    return f"Session {session_id_to_forget} has been forgotten."


@tool
async def delegate_to_agent(agent_id: str, mission: str, parent_yolo: bool = False) -> str:
    """Delegates a task to a specialist sub-agent (coder, researcher)."""
    from agent_loader import agent_loader
    global _HARNESS_REF
    if _HARNESS_REF is None: return "Error: Harness not initialized."
    try:
        config = agent_loader.load_agent(agent_id)
        specialist_prompt = config["instructions"].replace("{{mission}}", mission)
        specialist_permissions = config.get("permissions", "read")
        briefing = f"MISSION: {mission}\nPERMISSIONS: {specialist_permissions}"

        # Specialist briefing and tools manual... (same as before)
        skills_content = ""
        for skill_name in config.get("skills", []):
            skills_content += f"\n\n--- Skill: {skill_name} ---\n{agent_loader.load_skill(skill_name)}"

        tools_manual = ""
        allowed_tools = config.get("tools", [])
        if allowed_tools:
            tools_manual = "\n\n### AUTHORIZED TOOLS MANUAL:\n"
            for t_name in allowed_tools:
                tools_manual += agent_loader.load_tool_manual(t_name)

        sub_state = {
            "messages": [SystemMessage(content=f"{specialist_prompt}\n{briefing}{tools_manual}{skills_content}"), HumanMessage(content=mission)],
            "context_budget": config.get("max_iterations", 10), "iteration_count": 0,
            "session_id": f"sub-{agent_id}-{os.urandom(4).hex()}",
            "permissions": specialist_permissions, "context_summary": "",
            "incognito": False,
            "yolo": parent_yolo  # PROPAGATE YOLO MODE
        }
        result_state = await _HARNESS_REF.ainvoke(sub_state, config={"configurable": {"thread_id": sub_state["session_id"]}})

        from utils import cap_tool_output
        final_report = result_state['messages'][-1].content
        # Cap the report to prevent orchestrator context explosion
        capped_report = cap_tool_output(final_report, max_chars=4000)

        return f"### TECHNICAL REPORT FROM SPECIALIST ({agent_id}):\n{capped_report}"

    except Exception as e:
        return f"Error delegating to sub-agent '{agent_id}': {str(e)}"


# --- Tool Registry ---
registry.register("list_directory", "Lists files in a project path.", "read", list_directory)
registry.register("read_file", "Reads a file from disk with paging.", "read", read_file)
registry.register("edit_file", "Surgically updates a file line range.", "write", edit_file, requires_approval=True)
registry.register("write_file", "Writes content to a file.", "write", write_file, requires_approval=True)
registry.register("run_shell", "Executes a bash command.", "execute", run_shell, requires_approval=True)
registry.register("search_memory", "Layered memory search (L1 index, L2 summary, L3 full).", "read", search_memory)
registry.register("fetch_memory_detail", "Reads full content of a memory ID.", "read", fetch_memory_detail)
registry.register("forget_session", "Deletes data associated with a session ID.", "execute", forget_session, requires_approval=True)
registry.register("delegate_to_agent", "Delegates a task to a specialist sub-agent.", "read", delegate_to_agent)
