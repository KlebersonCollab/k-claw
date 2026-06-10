"""Pydantic models for WebUI API."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class WorkspaceCreate(BaseModel):
    """Model for creating a new workspace."""

    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")
    description: Optional[str] = Field(default="", max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate workspace name (alphanumeric, hyphens, underscores only)."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Name must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v.lower().strip()


class WorkspaceResponse(BaseModel):
    """Model for workspace response."""

    id: str
    name: str
    description: str
    created_at: str
    file_count: int = 0
    agents_md_exists: bool = False


class MissionRequest(BaseModel):
    """Model for sending a mission to an agent."""

    mission: str = Field(..., min_length=1, max_length=5000, description="Mission description")
    agent_id: str = Field(default="coder", description="Agent to execute the mission")


class LogEntry(BaseModel):
    """Model for log entries."""

    timestamp: str
    level: str = "INFO"
    message: str
    source: str = "system"


class FileEntry(BaseModel):
    """Model for file entries."""

    name: str
    path: str
    is_dir: bool
    size: int = 0
