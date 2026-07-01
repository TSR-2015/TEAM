"""
git_models.py — Pydantic schemas for the TeamBrain AI Git Connector.

This module owns every data-shape that crosses the Git Connector boundary:

Request schemas
~~~~~~~~~~~~~~~
* ``GitConnectRequest`` — the ``POST /git/connect`` request body.

Response schemas
~~~~~~~~~~~~~~~~
* ``GitConnectResponse``  — the top-level response returned to the client.
* ``RepositorySummary``   — rich metadata about the connected repository.
* ``CommitInfo``          — structured representation of a single Git commit.

Internal DTOs
~~~~~~~~~~~~~
* ``ConnectResult`` — returned by ``GitService`` so the router can build the
  HTTP response without reaching into GitPython objects.

Design notes
~~~~~~~~~~~~
* **No business logic lives here** — models are pure data containers.
* ``CommitInfo`` is deliberately decoupled from ``git.Commit`` so the service
  layer performs the mapping and this module has zero GitPython dependency.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------


class GitConnectRequest(BaseModel):
    """Request body for ``POST /git/connect``.

    Attributes:
        repo_path: Absolute filesystem path to a local Git repository.
    """

    repo_path: str = Field(
        ...,
        min_length=1,
        description="Absolute path to a local Git repository.",
        examples=["C:/Users/Jeevan/Desktop/myproject"],
    )


# ---------------------------------------------------------------------------
# Commit representation
# ---------------------------------------------------------------------------


class CommitInfo(BaseModel):
    """Structured representation of a single Git commit.

    Every field is extracted from the ``git.Commit`` object by the service
    layer.  ``changed_files`` may be empty if diff extraction fails — the
    connector never crashes for informational fields.

    Attributes:
        hash:          Full 40-character SHA-1 hex digest.
        author:        Committer display name.
        email:         Committer email address.
        date:          Commit timestamp (timezone-aware ISO-8601).
        branch:        Branch name the commit was read from.
        message:       Full commit message (leading/trailing whitespace stripped).
        changed_files: List of file paths modified in this commit.
    """

    hash: str = Field(..., description="Full SHA-1 commit hash.")
    author: str = Field(..., description="Author display name.")
    email: str = Field(default="", description="Author email address.")
    date: datetime = Field(..., description="Commit timestamp (UTC).")
    branch: str = Field(..., description="Branch name.")
    message: str = Field(..., description="Commit message.")
    changed_files: List[str] = Field(
        default_factory=list,
        description="Files modified in this commit.",
    )


# ---------------------------------------------------------------------------
# Repository summary
# ---------------------------------------------------------------------------


class RepositorySummary(BaseModel):
    """Rich metadata about the connected repository.

    Attributes:
        repository_name:  Directory name of the repository.
        current_branch:   Currently checked-out branch (or ``'detached'``).
        default_branch:   Conventional default branch (``main`` / ``master``).
        latest_commit:    Short hash + subject of the most recent commit.
        total_commits:    Total number of reachable commits in the repo.
        commits_imported: Number of commits actually converted to memories.
    """

    repository_name: str
    current_branch: str
    default_branch: str
    latest_commit: str
    total_commits: int
    commits_imported: int


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------


class GitConnectResponse(BaseModel):
    """Top-level response for ``POST /git/connect``.

    Attributes:
        status:  Always ``"success"`` on a 200 response.
        summary: Detailed repository summary.
        commits: List of imported commits (structured).
    """

    status: str = "success"
    repository_name: str
    current_branch: str
    default_branch: str
    latest_commit: str
    total_commits: int
    commits_imported: int


# ---------------------------------------------------------------------------
# Internal DTO (service → router)
# ---------------------------------------------------------------------------


class ConnectResult(BaseModel):
    """Internal value object returned by ``GitService.connect()``.

    Carries everything the router needs to build a ``GitConnectResponse``
    without importing GitPython types.

    Attributes:
        summary: Repository-level metadata.
        commits: The structured commit records that were imported.
    """

    summary: RepositorySummary
    commits: List[CommitInfo]
