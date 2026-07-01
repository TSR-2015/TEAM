import json
import os
from app.models import MeetingSummary
from app.ai import ai_service
from app.utils import logger

class MeetingManager:
    def __init__(self, data_dir: str = "data/meetings"):
        # Resolve data path relative to the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(base_dir, data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
    def process_meeting(self, meeting_id: str, title: str, date: str, transcript: str) -> MeetingSummary:
        """Processes a meeting transcript, generates a summary, and stores it."""
        logger.info(f"Processing meeting: {title} ({date})")
        
        # Generate summary using the AI service
        summary_text = ai_service.generate_summary(transcript)
        
        # In a real app, action items and key points could also be extracted using AI.
        # Here we populate standard structured fields.
        summary = MeetingSummary(
            id=meeting_id,
            title=title,
            date=date,
            transcript=transcript,
            summary=summary_text,
            action_items=["Follow up on design guidelines", "Test initial webhook payload"],
            key_points=["Reviewed teambrain-ai project architecture", "Set up file structure & config loader"]
        )
        
        self.save_summary(summary)
        return summary
        
    def save_summary(self, summary: MeetingSummary):
        """Saves a meeting summary object to disk."""
        filepath = os.path.join(self.data_dir, f"{summary.id}.json")
        try:
            with open(filepath, 'w') as f:
                json.dump(summary.model_dump(), f, indent=4, default=str)
            logger.info(f"Saved meeting summary {summary.id} to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save meeting summary {summary.id}: {e}")
            raise e

meeting_manager = MeetingManager()
