"""
models.py — Pydantic schemas for TeamBrain AI Memory Engine.

Defines three models:
  - MemoryCreate : the request body for adding a memory (user-supplied fields only).
  - Memory       : the full persisted memory record (includes server-generated id & timestamp).
  - MemoryAddResponse : the response returned after successfully adding a memory.
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    """Schema for the incoming request when a user adds a new memory.

    The ``id`` and ``timestamp`` fields are intentionally absent here
    because the server generates them automatically.
    """

    title: str = Field(..., min_length=1, description="Short title of the memory.")
    content: str = Field(..., min_length=1, description="Full content / description.")
    source: str = Field(
        ...,
        min_length=1,
        description="Origin of the memory (e.g. 'meeting', 'github', 'document').",
    )
    type: str = Field(
        ...,
        min_length=1,
        description="Category type (e.g. 'meeting', 'commit', 'task').",
    )
    author: str = Field(..., min_length=1, description="Author / contributor name.")
    tags: List[str] = Field(
        default_factory=list,
        description="Optional list of tags for categorisation.",
    )


class Memory(BaseModel):
    """Full memory record persisted to disk.

    Extends the user-supplied fields with a server-generated UUID ``id``
    and an ISO-8601 ``timestamp``.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier (UUID4).")
    title: str
    content: str
    source: str
    type: str
    author: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of when the memory was created.",
    )
    tags: List[str] = Field(default_factory=list)


class MemoryAddResponse(BaseModel):
    """Response returned after a memory is successfully persisted."""

    status: str = "success"
    memory_id: str
