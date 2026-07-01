import json
import os
from typing import List
from app.models import MemoryItem
from app.utils import logger

class MemoryManager:
    def __init__(self, data_dir: str = "data/memories"):
        # Resolve data path relative to the project root (assumed to be parent of app)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(base_dir, data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
    def add_memory(self, item: MemoryItem):
        """Save a new memory item to disk."""
        filepath = os.path.join(self.data_dir, f"{item.id}.json")
        try:
            with open(filepath, 'w') as f:
                json.dump(item.model_dump(), f, indent=4, default=str)
            logger.info(f"Saved memory {item.id} to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save memory {item.id}: {e}")
            raise e
            
    def get_all_memories(self) -> List[MemoryItem]:
        """Load and return all memory items from disk."""
        memories = []
        if not os.path.exists(self.data_dir):
            return memories
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        # Handle datetime parsing from string representation if needed
                        if isinstance(data.get('created_at'), str):
                            data['created_at'] = datetime.fromisoformat(data['created_at'])
                        if isinstance(data.get('updated_at'), str):
                            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                        memories.append(MemoryItem(**data))
                except Exception as e:
                    logger.debug(f"Could not load memory file {filename}: {e}")
        return memories

# Try importing datetime inside file to handle conversion if needed
from datetime import datetime

memory_manager = MemoryManager()
