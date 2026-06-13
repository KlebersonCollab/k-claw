import os
import json
import pytest
from tools.env_tools import detect_workspace_env

def test_detect_workspace_env(tmp_path):
    # Setup mock workspace
    prev_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        # 1. Create a dummy pyproject.toml
        (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname='test'")
        
        # 2. Call tool
        result_json = detect_workspace_env.invoke({})
        data = json.loads(result_json)
        
        # 3. Assertions
        assert data["primary_language"] == "Python"
        assert "pyproject.toml" in data["indicators_found"]
        assert data["build_tool"] in ["uv/poetry/pip", "pip"]
        assert data["suggested_test_command"] == "pytest"
        
        # Add another file to see if it catches it
        (tmp_path / "Makefile").write_text("test:\n\techo 'test'")
        result_json2 = detect_workspace_env.invoke({})
        data2 = json.loads(result_json2)
        assert "Makefile" in data2["indicators_found"]
        
    finally:
        os.chdir(prev_cwd)
