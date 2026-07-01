"""
utils.py — Shared utilities for TeamBrain AI.

Provides:
  - A pre-configured ``logger`` instance for structured logging.
  - ``ensure_dirs()`` to guarantee that required directory trees exist at startup.
"""

import logging
import os
from typing import List

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger: logging.Logger = logging.getLogger("teambrain-ai")


# ---------------------------------------------------------------------------
# File-system helpers
# ---------------------------------------------------------------------------


def ensure_dirs(directories: List[str]) -> None:
    """Create each directory in *directories* if it does not already exist.

    Args:
        directories: A list of directory paths (absolute or relative to cwd).
    """
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info("Created directory: %s", directory)
