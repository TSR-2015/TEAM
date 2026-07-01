"""
git_connector.py — Local Git Repository Connector for TeamBrain AI.

Reads the commit history of a local Git repository and converts each commit
into a ``Memory`` record that is persisted via the existing Memory Engine.

Public API
~~~~~~~~~~
* ``GitConnector.connect(repo_path)`` — the single entry-point called by the
  route handler.  Validates the path, opens the repo, extracts up to 100
  commits, converts each to a ``Memory``, saves them, and returns a summary.

Design notes
~~~~~~~~~~~~
* Depends on ``MemoryStore`` (injected via constructor) so the module never
  duplicates persistence logic.
* All Git operations are read-only — nothing is written to the user's repo.
* ``git.InvalidGitRepositoryError`` and ``git.NoSuchPathError`` are caught
  and re-raised as domain-specific ``ValueError`` exceptions so the route
  layer can map them to HTTP 400 without leaking GitPython internals.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import git  # GitPython

from app.memory import MemoryStore
from app.models import Memory
from app.utils import logger

# Maximum number of commits to import per connection request.
MAX_COMMITS: int = 100


# ---------------------------------------------------------------------------
# Result DTO
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConnectResult:
    """Value object returned after a successful repository connection."""

    repository: str
    commits_imported: int


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


class GitConnector:
    """Reads a local Git repository and converts commits into TeamBrain memories.

    Args:
        store: An existing ``MemoryStore`` instance used to persist the
               generated ``Memory`` records.
    """

    def __init__(self, store: MemoryStore) -> None:
        self._store: MemoryStore = store

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def connect(self, repo_path: str) -> ConnectResult:
        """Validate *repo_path*, extract commits, and save them as memories.

        Args:
            repo_path: Absolute or relative filesystem path to a local Git
                       repository.

        Returns:
            A ``ConnectResult`` containing the repository name and the number
            of commits that were imported.

        Raises:
            ValueError: If the path does not exist or is not a Git repository.
            OSError:    If a memory file cannot be written to disk.
        """
        repo: git.Repo = self._open_repo(repo_path)
        repo_name: str = Path(repo.working_dir).name

        logger.info(
            "Connected to repository '%s' at %s", repo_name, repo.working_dir
        )

        commits: List[git.Commit] = self._extract_commits(repo)
        memories: List[Memory] = [
            self._commit_to_memory(c, repo_name) for c in commits
        ]

        for memory in memories:
            self._store.save(memory)

        logger.info(
            "Imported %d commits from '%s'", len(memories), repo_name
        )
        return ConnectResult(repository=repo_name, commits_imported=len(memories))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _open_repo(repo_path: str) -> git.Repo:
        """Open the repository at *repo_path*, raising ``ValueError`` on failure.

        Raises:
            ValueError: With a human-readable message if the path is missing
                        or not a valid Git repository.
        """
        path = Path(repo_path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {repo_path}")

        try:
            return git.Repo(repo_path)
        except git.InvalidGitRepositoryError as exc:
            raise ValueError(
                f"Not a valid Git repository: {repo_path}"
            ) from exc
        except git.NoSuchPathError as exc:
            raise ValueError(
                f"Path does not exist: {repo_path}"
            ) from exc

    @staticmethod
    def _extract_commits(repo: git.Repo) -> List[git.Commit]:
        """Return the latest ``MAX_COMMITS`` commits from *repo*.

        Iterates over the active branch.  If the repository is empty (no
        commits) an empty list is returned.
        """
        try:
            return list(repo.iter_commits(max_count=MAX_COMMITS))
        except ValueError:
            # Raised when HEAD points to an unborn branch (empty repo).
            logger.warning("Repository has no commits.")
            return []

    @staticmethod
    def _get_active_branch(repo: git.Repo) -> str:
        """Return the name of the currently checked-out branch, or ``'detached'``."""
        try:
            return str(repo.active_branch)
        except TypeError:
            # Detached HEAD state.
            return "detached"

    @staticmethod
    def _get_changed_files(commit: git.Commit) -> List[str]:
        """Return filenames modified in *commit*.

        Compares against the first parent.  For the initial (root) commit the
        full tree is listed instead.
        """
        try:
            if commit.parents:
                diffs = commit.diff(commit.parents[0])
            else:
                # Root commit — diff against the empty tree.
                diffs = commit.diff(git.NULL_TREE)
            return [d.a_path or d.b_path for d in diffs]
        except Exception:
            # Gracefully degrade — file list is informational, not critical.
            return []

    def _commit_to_memory(self, commit: git.Commit, repo_name: str) -> Memory:
        """Convert a single ``git.Commit`` into a ``Memory`` record.

        The content field is a human-readable block that includes the commit
        hash, message, author, email, date, changed files, and branch.
        """
        short_hash: str = commit.hexsha[:8]
        message: str = commit.message.strip()
        author_name: str = commit.author.name or "Unknown"
        author_email: str = commit.author.email or ""
        committed_date: str = commit.committed_datetime.isoformat()
        branch: str = self._get_active_branch(commit.repo)
        changed_files: List[str] = self._get_changed_files(commit)

        content_lines: List[str] = [
            message,
            "",
            f"Commit: {commit.hexsha}",
            f"Author: {author_name} <{author_email}>",
            f"Date:   {committed_date}",
            f"Branch: {branch}",
        ]
        if changed_files:
            content_lines.append(f"Files changed: {', '.join(changed_files)}")

        return Memory(
            title=f"Git Commit: {message[:80]}",
            content="\n".join(content_lines),
            source="git",
            type="commit",
            author=author_name,
            tags=["git", repo_name, "commit"],
        )
