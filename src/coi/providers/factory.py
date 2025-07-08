"""
Provider factory for creating AI provider instances.

This module provides a factory pattern for creating provider instances
based on configuration and provider name.
"""

from typing import Dict, Type, Optional
import logging

from .base import BaseProvider, ProviderConfig
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from ..utils.config import AppConfig

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating AI provider instances."""
    
    # Registry of available providers
    _providers: Dict[str, Type[BaseProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    
    @classmethod
    def create_provider(
        cls, 
        provider_name: str, 
        config: AppConfig
    ) -> BaseProvider:
        """
        Create a provider instance.
        
        Args:
            provider_name: Name of the provider (openai, anthropic, etc.)
            config: Application configuration
            
        Returns:
            Initialized provider instance
            
        Raises:
            ValueError: If provider is not available or not configured
        """
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")
        
        # Create provider-specific config
        provider_config = cls._create_provider_config(provider_name, config)
        
        # Create and return provider instance
        provider_class = cls._providers[provider_name]
        return provider_class(provider_config)
    
    @classmethod
    def _create_provider_config(
        cls, 
        provider_name: str, 
        config: AppConfig
    ) -> ProviderConfig:
        """Create provider-specific configuration."""
        
        if provider_name == "openai":
            if not config.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return ProviderConfig(
                api_key=config.openai_api_key,
                timeout=config.request_timeout,
                max_retries=config.max_retries
            )
        
        elif provider_name == "anthropic":
            if not config.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return ProviderConfig(
                api_key=config.anthropic_api_key,
                timeout=config.request_timeout,
                max_retries=config.max_retries
            )
        
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    @classmethod
    def get_available_providers(cls, config: AppConfig) -> Dict[str, bool]:
        """
        Get available providers based on configuration.
        
        Args:
            config: Application configuration
            
        Returns:
            Dictionary mapping provider names to availability
        """
        return {
            "openai": bool(config.openai_api_key),
            "anthropic": bool(config.anthropic_api_key),
        }
    
    @classmethod
    def get_default_provider(cls, config: AppConfig) -> str:
        """
        Get the default provider based on configuration.
        
        Args:
            config: Application configuration
            
        Returns:
            Name of the default provider
            
        Raises:
            ValueError: If no providers are available
        """
        available = cls.get_available_providers(config)
        
        if not any(available.values()):
            raise ValueError("No providers are configured")
        
        # Prefer OpenAI if available, otherwise use first available
        if available["openai"]:
            return "openai"
        elif available["anthropic"]:
            return "anthropic"
        else:
            # Return first available provider
            return next(name for name, available in available.items() if available)