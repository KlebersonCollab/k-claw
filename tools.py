import os
import subprocess
from typing import Callable, Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from utils import redact_sensitive_info, path_filter

class ToolDescriptor(BaseModel):
    name: str
    description: str
    permissions_required: str # "read", "write", "execute"
    handler: Any
    requires_approval: bool = False

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolDescriptor] = {}

    def register(self, name: str, description: str, permissions: str, handler: Any, requires_approval: bool = False):
        self.tools[name] = ToolDescriptor(
            name=name,
            description=description,
            permissions_required=permissions,
            handler=handler,
            requires_approval=requires_approval
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
def read_file(path: str) -> str:
    """Reads a file from disk, respecting project ignore rules."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."

        if os.path.isdir(path):
            return f"Error: {path} is a directory. Use list_directory instead."

        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file."""
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
def search_memory(query: str) -> str:
    """Searches past conversation history for specific keywords or concepts."""
    from persistence import SessionLogger
    logger = SessionLogger("search_service")
    fts_results = logger.search_messages(query)
    semantic_results = logger.semantic_search(query)

    if not fts_results and not semantic_results:
        return f"No results found for '{query}'"

    output = ["### Memory Search Index (Layer 1):"]
    seen_ids = set()
    for r in fts_results[:5]:
        output.append(f"- ID: {r['rowid']} | Type: Keyword Match")
        seen_ids.add(r['rowid'])
    for r in semantic_results[:5]:
        if r['rowid'] not in seen_ids:
            output.append(f"- ID: {r['rowid']} | Type: Semantic Match | Summary: {escape_rich(r['summary'])}")
            seen_ids.add(r['rowid'])

    output.append("\nUse 'fetch_memory_detail(id)' to read full content.")
    return "\n".join(output)

def escape_rich(text):
    return text.replace("[", "[[").replace("]", "]]")

@tool
def fetch_memory_detail(memory_id: int) -> str:
    """Retrieves full content of a specific memory by ID (Layer 2)."""
    from persistence import SessionLogger
    logger = SessionLogger("search_service")
    detail = logger.get_memory_detail(memory_id)
    if detail:
        return f"### Memory Detail (ID: {memory_id})\nContent:\n{detail['content']}"
    return f"Memory {memory_id} not found."

@tool
def forget_session(session_id_to_forget: str) -> str:
    """Deletes data associated with a session ID."""
    from persistence import SessionLogger
    logger = SessionLogger("admin_service")
    logger.delete_memory_by_session(session_id_to_forget)
    return f"Session {session_id_to_forget} has been forgotten."

@tool
async def delegate_to_agent(agent_id: str, mission: str) -> str:
    """Delegates a task to a specialist sub-agent (coder, researcher)."""
    from agent_loader import agent_loader
    global _HARNESS_REF
    if _HARNESS_REF is None:
        return "Error: Harness not initialized for delegation."
    try:
        config = agent_loader.load_agent(agent_id)
        specialist_prompt = config["instructions"].replace("{{mission}}", mission)
        specialist_permissions = config.get("permissions", "read")
        briefing = f"MISSION: {mission}\nPERMISSIONS: {specialist_permissions}"

        skills_content = ""
        for skill_name in config.get("skills", []):
            skills_content += f"\n\n--- Skill: {skill_name} ---\n{agent_loader.load_skill(skill_name)}"

        sub_state = {
            "messages": [SystemMessage(content=f"{specialist_prompt}\n{briefing}{skills_content}"), HumanMessage(content=mission)],
            "context_budget": config.get("max_iterations", 10), "iteration_count": 0,
            "session_id": f"sub-{agent_id}-{os.urandom(4).hex()}",
            "permissions": specialist_permissions, "context_summary": "", "incognito": False
        }

        result_state = await _HARNESS_REF.ainvoke(sub_state, config={"configurable": {"thread_id": sub_state["session_id"]}})
        return f"### TECHNICAL REPORT FROM SPECIALIST ({agent_id}):\n{result_state['messages'][-1].content}"
    except Exception as e:
        import traceback
        return f"Error delegating to sub-agent '{agent_id}': {str(e)}\nTrace: {traceback.format_exc()}"

# Registry
registry.register("list_directory", "Lists files in a project path.", "read", list_directory)
registry.register("read_file", "Reads a file from disk.", "read", read_file)
registry.register("write_file", "Writes content to a file.", "write", write_file, requires_approval=True)
registry.register("run_shell", "Executes a bash command.", "execute", run_shell, requires_approval=True)
registry.register("search_memory", "Searches past conversation history.", "read", search_memory)
registry.register("fetch_memory_detail", "Reads full content of a memory ID.", "read", fetch_memory_detail)
registry.register("forget_session", "Deletes data associated with a session ID.", "execute", forget_session, requires_approval=True)
registry.register("delegate_to_agent", "Delegates a task to a specialist sub-agent.", "read", delegate_to_agent)
