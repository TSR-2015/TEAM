"""
main.py — FastAPI application entry-point for TeamBrain AI.

Responsibilities:
  1. Create the ``FastAPI`` application instance.
  2. Register CORS middleware (permissive for hackathon development).
  3. Mount the memory router from ``routes.py``.
  4. Ensure required data directories exist on startup.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.git_routes import router as git_router
from app.routes import router as memory_router
from app.utils import ensure_dirs, logger

# ---------------------------------------------------------------------------
# Application constants (will move to a config module later)
# ---------------------------------------------------------------------------
APP_NAME: str = "TeamBrain AI"
APP_VERSION: str = "0.1.0"


# ---------------------------------------------------------------------------
# Lifespan — replaces the deprecated @app.on_event("startup") pattern
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle hook.

    On startup the required data directories are created if they do not
    already exist.
    """
    logger.info("Initializing %s v%s …", APP_NAME, APP_VERSION)
    ensure_dirs(["data/memories"])
    yield  # ← application runs while suspended here
    logger.info("Shutting down %s.", APP_NAME)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

# Permissive CORS for local / hackathon development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(memory_router)
app.include_router(git_router)


# ---------------------------------------------------------------------------
# Root health-check
# ---------------------------------------------------------------------------


@app.get("/")
def root() -> dict:
    """Root endpoint — basic health-check / welcome message."""
    return {
        "message": f"Welcome to {APP_NAME}!",
        "version": APP_VERSION,
        "docs": "/docs",
    }
