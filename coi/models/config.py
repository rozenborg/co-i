from dataclasses import dataclass
from typing import Dict

@dataclass
class ModelInfo:
    identifier: str
    display_name: str
    provider: str

AVAILABLE_MODELS = {
    "claude-3-sonnet": ModelInfo(
        identifier="claude-3-sonnet-20240229",
        display_name="Claude 3 Sonnet",
        provider="anthropic"
    ),
    "gpt-4": ModelInfo(
        identifier="gpt-4-turbo-preview",
        display_name="GPT-4 Turbo",
        provider="openai"
    )
}