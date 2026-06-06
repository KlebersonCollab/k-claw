import os
import yaml
import re
from typing import Dict, Any, List, Optional

class AgentDefinitionLoader:
    def __init__(self, agents_dir: str = ".agents/agents", skills_dir: str = ".agents/skills", tools_dir: str = ".agents/tools"):
        self.agents_dir = agents_dir
        self.skills_dir = skills_dir
        self.tools_dir = tools_dir

    def _parse_md_with_frontmatter(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not match:
            return {"instructions": content.strip()}
        config = yaml.safe_load(match.group(1))
        config["instructions"] = match.group(2).strip()
        return config

    def load_agent(self, agent_name: str) -> Dict[str, Any]:
        return self._parse_md_with_frontmatter(os.path.join(self.agents_dir, f"{agent_name}.md"))

    def load_skill(self, skill_name: str) -> str:
        data = self._parse_md_with_frontmatter(os.path.join(self.skills_dir, f"{skill_name}.md"))
        return data.get("instructions", "")

    def load_tool_manual(self, tool_name: str) -> str:
        path = os.path.join(self.tools_dir, f"{tool_name}.md")
        if not os.path.exists(path):
            return ""
        data = self._parse_md_with_frontmatter(path)
        manual = f"### Tool: {tool_name}\n"
        if "description" in data: manual += f"Description: {data['description']}\n"
        if "usage" in data: manual += f"Usage: {data['usage']}\n"
        manual += f"\nDetailed Instructions:\n{data.get('instructions', '')}\n"
        return manual

    def list_available_agents(self) -> List[Dict[str, str]]:
        agents = []
        if os.path.exists(self.agents_dir):
            for file in os.listdir(self.agents_dir):
                if file.endswith(".md"):
                    try:
                        name = file.replace(".md", "")
                        data = self.load_agent(name)
                        agents.append({"id": name, "name": data.get("name", name), "description": data.get("description", "")})
                    except: continue
        return agents

    def generate_tools_md(self):
        """Consolidates all tool manuals into a single TOOLS.md file."""
        if not os.path.exists(self.tools_dir): return
        output = ["# 🛠️ Agent Tools Manual\n", "Este arquivo é gerado automaticamente a partir de `.agents/tools/`.\n"]
        for file in sorted(os.listdir(self.tools_dir)):
            if file.endswith(".md"):
                name = file.replace(".md", "")
                output.append(self.load_tool_manual(name))
                output.append("---")
        with open("TOOLS.md", "w", encoding="utf-8") as f:
            f.write("\n".join(output))

agent_loader = AgentDefinitionLoader()
