"""
Orchestrator (Father) — delegates to sub-agents and decides based on reports.

Implements the flow:
    Orquestrador → coder → verifier → decision (DELIVER / ESCALATE / LOOP)
"""

from __future__ import annotations
from tools import registry


class Orchestrator:
    """
    Simplified orchestrator that manages the delegation loop between
    coder and verifier sub-agents.
    """

    def __init__(self, max_correction_retries: int = 3):
        self.max_correction_retries = max_correction_retries
        self._delegate = registry.tools.get("delegate_to_agent")

    def delegate_to_agent(self, agent_id: str, mission: str) -> dict:
        """
        Delegate a task to a sub-agent. In production, this calls the
        registry tool; in tests, it is mocked.
        """
        if self._delegate is None:
            raise RuntimeError("delegate_to_agent not registered")
        return self._delegate(agent_id=agent_id, mission=mission)

    def execute_task(self, task: str) -> dict:
        """
        Execute a full task through the architect → coder → verifier loop.

        Returns a dict with:
            - decision: "DELIVER" | "ESCALATE"
            - status: final verifier status
            - correction_rounds: number of correction loops executed
            - final_report: the accepted report
        """
        correction_rounds = 0

        # Step 1: Delegate to architect for design
        design_report = self.delegate_to_agent("architect", f"Design the solution for: {task}")

        # Step 2: Delegate to coder with design report
        coder_mission = f"Implement the task based on this design report: {design_report}. Task: {task}"
        coder_report = self.delegate_to_agent("coder", coder_mission)

        # Step 3: Delegate to verifier with coder's report
        verifier_report = self.delegate_to_agent(
            "verifier",
            f"Verify the coder's work. Original Task: {task}. Technical Report: {coder_report}"
        )

        # Step 3: Decision loop
        while verifier_report.get("status") in ("FAIL", "NEEDS_REVIEW"):
            if correction_rounds >= self.max_correction_retries:
                return {
                    "decision": "ESCALATE",
                    "status": verifier_report.get("status"),
                    "correction_rounds": correction_rounds,
                    "final_report": verifier_report,
                }

            correction_rounds += 1

            # Re-delegate to coder with feedback
            feedback = f"Issues found: {verifier_report.get('issues', [])}. Recommendations: {verifier_report.get('recommendations', [])}"
            coder_report = self.delegate_to_agent(
                "coder",
                f"Fix the issues. Original task: {task}. Feedback: {feedback}"
            )

            # Re-verify
            verifier_report = self.delegate_to_agent(
                "verifier",
                f"Re-verify the corrected work. Technical Report: {coder_report}"
            )

        # PASS
        return {
            "decision": "DELIVER",
            "status": verifier_report.get("status", "PASS"),
            "correction_rounds": correction_rounds,
            "final_report": verifier_report,
        }
