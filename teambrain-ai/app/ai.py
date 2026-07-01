import os
from openai import OpenAI
import google.generativeai as genai
from app.config import settings
from app.utils import logger

class AIService:
    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
            
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to configure Gemini: {e}")
            
    def generate_summary(self, text: str) -> str:
        """Generates a summary of the provided text."""
        logger.info("Generating summary via AI service...")
        
        # Fallback to OpenAI if configured
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                        {"role": "user", "content": f"Please provide a clean, structured summary of the following text:\n\n{text}"}
                    ]
                )
                return response.choices[0].message.content or "No summary returned."
            except Exception as e:
                logger.error(f"OpenAI summary generation failed: {e}")
                
        # Fallback to Gemini if configured
        if settings.GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Please provide a clean, structured summary of the following text:\n\n{text}")
                return response.text
            except Exception as e:
                logger.error(f"Gemini summary generation failed: {e}")
                
        # Basic mock output if APIs are not configured
        return f"[Mock Summary] Summary of the text (APIs not configured):\n{text[:100]}..."

ai_service = AIService()
