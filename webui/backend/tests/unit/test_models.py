"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from models import WorkspaceCreate, WorkspaceResponse, MissionRequest, LogEntry, FileEntry


class TestWorkspaceCreate:
    """Tests for WorkspaceCreate model."""

    def test_valid_name_simple(self):
        """Test creating workspace with simple name."""
        data = WorkspaceCreate(name="myproject")
        assert data.name == "myproject"

    def test_valid_name_with_hyphens(self):
        """Test creating workspace with hyphens."""
        data = WorkspaceCreate(name="my-project")
        assert data.name == "my-project"

    def test_valid_name_with_underscores(self):
        """Test creating workspace with underscores."""
        data = WorkspaceCreate(name="my_project")
        assert data.name == "my_project"

    def test_valid_name_with_numbers(self):
        """Test creating workspace with numbers."""
        data = WorkspaceCreate(name="project123")
        assert data.name == "project123"

    def test_name_converted_to_lowercase(self):
        """Test that name is converted to lowercase."""
        data = WorkspaceCreate(name="MyProject")
        assert data.name == "myproject"

    def test_name_stripped(self):
        """Test that name whitespace is stripped (validator rejects leading/trailing spaces)."""
        # The validator checks the raw input, so spaces cause rejection
        with pytest.raises(ValidationError):
            WorkspaceCreate(name="  myproject  ")

    def test_name_with_description(self):
        """Test creating workspace with description."""
        data = WorkspaceCreate(name="myproject", description="My test project")
        assert data.description == "My test project"

    def test_name_empty_rejected(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError):
            WorkspaceCreate(name="")

    def test_name_with_spaces_rejected(self):
        """Test that name with spaces is rejected."""
        with pytest.raises(ValidationError):
            WorkspaceCreate(name="my project")

    def test_name_with_special_chars_rejected(self):
        """Test that name with special characters is rejected."""
        with pytest.raises(ValidationError):
            WorkspaceCreate(name="my@project!")

    def test_name_too_long_rejected(self):
        """Test that name exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            WorkspaceCreate(name="a" * 101)

    def test_description_too_long_rejected(self):
        """Test that description exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            WorkspaceCreate(name="myproject", description="a" * 501)


class TestWorkspaceResponse:
    """Tests for WorkspaceResponse model."""

    def test_create_response(self):
        """Test creating a workspace response."""
        response = WorkspaceResponse(
            id="myproject",
            name="myproject",
            description="Test project",
            created_at="2026-01-17T10:00:00",
            file_count=5,
            agents_md_exists=True,
        )
        assert response.id == "myproject"
        assert response.file_count == 5
        assert response.agents_md_exists is True

    def test_defaults(self):
        """Test default values."""
        response = WorkspaceResponse(
            id="test",
            name="test",
            description="",
            created_at="2026-01-17T10:00:00",
        )
        assert response.file_count == 0
        assert response.agents_md_exists is False


class TestMissionRequest:
    """Tests for MissionRequest model."""

    def test_valid_mission(self):
        """Test creating a valid mission request."""
        data = MissionRequest(mission="Create a REST API", agent_id="coder")
        assert data.mission == "Create a REST API"
        assert data.agent_id == "coder"

    def test_default_agent(self):
        """Test default agent is coder."""
        data = MissionRequest(mission="Create a REST API")
        assert data.agent_id == "coder"

    def test_empty_mission_rejected(self):
        """Test that empty mission is rejected."""
        with pytest.raises(ValidationError):
            MissionRequest(mission="")

    def test_mission_too_long_rejected(self):
        """Test that mission exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            MissionRequest(mission="a" * 5001)

    def test_different_agents(self):
        """Test different agent types."""
        for agent in ["coder", "researcher", "verifier"]:
            data = MissionRequest(mission="Test mission", agent_id=agent)
            assert data.agent_id == agent


class TestLogEntry:
    """Tests for LogEntry model."""

    def test_create_log_entry(self):
        """Test creating a log entry."""
        entry = LogEntry(
            timestamp="2026-01-17T10:00:00",
            level="INFO",
            message="Test message",
            source="system",
        )
        assert entry.level == "INFO"
        assert entry.message == "Test message"
        assert entry.source == "system"

    def test_default_level(self):
        """Test default log level."""
        entry = LogEntry(
            timestamp="2026-01-17T10:00:00",
            message="Test message",
        )
        assert entry.level == "INFO"
        assert entry.source == "system"

    def test_error_level(self):
        """Test error log level."""
        entry = LogEntry(
            timestamp="2026-01-17T10:00:00",
            level="ERROR",
            message="Error occurred",
            source="coder",
        )
        assert entry.level == "ERROR"


class TestFileEntry:
    """Tests for FileEntry model."""

    def test_create_file_entry(self):
        """Test creating a file entry."""
        entry = FileEntry(name="test.py", path="src/test.py", is_dir=False, size=1024)
        assert entry.name == "test.py"
        assert entry.is_dir is False
        assert entry.size == 1024

    def test_create_dir_entry(self):
        """Test creating a directory entry."""
        entry = FileEntry(name="src", path="src", is_dir=True)
        assert entry.is_dir is True
        assert entry.size == 0

    def test_default_size(self):
        """Test default size is 0."""
        entry = FileEntry(name="test.py", path="test.py", is_dir=False)
        assert entry.size == 0
