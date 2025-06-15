"""
Base provider interface for AI experimentation platform.

This module defines the abstract base class that all AI providers must implement
to ensure consistent behavior across different AI services.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """
    Standard response container for AI provider outputs.
    
    This class provides a consistent interface for AI responses regardless
    of the underlying provider implementation.
    """
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    cost_usd: float
    provider: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProviderConfig:
    """Configuration container for AI providers."""
    api_key: str
    base_url: Optional[str] = None
    organization: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    extra_headers: Optional[Dict[str, str]] = None


class BaseProvider(ABC):
    """
    Abstract base class for all AI providers.
    
    This class defines the interface that all AI providers must implement
    to work with the experimentation platform.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize the provider with configuration.
        
        Args:
            config: Provider configuration containing API keys and settings
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate the provider configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate a response using the AI provider.
        
        Args:
            prompt: The input prompt to send to the AI model
            model: The specific model to use for generation
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIResponse: Standardized response object
            
        Raises:
            ProviderError: If the API call fails
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for this provider.
        
        Returns:
            List of model names supported by this provider
        """
        pass
    
    @abstractmethod
    def estimate_cost(
        self, 
        prompt: str, 
        model: str, 
        max_tokens: Optional[int] = None
    ) -> float:
        """
        Estimate the cost of a generation request.
        
        Args:
            prompt: The input prompt
            model: The model to use
            max_tokens: Maximum tokens to generate
            
        Returns:
            Estimated cost in USD
        """
        pass
    
    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        return self.__class__.__name__.replace("Provider", "").lower()


class ProviderError(Exception):
    """Base exception for provider-related errors."""
    
    def __init__(self, message: str, provider: str, model: Optional[str] = None):
        self.provider = provider
        self.model = model
        super().__init__(f"[{provider}] {message}")


class RateLimitError(ProviderError):
    """Raised when provider rate limits are exceeded."""
    pass


class InvalidConfigError(ProviderError):
    """Raised when provider configuration is invalid."""
    pass


class ModelNotFoundError(ProviderError):
    """Raised when requested model is not available."""
    pass 