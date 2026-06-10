"""
End-to-end and integration tests for the Orquestrador → Coder → Verifier flow.

Flow under test:
    Orquestrador delegates to "coder" → receives Technical Report →
    delegates to "verifier" → receives Verification Report →
    decides: PASS (deliver) or FAIL (correction loop)

Covers:
    - Happy path: PASS → delivery
    - Correction loop: FAIL → re-delegate to coder (up to max retries)
    - NEEDS_REVIEW → request adjustments
    - Empty / malformed / invalid reports from coder
    - Verifier never receives write permissions
    - Loop termination (no infinite loops)
"""

import pytest
from unittest.mock import patch, MagicMock, call
from tools import registry
from infra.agent_loader import agent_loader
from infra.orchestrator import Orchestrator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def orchestrator():
    """
    Simulates the Orquestrador (Father) that delegates to sub-agents
    and makes decisions based on their reports.
    """
    return Orchestrator(max_correction_retries=3)


@pytest.fixture
def sample_coder_report_pass():
    """A well-formed Technical Report from coder that should pass verification."""
    return {
        "agent": "coder",
        "status": "completed",
        "summary": "Implemented feature X with full test coverage.",
        "files_created": ["src/feature_x.py", "tests/test_feature_x.py"],
        "files_modified": [],
        "tests": {
            "unit": "tests/test_feature_x.py",
            "integration": "tests/integration/test_feature_x_integration.py",
            "e2e": "tests/e2e/test_feature_x_e2e.py",
        },
        "test_results": "All 47 tests passed.",
        "coverage": "94%",
        "requirements": [
            "REQ-001: Feature X accepts input A → DONE",
            "REQ-002: Feature X returns output B → DONE",
            "REQ-003: Feature X handles edge case C → DONE",
        ],
    }


@pytest.fixture
def sample_coder_report_fail():
    """A Technical Report from coder that should fail verification."""
    return {
        "agent": "coder",
        "status": "completed",
        "summary": "Implemented feature X but tests are incomplete.",
        "files_created": ["src/feature_x.py"],
        "files_modified": [],
        "tests": {
            "unit": "tests/test_feature_x.py",
        },
        "test_results": "3 tests passed, 2 failed.",
        "coverage": "62%",
        "requirements": [
            "REQ-001: Feature X accepts input A → DONE",
            "REQ-002: Feature X returns output B → PARTIAL",
            "REQ-003: Feature X handles edge case C → NOT DONE",
        ],
    }


@pytest.fixture
def sample_verifier_report_pass():
    """Verification Report with STATUS=PASS."""
    return {
        "agent": "verifier",
        "status": "PASS",
        "checks": [
            "Requirements Compliance: All 3 requirements met",
            "Test Coverage: 94% (≥ 90% threshold)",
            "Code Quality: No anti-patterns found",
            "No Regressions: All existing tests still pass",
        ],
        "issues": [],
        "recommendations": [],
    }


@pytest.fixture
def sample_verifier_report_fail():
    """Verification Report with STATUS=FAIL."""
    return {
        "agent": "verifier",
        "status": "FAIL",
        "checks": [
            "Requirements Compliance: REQ-002 partial, REQ-003 not done",
            "Test Coverage: 62% (< 90% threshold)",
            "Code Quality: Missing edge case handling",
            "No Regressions: 2 new tests failing",
        ],
        "issues": [
            "REQ-002 only partially implemented",
            "REQ-003 not implemented",
            "Coverage below 90% threshold",
            "2 tests failing",
        ],
        "recommendations": [
            "Complete REQ-002 implementation",
            "Implement REQ-003 edge case handling",
            "Add missing tests to reach 90% coverage",
        ],
    }


@pytest.fixture
def sample_verifier_report_needs_review():
    """Verification Report with STATUS=NEEDS_REVIEW."""
    return {
        "agent": "verifier",
        "status": "NEEDS_REVIEW",
        "checks": [
            "Requirements Compliance: All requirements met",
            "Test Coverage: 91% (≥ 90% threshold)",
            "Code Quality: Minor style issues",
            "No Regressions: All existing tests pass",
        ],
        "issues": [
            "Minor: function naming could be more descriptive",
        ],
        "recommendations": [
            "Rename internal functions for clarity (non-blocking)",
        ],
    }


@pytest.fixture
def empty_coder_report():
    """An empty/malformed Technical Report."""
    return {}


@pytest.fixture
def malformed_coder_report():
    """A report with invalid syntax / missing critical sections."""
    return {
        "agent": "coder",
        "status": "completed",
        # Missing: files_created, tests, requirements
        "summary": "Done something.",
    }


# ---------------------------------------------------------------------------
# Integration Tests — Full Flow
# ---------------------------------------------------------------------------

class TestOrchestratorCoderVerifierFlow:
    """
    Integration tests for the complete Orquestrador → Coder → Verifier flow.
    """

    def test_orchestrator_always_calls_verifier_after_coder(
        self, orchestrator, sample_coder_report_pass, sample_verifier_report_pass
    ):
        """
        Scenario: Orquestrador delegates to coder, receives report,
        then MUST always delegate to verifier before delivering.
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            # First call returns coder report, second returns verifier report
            mock_delegate.side_effect = [sample_coder_report_pass, sample_verifier_report_pass]

            result = orchestrator.execute_task("Implement feature X")

            # Must have called delegate_to_agent exactly twice
            assert mock_delegate.call_count == 2

            # First call must be to coder
            first_call = mock_delegate.call_args_list[0]
            assert first_call[0][0] == "coder"

            # Second call must be to verifier
            second_call = mock_delegate.call_args_list[1]
            assert second_call[0][0] == "verifier"

    def test_pass_status_delivers_to_user(
        self, orchestrator, sample_coder_report_pass, sample_verifier_report_pass
    ):
        """
        Scenario: Verifier returns STATUS=PASS → Orquestrador delivers to user.
        No further delegation should happen.
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            mock_delegate.side_effect = [sample_coder_report_pass, sample_verifier_report_pass]

            result = orchestrator.execute_task("Implement feature X")

            assert result["decision"] == "DELIVER"
            assert result["status"] == "PASS"
            assert mock_delegate.call_count == 2  # coder + verifier only

    def test_fail_status_triggers_correction_loop(
        self, orchestrator, sample_coder_report_fail, sample_verifier_report_fail
    ):
        """
        Scenario: Verifier returns STATUS=FAIL → Orquestrador re-delegates to coder.
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            # coder → verifier(FAIL) → coder (correction) → verifier(PASS)
            corrected_report = dict(sample_coder_report_fail)
            corrected_report["test_results"] = "All tests passed."
            corrected_report["coverage"] = "95%"

            verifier_pass = {
                "agent": "verifier",
                "status": "PASS",
                "checks": ["All good after correction"],
                "issues": [],
                "recommendations": [],
            }

            mock_delegate.side_effect = [
                sample_coder_report_fail,
                sample_verifier_report_fail,
                corrected_report,
                verifier_pass,
            ]

            result = orchestrator.execute_task("Implement feature X")

            assert result["decision"] == "DELIVER"
            assert result["correction_rounds"] == 1
            assert mock_delegate.call_count == 4  # coder → verifier → coder → verifier

    def test_correction_loop_has_max_retries(
        self, orchestrator, sample_coder_report_fail, sample_verifier_report_fail
    ):
        """
        Scenario: Verifier keeps returning FAIL → loop must stop at max_retries.

        Flow with max_correction_retries=3:
            coder → verifier(FAIL) → coder → verifier(FAIL) → coder → verifier(FAIL) → coder → verifier(FAIL) → ESCALATE
            Total: 4 coder + 4 verifier = 8 calls
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            mock_delegate.side_effect = [
                sample_coder_report_fail,    # coder attempt 1
                sample_verifier_report_fail, # verifier → FAIL
                sample_coder_report_fail,    # coder attempt 2
                sample_verifier_report_fail, # verifier → FAIL
                sample_coder_report_fail,    # coder attempt 3
                sample_verifier_report_fail, # verifier → FAIL
                sample_coder_report_fail,    # coder attempt 4
                sample_verifier_report_fail, # verifier → FAIL → ESCALATE
            ]

            result = orchestrator.execute_task("Implement feature X")

            assert result["decision"] == "ESCALATE"
            assert result["correction_rounds"] == 3
            assert mock_delegate.call_count == 8  # 4 coder + 4 verifier

    def test_verifier_receives_coder_report_in_mission(
        self, orchestrator, sample_coder_report_pass, sample_verifier_report_pass
    ):
        """
        Scenario: The verifier's mission briefing must include the coder's report.
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            mock_delegate.side_effect = [sample_coder_report_pass, sample_verifier_report_pass]

            orchestrator.execute_task("Implement feature X")

            # Verify the verifier call includes the coder report
            verifier_call = mock_delegate.call_args_list[1]
            mission_arg = verifier_call[0][1]  # second positional arg is the mission
            assert "coder" in mission_arg.lower() or "technical report" in mission_arg.lower()

    def test_verifier_never_gets_write_permissions(self):
        """
        Scenario: The verifier agent must NEVER have write tools.
        This is a security/safety invariant.
        """
        config = agent_loader.load_agent("verifier")

        write_tools = {"write_file", "replace_string", "forget_session"}
        allowed_tools = set(config["tools"])

        assert allowed_tools.isdisjoint(write_tools), (
            f"Verifier has write tools: {allowed_tools & write_tools}"
        )
        assert config["permissions"] == "read"


# ---------------------------------------------------------------------------
# Edge Cases — Empty / Malformed Reports
# ---------------------------------------------------------------------------

class TestEdgeCasesMalformedReports:
    """Test behavior when coder reports are empty or malformed."""

    def test_empty_coder_report_still_triggers_verification(
        self, orchestrator, empty_coder_report, sample_verifier_report_pass
    ):
        """
        Scenario: Coder returns empty report → verifier should still be called.
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            mock_delegate.side_effect = [empty_coder_report, sample_verifier_report_pass]

            result = orchestrator.execute_task("Implement feature X")

            assert mock_delegate.call_count == 2
            assert mock_delegate.call_args_list[1][0][0] == "verifier"

    def test_malformed_coder_report_still_triggers_verification(
        self, orchestrator, malformed_coder_report, sample_verifier_report_pass
    ):
        """
        Scenario: Coder returns malformed report → verifier should still be called.
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            mock_delegate.side_effect = [malformed_coder_report, sample_verifier_report_pass]

            result = orchestrator.execute_task("Implement feature X")

            assert mock_delegate.call_count == 2
            assert mock_delegate.call_args_list[1][0][0] == "verifier"

    def test_verifier_handles_missing_test_section(
        self, orchestrator, malformed_coder_report
    ):
        """
        Scenario: Coder report has no test section → verifier should flag it (FAIL).
        With max_correction_retries=3, it will loop and eventually escalate.
        """
        verifier_report_no_tests = {
            "agent": "verifier",
            "status": "FAIL",
            "checks": ["No test section found in report"],
            "issues": ["Missing test coverage section"],
            "recommendations": ["Add unit, integration, and e2e tests"],
        }

        # All coder attempts still produce malformed report, verifier always FAIL
        mock_side = [
            malformed_coder_report,      # coder attempt 1
            verifier_report_no_tests,    # verifier → FAIL
            malformed_coder_report,      # coder attempt 2
            verifier_report_no_tests,    # verifier → FAIL
            malformed_coder_report,      # coder attempt 3
            verifier_report_no_tests,    # verifier → FAIL
            malformed_coder_report,      # coder attempt 4
            verifier_report_no_tests,    # verifier → FAIL → ESCALATE
        ]

        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            mock_delegate.side_effect = mock_side

            result = orchestrator.execute_task("Implement feature X")

            assert result["decision"] == "ESCALATE"
            assert result["correction_rounds"] == 3


# ---------------------------------------------------------------------------
# Edge Cases — NEEDS_REVIEW State
# ---------------------------------------------------------------------------

class TestNeedsReviewState:
    """Test the three-state decision: PASS, FAIL, NEEDS_REVIEW."""

    def test_needs_review_triggers_adjustment_request(
        self, orchestrator, sample_coder_report_pass, sample_verifier_report_needs_review
    ):
        """
        Scenario: Verifier returns NEEDS_REVIEW → Orquestrador requests adjustments.
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            adjusted_report = dict(sample_coder_report_pass)
            verifier_pass = {
                "agent": "verifier",
                "status": "PASS",
                "checks": ["All good after adjustments"],
                "issues": [],
                "recommendations": [],
            }

            mock_delegate.side_effect = [
                sample_coder_report_pass,
                sample_verifier_report_needs_review,
                adjusted_report,
                verifier_pass,
            ]

            result = orchestrator.execute_task("Implement feature X")

            assert result["decision"] == "DELIVER"
            assert result["correction_rounds"] == 1

    def test_all_three_statuses_are_handled(self, orchestrator, sample_coder_report_pass):
        """
        Scenario: Orquestrador must handle PASS, FAIL, and NEEDS_REVIEW.
        """
        with patch.object(orchestrator, "delegate_to_agent") as mock_delegate:
            for status in ["PASS", "FAIL", "NEEDS_REVIEW"]:
                verifier_report = {
                    "agent": "verifier",
                    "status": status,
                    "checks": [],
                    "issues": [],
                    "recommendations": [],
                }

                if status == "PASS":
                    mock_delegate.side_effect = [sample_coder_report_pass, verifier_report]
                    result = orchestrator.execute_task("test")
                    assert result["decision"] == "DELIVER"

                elif status == "FAIL":
                    # With max_retries=3, first FAIL triggers correction loop
                    corrected = dict(sample_coder_report_pass)
                    verifier_pass = dict(verifier_report)
                    verifier_pass["status"] = "PASS"
                    mock_delegate.side_effect = [
                        sample_coder_report_pass,
                        verifier_report,
                        corrected,
                        verifier_pass,
                    ]
                    result = orchestrator.execute_task("test")
                    assert result["decision"] == "DELIVER"

                elif status == "NEEDS_REVIEW":
                    adjusted = dict(sample_coder_report_pass)
                    verifier_pass = dict(verifier_report)
                    verifier_pass["status"] = "PASS"
                    mock_delegate.side_effect = [
                        sample_coder_report_pass,
                        verifier_report,
                        adjusted,
                        verifier_pass,
                    ]
                    result = orchestrator.execute_task("test")
                    assert result["decision"] == "DELIVER"

                mock_delegate.reset_mock()


# ---------------------------------------------------------------------------
# Infrastructure Tests
# ---------------------------------------------------------------------------

class TestVerifierInfrastructure:
    """Verify the verifier agent is properly registered and configured."""

    def test_verifier_in_agent_registry(self):
        """Verifier must be listed in available agents."""
        available = agent_loader.list_available_agents()
        ids = [a["id"] for a in available]
        assert "verifier" in ids

    def test_verifier_has_delegate_tool(self):
        """delegate_to_agent must be a registered tool."""
        assert "delegate_to_agent" in registry.tools

    def test_verifier_tools_are_read_only(self):
        """Verifier tools must not include any write operations."""
        config = agent_loader.load_agent("verifier")
        write_tools = {"write_file", "replace_string", "forget_session"}
        for tool in write_tools:
            assert tool not in config["tools"], f"Verifier should not have '{tool}'"

    def test_verifier_max_iterations_is_conservative(self):
        """Verifier max_iterations should be ≤ 10 (conservative)."""
        config = agent_loader.load_agent("verifier")
        assert config["max_iterations"] <= 10

    def test_verifier_has_verification_protocol(self):
        """Verifier instructions must contain the verification protocol."""
        config = agent_loader.load_agent("verifier")
        instructions = config["instructions"]
        assert "VERIFICATION PROTOCOL" in instructions or "Verification Protocol" in instructions
        assert "STATUS" in instructions
        assert "PASS" in instructions
        assert "FAIL" in instructions


class TestOrchestratorErrorHandling:
    """Test error handling paths in the Orchestrator."""

    def test_orchestrator_raises_when_delegate_not_registered(self):
        """
        Scenario: delegate_to_agent is not in registry → must raise RuntimeError.
        Covers lines 27-29 of infra/orchestrator.py.
        """
        with patch.dict(registry.tools, {}, clear=False):
            # Remove delegate_to_agent temporarily
            saved = registry.tools.pop("delegate_to_agent", None)
            try:
                orch = Orchestrator(max_correction_retries=3)
                with pytest.raises(RuntimeError, match="delegate_to_agent not registered"):
                    orch.delegate_to_agent("coder", "test task")
            finally:
                if saved is not None:
                    registry.tools["delegate_to_agent"] = saved
