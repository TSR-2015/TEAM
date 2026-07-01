from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import router
from app.utils import ensure_dirs, logger

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="0.1.0"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints under /api prefix
app.include_router(router, prefix="/api")

@app.on_event("startup")
def on_startup():
    logger.info("Initializing TeamBrain AI application...")
    # Ensure standard data directories are created on launch
    ensure_dirs([
        "data/memories",
        "data/meetings",
        "data/uploads"
    ])

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "documentation": "/docs"
    }
