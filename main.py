#!/usr/bin/env python3
"""
AI Experimentation Platform - Main Entry Point

This script demonstrates the structured approach to AI API integration
with proper error handling, logging, and configuration management.

Run this to test the refactored codebase with sound coding practices.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from coi.utils.config import load_config, validate_config, get_available_providers
from coi.utils.logging import setup_logging, get_logger
from coi.providers.base import ProviderConfig
from coi.providers.openai_provider import OpenAIProvider


async def main():
    """Main application entry point."""
    
    # Load configuration
    try:
        config = load_config()
        validate_config(config)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n🔧 Please check your .env file or environment variables")
        return 1
    
    # Set up logging
    setup_logging(
        level=config.log_level,
        log_file=config.log_file,
        enable_debug=config.enable_debug
    )
    
    logger = get_logger(__name__)
    logger.info("🚀 AI Experimentation Platform starting...")
    
    # Show available providers
    available_providers = get_available_providers(config)
    logger.info(f"Available providers: {available_providers}")
    
    if not available_providers.get("openai", False):
        logger.error("OpenAI provider not configured")
        return 1
    
    # Initialize OpenAI provider
    try:
        provider_config = ProviderConfig(
            api_key=config.openai_api_key,
            timeout=config.request_timeout,
            max_retries=config.max_retries
        )
        provider = OpenAIProvider(provider_config)
        logger.info("✅ OpenAI provider initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize provider: {e}")
        return 1
    
    # Test generation
    test_prompt = "Explain the benefits of structured code organization in software development."
    
    try:
        logger.info(f"Making test API call with prompt: {test_prompt[:50]}...")
        
        response = await provider.generate(
            prompt=test_prompt,
            model=config.default_model,
            temperature=config.default_temperature,
            max_tokens=config.default_max_tokens
        )
        
        logger.info("🎉 API call successful!")
        
        # Display results
        print("\n" + "="*60)
        print("🤖 AI RESPONSE")
        print("="*60)
        print(f"Model: {response.model} ({response.provider})")
        print(f"Tokens: {response.total_tokens} (${response.cost_usd:.6f})")
        print(f"Content: {response.content}")
        print("\n" + "="*60)
        print("📊 METADATA")
        print("="*60)
        for key, value in response.metadata.items():
            print(f"{key}: {value}")
        print("="*60)
        
        logger.info(
            f"Generation complete: {response.total_tokens} tokens, "
            f"${response.cost_usd:.6f} cost"
        )
        
        return 0
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 