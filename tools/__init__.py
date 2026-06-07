"""Package de ferramentas do agente.

Cada módulo contém ferramentas relacionadas (file, shell, memory, delegate).
Importe do sub-módulo específico ou use este barrel para compatibilidade.
"""

from tools.classification import classify_shell_command, risk_level_value
from tools.registry import ToolDescriptor, ToolRegistry, registry, set_harness_refs, _HARNESS_REF
from tools.file_tools import list_directory, read_file, replace_string, write_file, grep_search, glob_search
from tools.shell_tools import run_shell
from tools.memory_tools import search_memory, fetch_memory_detail, forget_session
from tools.delegate_tools import delegate_to_agent

__all__ = [
    # classification
    "classify_shell_command",
    "risk_level_value",
    # registry
    "ToolDescriptor",
    "ToolRegistry",
    "registry",
    "set_harness_refs",
    "_HARNESS_REF",
    # file tools
    "list_directory",
    "read_file",
    "replace_string",
    "write_file",
    "grep_search",
    "glob_search",
    # shell tools
    "run_shell",
    # memory tools
    "search_memory",
    "fetch_memory_detail",
    "forget_session",
    # delegate tools
    "delegate_to_agent",
]

# ── Auto-registro das tools no registry ──────────────────────────────────────
registry.register("list_directory", "Lists files in a project path.", "read", list_directory)
registry.register("read_file", "Reads a file from disk with paging.", "read", read_file)
registry.register("replace_string", "Surgically replaces a specific exact string block in a file.", "write", replace_string, requires_approval=True)
registry.register("write_file", "Writes content to a file.", "write", write_file, requires_approval=True)
registry.register("grep_search", "Searches for a regex pattern in file contents.", "read", grep_search)
registry.register("glob_search", "Finds files matching a glob pattern.", "read", glob_search)
registry.register("run_shell", "Executes a bash command.", "execute", run_shell, requires_approval=True)
registry.register("search_memory", "Layered memory search (L1 index, L2 summary, L3 full).", "read", search_memory)
registry.register("fetch_memory_detail", "Reads full content of a memory ID.", "read", fetch_memory_detail)
registry.register("forget_session", "Deletes data associated with a session ID.", "execute", forget_session, requires_approval=True)
registry.register("delegate_to_agent", "Delegates a task to a specialist sub-agent.", "read", delegate_to_agent)
