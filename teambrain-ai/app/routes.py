from fastapi import APIRouter, Request, Header
from typing import List
from pydantic import BaseModel
from app.models import MemoryItem, MeetingSummary
from app.memory import memory_manager
from app.meetings import meeting_manager
from app.github_webhook import handle_github_webhook

router = APIRouter()

class MeetingCreateRequest(BaseModel):
    id: str
    title: str
    date: str
    transcript: str

@router.get("/health")
def health_check():
    """Health check endpoint to verify server status."""
    return {"status": "ok", "app": "TeamBrain AI"}

@router.post("/memories", response_model=MemoryItem)
def add_memory(item: MemoryItem):
    """Add a new item to shared team memory."""
    memory_manager.add_memory(item)
    return item

@router.get("/memories", response_model=List[MemoryItem])
def get_memories():
    """Retrieve all shared team memories."""
    return memory_manager.get_all_memories()

@router.post("/meetings", response_model=MeetingSummary)
def process_meeting(req: MeetingCreateRequest):
    """Submit a meeting transcript to summarize, extract actions, and persist."""
    return meeting_manager.process_meeting(req.id, req.title, req.date, req.transcript)

@router.post("/webhook/github")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    """Receives and validates GitHub Webhook payloads."""
    return await handle_github_webhook(request, x_hub_signature_256)
