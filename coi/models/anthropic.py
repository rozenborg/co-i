from typing import Optional
import anthropic
from .base import LLMBase
from ..utils.config import Config

class ClaudeHandler(LLMBase):
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = "claude-3-sonnet-20240229"
        
    async def send_message(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Send a message to Claude and get response"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": message}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def create_conversation(self) -> str:
        """Create a new conversation ID"""
        # For Claude we don't need persistent conversation IDs
        # but we implement this for consistency
        return "claude-conversation"