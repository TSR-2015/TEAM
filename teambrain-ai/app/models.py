from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MemoryItem(BaseModel):
    id: str
    content: str
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class MeetingSummary(BaseModel):
    id: str
    title: str
    date: str
    transcript: str
    summary: str
    action_items: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)

class GitHubEvent(BaseModel):
    event_type: str
    repository: str
    sender: str
    payload: dict
