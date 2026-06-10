"""Ferramenta de delegação para sub-agentes (decorada com @tool do LangChain)."""

from __future__ import annotations

import time
import traceback
from typing import Optional

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

from core.utils import cap_tool_output


@tool
async def delegate_to_agent(agent_id: str, mission: str, parent_yolo: bool = False, workspace_path: Optional[str] = None) -> str:
    """Delegates a task to a specialist sub-agent (coder, researcher)."""
    import subprocess
    import tempfile
    import os
    import shutil
    import time
    import traceback
    from infra.agent_loader import agent_loader
    from core.ui_interface import get_current_session_id
    from tools.registry import _HARNESS_REF
    from langchain_core.messages import SystemMessage, HumanMessage

    current_session = get_current_session_id() or "unknown"

    if _HARNESS_REF is None:
        return "Error: Harness not initialized."

    active_workspace = workspace_path
    worktree_created = False

    try:
        config = agent_loader.load_agent(agent_id)
        specialist_prompt = config["instructions"].replace("{{mission}}", mission)
        specialist_permissions = config.get("permissions", "read")
        briefing = f"MISSION: {mission}\nPERMISSIONS: {specialist_permissions}"
        skills_content = ""
        for skill_name in config.get("skills", []):
            skills_content += f"\n\n--- Skill: {skill_name} ---\n{agent_loader.load_skill(skill_name)}"

        tools_manual = ""
        allowed_tools = config.get("tools", [])
        if allowed_tools:
            tools_manual = "\n\n### AUTHORIZED TOOLS MANUAL:\n"
            for t_name in allowed_tools:
                tools_manual += agent_loader.load_tool_manual(t_name)

        ts = int(time.time()) % 10000
        sub_session_id = f"sub-{current_session[:8]}-{agent_id}-{ts}"

        # Setup Git Worktree for isolation if no workspace_path provided
        if not active_workspace:
            try:
                temp_dir = tempfile.gettempdir()
                active_workspace = os.path.join(temp_dir, f"k-claw-{sub_session_id}")
                # Use --detach to avoid branch conflicts
                subprocess.run(["git", "worktree", "add", "--detach", active_workspace, "HEAD"], check=True, capture_output=True, text=True)
                worktree_created = True
            except Exception as wt_err:
                active_workspace = None

        sub_state = {
            "messages": [
                SystemMessage(content=f"{specialist_prompt}\n{briefing}{tools_manual}{skills_content}"),
                HumanMessage(content=mission),
            ],
            "context_budget": 50,
            "max_iterations": config.get("max_iterations", 10),
            "iteration_count": 0,
            "session_id": sub_session_id,
            "permissions": specialist_permissions,
            "workspace_path": active_workspace,
            "context_summary": "",
            "incognito": False,
            "yolo": parent_yolo,
        }

        # Step 1: Execute Specialist Task
        result_state = await _HARNESS_REF.ainvoke(
            sub_state, config={"configurable": {"thread_id": sub_state["session_id"]}}
        )
        final_report = result_state["messages"][-1].content

        # Step 2: Automatic Verification for 'coder'
        if agent_id == "coder":
            max_retries = 3
            retries = 0

            while retries < max_retries:
                # Trigger Verifier
                verifier_mission = f"Verify this Coder's report and work. Mission was: {mission}\n\nCoder's Report:\n{final_report}"

                # Pass the SAME active_workspace to the verifier so it can see the coder's work
                verifier_result = await delegate_to_agent.ainvoke(
                    {"agent_id": "verifier", "mission": verifier_mission, "parent_yolo": parent_yolo, "workspace_path": active_workspace}
                )

                # Check status in verifier result (looking for STATUS: PASS)
                if "STATUS: PASS" in verifier_result:
                    return f"### TECHNICAL REPORT FROM SPECIALIST ({agent_id}) - VERIFIED PASS:\n{cap_tool_output(final_report, max_chars=4000)}\n\n--- Verification Summary ---\n{verifier_result}"

                # If FAIL/NEEDS_REVIEW, loop back to Coder with feedback
                retries += 1
                if retries >= max_retries:
                    return f"### TECHNICAL REPORT FROM SPECIALIST ({agent_id}) - ESCALATED (Verification Failed after {retries} retries):\n{cap_tool_output(final_report, max_chars=4000)}\n\n--- Final Verification Failure ---\n{verifier_result}"

                # Feedback to Coder
                mission = f"Fix the issues found in verification. Original Mission: {mission}\n\nVerification Feedback:\n{verifier_result}"
                sub_state["messages"].append(HumanMessage(content=mission))
                sub_state["iteration_count"] = 0 # Reset iteration for correction

                result_state = await _HARNESS_REF.ainvoke(
                    sub_state, config={"configurable": {"thread_id": sub_state["session_id"]}}
                )
                final_report = result_state["messages"][-1].content

        return f"### TECHNICAL REPORT FROM SPECIALIST ({agent_id}):\n{cap_tool_output(final_report, max_chars=4000)}"

    except Exception as e:
        return f"Error delegating to sub-agent '{agent_id}': {str(e)}\nTrace: {traceback.format_exc()}"
    finally:
        # Cleanup worktree only if we created it here
        if worktree_created and active_workspace:
            try:
                subprocess.run(["git", "worktree", "remove", "--force", active_workspace], check=True, capture_output=True)
            except Exception:
                if os.path.exists(active_workspace):
                    shutil.rmtree(active_workspace, ignore_errors=True)
