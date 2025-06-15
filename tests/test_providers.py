"""
Tests for AI provider implementations.

This module demonstrates testing best practices for the AI experimentation platform.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coi.providers.base import ProviderConfig, BaseProvider, AIResponse, ProviderError
from coi.providers.openai_provider import OpenAIProvider


class TestProviderConfig:
    """Test cases for ProviderConfig."""
    
    def test_provider_config_creation(self):
        """Test creating a provider configuration."""
        config = ProviderConfig(
            api_key="test-key",
            timeout=30,
            max_retries=3
        )
        
        assert config.api_key == "test-key"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.base_url is None
        assert config.organization is None


class TestOpenAIProvider:
    """Test cases for OpenAI provider."""
    
    def test_provider_initialization(self):
        """Test OpenAI provider initialization."""
        config = ProviderConfig(api_key="sk-test-key")
        
        with patch('coi.providers.openai_provider.AsyncOpenAI'):
            provider = OpenAIProvider(config)
            assert provider.config.api_key == "sk-test-key"
    
    def test_invalid_api_key(self):
        """Test validation of invalid API key."""
        config = ProviderConfig(api_key="invalid-key")
        
        with pytest.raises(Exception):  # Should raise InvalidConfigError
            with patch('coi.providers.openai_provider.AsyncOpenAI'):
                OpenAIProvider(config)
    
    def test_get_available_models(self):
        """Test getting available models."""
        config = ProviderConfig(api_key="sk-test-key")
        
        with patch('coi.providers.openai_provider.AsyncOpenAI'):
            provider = OpenAIProvider(config)
            models = provider.get_available_models()
            
            assert isinstance(models, list)
            assert len(models) > 0
            assert 'gpt-3.5-turbo' in models
    
    def test_cost_calculation(self):
        """Test cost calculation for different models."""
        config = ProviderConfig(api_key="sk-test-key")
        
        with patch('coi.providers.openai_provider.AsyncOpenAI'):
            provider = OpenAIProvider(config)
            
            # Test known model
            cost = provider._calculate_cost('gpt-3.5-turbo', 100, 50)
            expected = (100/1000 * 0.0015) + (50/1000 * 0.002)
            assert abs(cost - expected) < 0.000001
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        config = ProviderConfig(api_key="sk-test-key")
        
        with patch('coi.providers.openai_provider.AsyncOpenAI'):
            provider = OpenAIProvider(config)
            
            cost = provider.estimate_cost("Test prompt", "gpt-3.5-turbo", 100)
            assert cost > 0
            assert isinstance(cost, float)
    
    @pytest.mark.asyncio
    async def test_generate_success(self):
        """Test successful generation."""
        config = ProviderConfig(api_key="sk-test-key")
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30
        mock_response.id = "test-response-id"
        mock_response.created = 1234567890
        
        with patch('coi.providers.openai_provider.AsyncOpenAI') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            provider = OpenAIProvider(config)
            
            response = await provider.generate("Test prompt", "gpt-3.5-turbo")
            
            assert isinstance(response, AIResponse)
            assert response.content == "Test response"
            assert response.provider == "openai"
            assert response.model == "gpt-3.5-turbo"
            assert response.total_tokens == 30
            assert response.cost_usd > 0


class TestAIResponse:
    """Test cases for AIResponse."""
    
    def test_ai_response_creation(self):
        """Test creating an AI response."""
        response = AIResponse(
            content="Test response",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            model="gpt-3.5-turbo",
            cost_usd=0.001,
            provider="openai"
        )
        
        assert response.content == "Test response"
        assert response.total_tokens == 30
        assert response.provider == "openai"
        assert response.metadata is None 