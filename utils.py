import os
import re
import fnmatch
from langchain.chat_models import init_chat_model

class PathFilter:
    def __init__(self, root_path: str = "."):
        self.root_path = os.path.abspath(root_path)
        # Patterns that match a whole directory name or file name
        self.ignore_patterns = [
            ".git", ".venv", "__pycache__", "node_modules",
            ".api.pid", "api.log", "harness.db", "harness.db-shm", "harness.db-wal", ".agents"
        ]
        self._load_gitignore()

    def _load_gitignore(self):
        gitignore_path = os.path.join(self.root_path, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.ignore_patterns.append(line.rstrip("/"))

    def is_ignored(self, path: str) -> bool:
        full_path = os.path.abspath(path)
        rel_path = os.path.relpath(full_path, self.root_path)

        if rel_path == ".":
            return False

        # Check every part of the path
        parts = rel_path.split(os.sep)
        for part in parts:
            if part in self.ignore_patterns:
                return True
            for pattern in self.ignore_patterns:
                if fnmatch.fnmatch(part, pattern):
                    return True
        return False

path_filter = PathFilter()

# Global cache for the model instance
_MODEL_CACHE = {}

def get_model():
    provider = os.getenv("AI_PROVIDER", "openai")
    model_name = os.getenv("AI_MODEL", "gpt-4o")
    cache_key = f"{provider}:{model_name}"

    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    kwargs = {}
    if provider == "openrouter":
        kwargs["base_url"] = "https://openrouter.ai/api/v1"
        kwargs["api_key"] = os.getenv("OPENROUTER_API_KEY")
        provider = "openai"

    model = init_chat_model(model_name, model_provider=provider, **kwargs)
    _MODEL_CACHE[cache_key] = model
    return model

def redact_sensitive_info(text: str) -> str:
    """Masks potential API keys and secrets in the text."""
    patterns = [
        r"(sk-[a-zA-Z0-9]{32,})", # OpenAI/Anthropic
        r"(AIza[0-9A-Za-z-_]{35})", # Google
        r"([a-f0-9]{32})", # Generic hex
    ]
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED]", redacted)
    return redacted

def recursive_load_context(start_path: str = ".") -> str:
    """Walks up from start_path to root, collecting context files."""
    current_path = os.path.abspath(start_path)
    context_content = []
    visited_files = set()
    target_files = ["AGENTS.md", "CONTEXT.md", ".harness.md"]

    while True:
        for target in target_files:
            file_path = os.path.join(current_path, target)
            if os.path.exists(file_path) and file_path not in visited_files:
                with open(file_path, "r", encoding="utf-8") as f:
                    context_content.append(f"--- Context from {file_path} ---\n{f.read()}\n")
                visited_files.add(file_path)

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path: break
        current_path = parent_path

    return "\n".join(reversed(context_content))
