"""Unit tests for infra/agent_loader.py — agent definition loading."""

import os
import pytest
from unittest.mock import patch, MagicMock
from infra.agent_loader import AgentDefinitionLoader


class TestParseMdWithFrontmatter:
    """Test markdown frontmatter parsing."""

    def test_parses_frontmatter(self, temp_dir):
        file_path = os.path.join(temp_dir, "test.md")
        with open(file_path, "w") as f:
            f.write("---\nname: Test Agent\ndescription: A test agent\n---\n# Instructions\nDo things.")

        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        result = loader._parse_md_with_frontmatter(file_path)
        assert result["name"] == "Test Agent"
        assert result["description"] == "A test agent"
        assert "Do things" in result["instructions"]

    def test_parses_without_frontmatter(self, temp_dir):
        file_path = os.path.join(temp_dir, "plain.md")
        with open(file_path, "w") as f:
            f.write("Just plain instructions.")

        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        result = loader._parse_md_with_frontmatter(file_path)
        assert result["instructions"] == "Just plain instructions."

    def test_file_not_found(self, temp_dir):
        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        with pytest.raises(FileNotFoundError):
            loader._parse_md_with_frontmatter(os.path.join(temp_dir, "nonexistent.md"))


class TestLoadAgent:
    """Test agent loading."""

    def test_loads_agent(self, temp_dir):
        file_path = os.path.join(temp_dir, "test_agent.md")
        with open(file_path, "w") as f:
            f.write("---\nname: Test Agent\npermissions: read\n---\nSystem prompt here.")

        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        result = loader.load_agent("test_agent")
        assert result["name"] == "Test Agent"
        assert "System prompt here" in result["instructions"]


class TestLoadSkill:
    """Test skill loading."""

    def test_loads_skill(self, temp_dir):
        file_path = os.path.join(temp_dir, "test_skill.md")
        with open(file_path, "w") as f:
            f.write("---\nname: Test Skill\n---\nSkill instructions here.")

        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        result = loader.load_skill("test_skill")
        assert result == "Skill instructions here."

    def test_loads_skill_without_frontmatter(self, temp_dir):
        file_path = os.path.join(temp_dir, "plain_skill.md")
        with open(file_path, "w") as f:
            f.write("Plain skill instructions.")

        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        result = loader.load_skill("plain_skill")
        assert result == "Plain skill instructions."


class TestLoadToolManual:
    """Test tool manual loading."""

    def test_loads_tool_manual(self, temp_dir):
        file_path = os.path.join(temp_dir, "test_tool.md")
        with open(file_path, "w") as f:
            f.write("---\ndescription: A test tool\nusage: test_tool --arg\n---\nDetailed instructions.")

        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        result = loader.load_tool_manual("test_tool")
        assert "test_tool" in result
        assert "A test tool" in result
        assert "test_tool --arg" in result

    def test_missing_tool_returns_empty(self, temp_dir):
        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        result = loader.load_tool_manual("nonexistent")
        assert result == ""


class TestListAvailableAgents:
    """Test agent listing."""

    def test_lists_agents(self, temp_dir):
        for name in ["agent_a", "agent_b"]:
            file_path = os.path.join(temp_dir, f"{name}.md")
            with open(file_path, "w") as f:
                f.write(f"---\nname: {name}\n---\nInstructions.")

        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        agents = loader.list_available_agents()
        ids = [a["id"] for a in agents]
        assert "agent_a" in ids
        assert "agent_b" in ids

    def test_empty_directory(self, temp_dir):
        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        agents = loader.list_available_agents()
        assert agents == []

    def test_nonexistent_directory(self, temp_dir):
        loader = AgentDefinitionLoader(
            agents_dir=os.path.join(temp_dir, "nonexistent"),
            skills_dir=temp_dir,
            tools_dir=temp_dir,
        )
        agents = loader.list_available_agents()
        assert agents == []

    def test_skips_invalid_files(self, temp_dir):
        # Create a valid agent
        with open(os.path.join(temp_dir, "valid.md"), "w") as f:
            f.write("---\nname: Valid\n---\nInstructions.")
        # Create a non-md file
        with open(os.path.join(temp_dir, "readme.txt"), "w") as f:
            f.write("Not an agent")

        loader = AgentDefinitionLoader(agents_dir=temp_dir, skills_dir=temp_dir, tools_dir=temp_dir)
        agents = loader.list_available_agents()
        ids = [a["id"] for a in agents]
        assert "valid" in ids
        assert "readme" not in ids
