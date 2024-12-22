from typing import Optional
from openai import OpenAI
from .base import LLMBase
from ..utils.config import Config

class OpenAIHandler(LLMBase):
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4-turbo-preview"
        
    async def send_message(self, message: str, conversation_id: Optional[str] = None) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": message}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def create_conversation(self) -> str:
        return "openai-conversation"