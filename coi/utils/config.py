from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    @staticmethod
    def validate():
        """Validate required environment variables are set"""
        missing_keys = []
        if not Config.ANTHROPIC_API_KEY:
            missing_keys.append("ANTHROPIC_API_KEY")
        if not Config.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        # Print first few characters of keys for debugging
        print(f"Anthropic key loaded (starts with): {Config.ANTHROPIC_API_KEY[:8]}...")
        print(f"OpenAI key loaded (starts with): {Config.OPENAI_API_KEY[:8]}...")

# Validate config on import
Config.validate()