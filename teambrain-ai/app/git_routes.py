"""
git_routes.py — FastAPI router for the TeamBrain AI Git Connector.

Endpoints
~~~~~~~~~
* ``POST /git/connect`` — connect a local Git repository and import its
  commit history as TeamBrain memories.

Dependencies are injected via ``Depends()`` so the route handler remains
thin, testable, and free of global state.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.git_connector import GitConnector
from app.memory import MemoryStore
from app.utils import logger

router = APIRouter(prefix="/git", tags=["Git"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class GitConnectRequest(BaseModel):
    """Request body for ``POST /git/connect``."""

    repo_path: str = Field(
        ...,
        min_length=1,
        description="Absolute path to a local Git repository.",
    )


class GitConnectResponse(BaseModel):
    """Response returned after commits have been imported."""

    status: str = "success"
    repository: str
    commits_imported: int


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


def get_memory_store() -> MemoryStore:
    """Provide a ``MemoryStore`` instance for the connector to persist memories."""
    return MemoryStore()


def get_git_connector(
    store: MemoryStore = Depends(get_memory_store),
) -> GitConnector:
    """Provide a ``GitConnector`` wired to the current ``MemoryStore``."""
    return GitConnector(store=store)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/connect", response_model=GitConnectResponse, status_code=200)
def connect_repository(
    payload: GitConnectRequest,
    connector: GitConnector = Depends(get_git_connector),
) -> GitConnectResponse:
    """Connect to a local Git repository and import its commit history.

    Validates that the path exists and is a valid Git repo, extracts the
    latest 100 commits, converts each into a ``Memory``, and saves them
    via the existing Memory Engine.

    Returns:
        A summary containing the repository name and the number of commits
        imported.

    Raises:
        HTTPException 400: If the path is invalid or not a Git repository.
        HTTPException 500: If an unexpected error occurs during import.
    """
    try:
        result = connector.connect(payload.repo_path)
        return GitConnectResponse(
            repository=result.repository,
            commits_imported=result.commits_imported,
        )
    except ValueError as exc:
        logger.warning("Git connect failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OSError as exc:
        logger.exception("Failed to persist git memories")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save memories: {exc}",
        ) from exc
