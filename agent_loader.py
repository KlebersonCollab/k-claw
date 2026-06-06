import os
import yaml
import re
from typing import Dict, Any, List, Optional

class AgentDefinitionLoader:
    def __init__(self, agents_dir: str = ".agents/agents", skills_dir: str = ".agents/skills"):
        self.agents_dir = agents_dir
        self.skills_dir = skills_dir

    def load_agent(self, agent_name: str) -> Dict[str, Any]:
        file_path = os.path.join(self.agents_dir, f"{agent_name}.md")
        if not os.path.exists(file_path):
            # Try searching recursively or just the name
            file_path = os.path.join(self.agents_dir, f"{agent_name}.md")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Agent definition for '{agent_name}' not found at {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse Frontmatter
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not frontmatter_match:
            raise ValueError(f"Invalid format in {file_path}. Missing Frontmatter.")

        config = yaml.safe_load(frontmatter_match.group(1))
        instructions = frontmatter_match.group(2).strip()

        config["instructions"] = instructions
        return config

    def load_skill(self, skill_name: str) -> str:
        file_path = os.path.join(self.skills_dir, f"{skill_name}.md")
        if not os.path.exists(file_path):
            # Also check for uppercase variants as per user comment
            file_path = os.path.join(self.skills_dir, f"{skill_name.upper()}.md")
            if not os.path.exists(file_path):
                return f"\n[Warning: Skill {skill_name} not found]\n"

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def list_available_agents(self) -> List[Dict[str, str]]:
        agents = []
        if not os.path.exists(self.agents_dir):
            return []

        for file in os.listdir(self.agents_dir):
            if file.endswith(".md"):
                try:
                    agent_name = file.replace(".md", "")
                    data = self.load_agent(agent_name)
                    agents.append({
                        "id": agent_name,
                        "name": data.get("name", agent_name),
                        "description": data.get("description", "No description provided.")
                    })
                except Exception:
                    continue
        return agents

agent_loader = AgentDefinitionLoader()
