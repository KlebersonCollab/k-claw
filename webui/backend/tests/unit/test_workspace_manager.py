"""Unit tests for workspace manager."""

import pytest
from pathlib import Path

from models import WorkspaceCreate
from workspace_manager import (
    create_workspace,
    list_workspaces,
    get_workspace,
    delete_workspace,
    list_workspace_files,
    workspace_exists,
    WORKSPACES_DIR,
)


class TestCreateWorkspace:
    """Tests for create_workspace function."""

    def test_create_basic_workspace(self, clean_workspaces):
        """Test creating a basic workspace."""
        data = WorkspaceCreate(name="myproject", description="My project")
        result = create_workspace(data)

        assert result.id == "myproject"
        assert result.name == "myproject"
        assert result.agents_md_exists is True
        assert result.file_count >= 1

    def test_creates_directory_structure(self, clean_workspaces):
        """Test that workspace creates proper directory structure."""
        data = WorkspaceCreate(name="structured")
        result = create_workspace(data)

        ws_path = WORKSPACES_DIR / "structured"
        assert ws_path.exists()
        assert (ws_path / "src").is_dir()
        assert (ws_path / "tests").is_dir()
        assert (ws_path / "tests" / "unit").is_dir()
        assert (ws_path / "tests" / "integration").is_dir()
        assert (ws_path / "tests" / "e2e").is_dir()
        assert (ws_path / "tests" / "edge_cases").is_dir()

    def test_creates_agents_md(self, clean_workspaces):
        """Test that workspace creates AGENTS.md file."""
        data = WorkspaceCreate(name="agents-test")
        create_workspace(data)

        agents_md = WORKSPACES_DIR / "agents-test" / "AGENTS.md"
        assert agents_md.exists()
        content = agents_md.read_text()
        assert "agents-test" in content
        assert "Agent Catalog" in content

    def test_creates_readme(self, clean_workspaces):
        """Test that workspace creates README.md file."""
        data = WorkspaceCreate(name="readme-test", description="Test desc")
        create_workspace(data)

        readme = WORKSPACES_DIR / "readme-test" / "README.md"
        assert readme.exists()
        content = readme.read_text()
        assert "readme-test" in content
        assert "Test desc" in content

    def test_creates_pyproject_toml(self, clean_workspaces):
        """Test that workspace creates pyproject.toml file."""
        data = WorkspaceCreate(name="pyproject-test")
        create_workspace(data)

        pyproject = WORKSPACES_DIR / "pyproject-test" / "pyproject.toml"
        assert pyproject.exists()
        content = pyproject.read_text()
        assert "pyproject-test" in content

    def test_duplicate_workspace_raises_error(self, clean_workspaces):
        """Test that creating duplicate workspace raises ValueError."""
        data = WorkspaceCreate(name="duplicate")
        create_workspace(data)

        with pytest.raises(ValueError, match="already exists"):
            create_workspace(data)

    def test_name_converted_to_lowercase(self, clean_workspaces):
        """Test that workspace name is converted to lowercase."""
        data = WorkspaceCreate(name="MyProject")
        result = create_workspace(data)

        assert result.id == "myproject"
        assert (WORKSPACES_DIR / "myproject").exists()


class TestListWorkspaces:
    """Tests for list_workspaces function."""

    def test_empty_list(self, clean_workspaces):
        """Test listing when no workspaces exist."""
        result = list_workspaces()
        assert result == []

    def test_list_single_workspace(self, sample_workspace):
        """Test listing single workspace."""
        result = list_workspaces()
        assert len(result) == 1
        assert result[0].id == "test-project"

    def test_list_multiple_workspaces(self, multiple_workspaces):
        """Test listing multiple workspaces."""
        result = list_workspaces()
        assert len(result) == 3
        ids = [ws.id for ws in result]
        assert "project-alpha" in ids
        assert "project-beta" in ids
        assert "project-gamma" in ids

    def test_list_sorted_alphabetically(self, clean_workspaces):
        """Test that workspaces are sorted alphabetically."""
        for name in ["zebra", "alpha", "mango"]:
            create_workspace(WorkspaceCreate(name=name))

        result = list_workspaces()
        ids = [ws.id for ws in result]
        assert ids == ["alpha", "mango", "zebra"]


class TestGetWorkspace:
    """Tests for get_workspace function."""

    def test_get_existing_workspace(self, sample_workspace):
        """Test getting an existing workspace."""
        result = get_workspace("test-project")
        assert result.id == "test-project"
        assert result.agents_md_exists is True

    def test_get_nonexistent_workspace_raises_error(self, clean_workspaces):
        """Test that getting nonexistent workspace raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            get_workspace("nonexistent")


class TestDeleteWorkspace:
    """Tests for delete_workspace function."""

    def test_delete_existing_workspace(self, sample_workspace):
        """Test deleting an existing workspace."""
        result = delete_workspace("test-project")
        assert result is True
        assert not (WORKSPACES_DIR / "test-project").exists()

    def test_delete_nonexistent_workspace_raises_error(self, clean_workspaces):
        """Test that deleting nonexistent workspace raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            delete_workspace("nonexistent")

    def test_delete_removes_all_files(self, clean_workspaces):
        """Test that deletion removes all workspace files."""
        create_workspace(WorkspaceCreate(name="to-delete"))
        assert (WORKSPACES_DIR / "to-delete").exists()

        delete_workspace("to-delete")
        assert not (WORKSPACES_DIR / "to-delete").exists()


class TestWorkspaceExists:
    """Tests for workspace_exists function."""

    def test_existing_workspace(self, sample_workspace):
        """Test checking existing workspace."""
        assert workspace_exists("test-project") is True

    def test_nonexistent_workspace(self, clean_workspaces):
        """Test checking nonexistent workspace."""
        assert workspace_exists("nonexistent") is False


class TestListWorkspaceFiles:
    """Tests for list_workspace_files function."""

    def test_list_root_files(self, sample_workspace):
        """Test listing files in workspace root."""
        files = list_workspace_files("test-project")
        names = [f.name for f in files]
        assert "AGENTS.md" in names
        assert "README.md" in names
        assert "src" in names
        assert "tests" in names

    def test_list_src_subdirectory(self, sample_workspace):
        """Test listing files in src subdirectory."""
        files = list_workspace_files("test-project", "src")
        # src should be empty initially
        assert files == []

    def test_skip_hidden_files(self, clean_workspaces):
        """Test that hidden files are skipped."""
        create_workspace(WorkspaceCreate(name="hidden-test"))
        # Create a hidden file
        hidden = WORKSPACES_DIR / "hidden-test" / ".hidden"
        hidden.write_text("secret")

        files = list_workspace_files("hidden-test")
        names = [f.name for f in files]
        assert ".hidden" not in names

    def test_skip_pycache(self, clean_workspaces):
        """Test that __pycache__ is skipped."""
        create_workspace(WorkspaceCreate(name="pycache-test"))
        # Create __pycache__
        pycache = WORKSPACES_DIR / "pycache-test" / "__pycache__"
        pycache.mkdir()

        files = list_workspace_files("pycache-test")
        names = [f.name for f in files]
        assert "__pycache__" not in names

    def test_nonexistent_workspace_raises_error(self, clean_workspaces):
        """Test that listing files of nonexistent workspace raises error."""
        with pytest.raises(FileNotFoundError, match="not found"):
            list_workspace_files("nonexistent")

    def test_file_entry_properties(self, sample_workspace):
        """Test that file entries have correct properties."""
        files = list_workspace_files("test-project")
        for f in files:
            assert isinstance(f.is_dir, bool)
            assert isinstance(f.size, int)
            assert f.size >= 0
            if f.is_dir:
                assert f.size == 0
