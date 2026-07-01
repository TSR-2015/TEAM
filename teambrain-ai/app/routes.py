"""
routes.py — FastAPI router for the TeamBrain AI Memory Engine.

Endpoints
~~~~~~~~~
* ``POST /memory/add``     — ingest a new memory record.
* ``GET  /memory/search``  — full-text substring search across memories.
* ``GET  /memory/all``     — return every stored memory (convenience / debug).

The ``MemoryStore`` is injected via ``Depends(get_memory_store)`` so that:
  1. There are **no module-level global variables**.
  2. Tests can easily override the dependency to point at a temp directory.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.memory import MemoryStore
from app.models import Memory, MemoryAddResponse, MemoryCreate

router = APIRouter(prefix="/memory", tags=["Memory"])


# ---------------------------------------------------------------------------
# Dependency — provides a MemoryStore to each request handler
# ---------------------------------------------------------------------------


def get_memory_store() -> MemoryStore:
    """FastAPI dependency that yields a ``MemoryStore`` instance.

    By default it uses the standard ``data/memories`` directory.
    Override this dependency in tests to use a temporary path.
    """
    return MemoryStore()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/add", response_model=MemoryAddResponse, status_code=201)
def add_memory(
    payload: MemoryCreate,
    store: MemoryStore = Depends(get_memory_store),
) -> MemoryAddResponse:
    """Ingest a new memory.

    Accepts user-supplied fields (title, content, source, type, author, tags),
    auto-generates ``id`` (UUID4) and ``timestamp`` (UTC now), persists the
    record as a JSON file, and returns the generated ``memory_id``.
    """
    try:
        memory = Memory(**payload.model_dump())
        store.save(memory)
        return MemoryAddResponse(memory_id=str(memory.id))
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to persist memory: {exc}",
        ) from exc


@router.get("/search", response_model=List[Memory])
def search_memories(
    q: str = Query(..., min_length=1, description="Search term."),
    store: MemoryStore = Depends(get_memory_store),
) -> List[Memory]:
    """Search stored memories by a substring match on **title** and **content**.

    Returns all memories where the query string appears (case-insensitive).
    """
    results: List[Memory] = store.search(q)
    return results


@router.get("/all", response_model=List[Memory])
def list_all_memories(
    store: MemoryStore = Depends(get_memory_store),
) -> List[Memory]:
    """Return every stored memory.  Useful for debugging and admin dashboards."""
    return store.load_all()
