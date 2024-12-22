from typing import Dict, List, Tuple
import asyncio
from .base import LLMBase

class ModelConversation:
    def __init__(self, model1: LLMBase, model2: LLMBase, 
                 initial_prompt: str, num_turns: int,
                 progress_callback=None):
        self.model1 = model1
        self.model2 = model2
        self.initial_prompt = initial_prompt
        self.num_turns = num_turns
        self.progress_callback = progress_callback
        self.conversation_history: List[Tuple[str, str]] = []  # (speaker, message)
    
    async def run_conversation(self):
        # Start with initial prompt to model1
        current_prompt = self.initial_prompt
        current_speaker = "Model 1"
        
        for turn in range(self.num_turns * 2):  # *2 because each turn involves both models
            # Determine current model
            current_model = self.model1 if current_speaker == "Model 1" else self.model2
            
            # Get response
            response = await current_model.send_message(current_prompt)
            self.conversation_history.append((current_speaker, response))
            
            # Update callback if provided
            if self.progress_callback:
                self.progress_callback(current_speaker, response)
            
            # Prepare for next turn
            current_prompt = response
            current_speaker = "Model 2" if current_speaker == "Model 1" else "Model 1"
        
        return self.conversation_history