from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class LLMBase(ABC):
    """Base class for LLM interactions"""
    
    @abstractmethod
    async def send_message(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Send a message to the LLM and get response"""
        pass
    
    @abstractmethod
    def create_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        pass