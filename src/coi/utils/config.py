"""
Configuration management for the AI experimentation platform.

This module handles loading configuration from environment variables,
.env files, and provides defaults for the application.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


@dataclass
class AppConfig:
    """Main application configuration."""
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_debug: bool = False
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    
    # Provider Settings
    default_model: str = "gpt-3.5-turbo"
    default_temperature: float = 0.7
    default_max_tokens: int = 150
    request_timeout: int = 30
    max_retries: int = 3
    
    # Development
    environment: str = "development"


def load_config(env_file: Optional[str] = None) -> AppConfig:
    """
    Load configuration from environment variables and .env file.
    
    Args:
        env_file: Path to .env file (defaults to .env in current directory)
        
    Returns:
        AppConfig instance with loaded configuration
    """
    # Load .env file if available
    if load_dotenv and env_file is None:
        env_file = ".env"
    
    if load_dotenv and env_file and Path(env_file).exists():
        load_dotenv(env_file)
    
    return AppConfig(
        # Logging
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        log_file=os.getenv("LOG_FILE"),
        enable_debug=os.getenv("DEBUG", "false").lower() == "true",
        
        # API Keys
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        
        # Provider Settings
        default_model=os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo"),
        default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
        default_max_tokens=int(os.getenv("DEFAULT_MAX_TOKENS", "150")),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        
        # Development
        environment=os.getenv("ENVIRONMENT", "development"),
    )


def get_available_providers(config: AppConfig) -> Dict[str, bool]:
    """
    Check which providers are available based on configuration.
    
    Args:
        config: Application configuration
        
    Returns:
        Dictionary mapping provider names to availability
    """
    return {
        "openai": bool(config.openai_api_key),
        "anthropic": bool(config.anthropic_api_key),
        "azure": bool(config.azure_openai_api_key and config.azure_openai_endpoint),
    }


def validate_config(config: AppConfig) -> None:
    """
    Validate configuration and raise errors for missing required settings.
    
    Args:
        config: Application configuration to validate
        
    Raises:
        ValueError: If required configuration is missing
    """
    available_providers = get_available_providers(config)
    
    if not any(available_providers.values()):
        raise ValueError(
            "No AI providers configured. Please set at least one of: "
            "OPENAI_API_KEY, ANTHROPIC_API_KEY, or AZURE_OPENAI_API_KEY"
        )
    
    if config.default_temperature < 0 or config.default_temperature > 2:
        raise ValueError("DEFAULT_TEMPERATURE must be between 0 and 2")
    
    if config.request_timeout <= 0:
        raise ValueError("REQUEST_TIMEOUT must be positive")
    
    if config.max_retries < 0:
        raise ValueError("MAX_RETRIES must be non-negative") 