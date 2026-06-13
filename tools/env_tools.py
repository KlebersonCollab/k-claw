"""Ferramenta agnóstica para detecção de ambiente e stack tecnológica."""

import os
import json
from langchain_core.tools import tool

@tool
def detect_workspace_env() -> str:
    """
    Detects the programming languages, frameworks, build tools, and test commands 
    of the current workspace. Use this to adapt your reasoning to the project's tech stack.
    """
    workspace = os.getcwd()
    env_data = {
        "primary_language": "Unknown",
        "frameworks": [],
        "build_tool": "Unknown",
        "suggested_test_command": "Unknown",
        "indicators_found": []
    }

    # Common indicators
    indicators = {
        "pyproject.toml": {"lang": "Python", "tool": "uv/poetry/pip", "test": "pytest"},
        "requirements.txt": {"lang": "Python", "tool": "pip", "test": "pytest"},
        "package.json": {"lang": "JavaScript/TypeScript", "tool": "npm/yarn/pnpm", "test": "npm test"},
        "Cargo.toml": {"lang": "Rust", "tool": "cargo", "test": "cargo test"},
        "go.mod": {"lang": "Go", "tool": "go", "test": "go test ./..."},
        "pom.xml": {"lang": "Java", "tool": "maven", "test": "mvn test"},
        "build.gradle": {"lang": "Java", "tool": "gradle", "test": "gradle test"},
        "Makefile": {"lang": "Any", "tool": "make", "test": "make test"},
        "docker-compose.yml": {"framework": "Docker"},
        "pytest.ini": {"test": "pytest"},
    }

    for file_name, meta in indicators.items():
        if os.path.exists(os.path.join(workspace, file_name)):
            env_data["indicators_found"].append(file_name)
            if "lang" in meta and env_data["primary_language"] == "Unknown":
                env_data["primary_language"] = meta["lang"]
            if "tool" in meta and env_data["build_tool"] == "Unknown":
                env_data["build_tool"] = meta["tool"]
            if "test" in meta and env_data["suggested_test_command"] == "Unknown":
                env_data["suggested_test_command"] = meta["test"]
            if "framework" in meta:
                env_data["frameworks"].append(meta["framework"])

    # Fallback to file extension scanning if no major config found
    if env_data["primary_language"] == "Unknown":
        ext_counts = {".py": 0, ".js": 0, ".ts": 0, ".go": 0, ".rs": 0, ".java": 0}
        for root, dirs, files in os.walk(workspace):
            if ".git" in dirs: dirs.remove(".git")
            if "node_modules" in dirs: dirs.remove("node_modules")
            if ".venv" in dirs: dirs.remove(".venv")
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in ext_counts:
                    ext_counts[ext] += 1
        
        dominant_ext = max(ext_counts, key=ext_counts.get)
        if ext_counts[dominant_ext] > 0:
            ext_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".go": "Go", ".rs": "Rust", ".java": "Java"}
            env_data["primary_language"] = ext_map.get(dominant_ext, "Unknown")

    return json.dumps(env_data, indent=2)
