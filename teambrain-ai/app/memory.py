"""
memory.py — Data-access layer for the TeamBrain AI Memory Engine.

Encapsulates all filesystem I/O for memory records:
  - ``save``   — serialise a ``Memory`` to a JSON file.
  - ``search`` — case-insensitive substring search across every persisted memory.
  - ``load_all`` — return every memory on disk.

Design notes
~~~~~~~~~~~~
* The class is deliberately *not* instantiated as a module-level singleton.
  Instead, ``routes.py`` wires it via a FastAPI **dependency** so the storage
  path can be overridden in tests.
* Each memory is stored as ``<uuid>.json`` inside the configured data
  directory.
"""

import json
import os
from pathlib import Path
from typing import List

from app.models import Memory
from app.utils import logger


class MemoryStore:
    """Thin persistence layer that reads / writes ``Memory`` objects as JSON files."""

    def __init__(self, data_dir: str = "data/memories") -> None:
        """Initialise the store, resolving *data_dir* relative to the project root.

        Args:
            data_dir: Path to the directory where memory JSON files are stored.
                      Resolved relative to the project root (one level above ``app/``).
        """
        project_root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir: Path = Path(project_root) / data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(self, memory: Memory) -> None:
        """Persist a single ``Memory`` to disk as a JSON file.

        Args:
            memory: The fully-populated memory record to save.

        Raises:
            OSError: If the file cannot be written.
        """
        filepath: Path = self.data_dir / f"{memory.id}.json"
        try:
            filepath.write_text(
                memory.model_dump_json(indent=4),
                encoding="utf-8",
            )
            logger.info("Saved memory %s → %s", memory.id, filepath)
        except OSError:
            logger.exception("Failed to save memory %s", memory.id)
            raise

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def _load_file(self, filepath: Path) -> Memory | None:
        """Load a single JSON file and return a ``Memory``, or ``None`` on failure."""
        try:
            raw: str = filepath.read_text(encoding="utf-8")
            return Memory.model_validate_json(raw)
        except Exception:
            logger.warning("Skipping unreadable memory file: %s", filepath.name)
            return None

    def load_all(self) -> List[Memory]:
        """Return every valid ``Memory`` found in the data directory.

        Corrupt or unparseable files are logged and silently skipped so that
        one bad file never crashes the entire search.
        """
        memories: List[Memory] = []
        if not self.data_dir.exists():
            return memories

        for filepath in sorted(self.data_dir.glob("*.json")):
            memory = self._load_file(filepath)
            if memory is not None:
                memories.append(memory)
        return memories

    def search(self, query: str) -> List[Memory]:
        """Return memories whose **title** or **content** contain *query* (case-insensitive).

        Args:
            query: The search term.

        Returns:
            A (possibly empty) list of matching ``Memory`` objects.
        """
        query_lower: str = query.lower()
        return [
            m
            for m in self.load_all()
            if query_lower in m.title.lower() or query_lower in m.content.lower()
        ]
