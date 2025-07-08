"""
Anthropic provider implementation for the AI experimentation platform.

This module provides integration with Anthropic's Claude API including Claude-3 
models with proper error handling and cost calculation.
"""

import asyncio
from typing import List, Optional, Dict, Any
import logging

try:
    from anthropic import AsyncAnthropic
    from anthropic.types import Message
    from anthropic import RateLimitError as AnthropicRateLimitError
    from anthropic import AuthenticationError, APIError
except ImportError:
    raise ImportError("Anthropic package not found. Install with: pip install anthropic")

from .base import (
    BaseProvider, 
    AIResponse, 
    ProviderConfig, 
    ProviderError, 
    RateLimitError, 
    InvalidConfigError,
    ModelNotFoundError
)

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """
    Anthropic provider implementation.
    
    Supports Claude-3 models with comprehensive error handling, 
    cost calculation, and retry logic.
    """
    
    # Current pricing per 1K tokens (as of July 2024)
    PRICING = {
        'claude-3-5-sonnet-20241022': {'input': 0.003, 'output': 0.015},
        'claude-3-5-sonnet-20240620': {'input': 0.003, 'output': 0.015},
        'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
    }
    
    def __init__(self, config: ProviderConfig):
        """Initialize Anthropic provider."""
        super().__init__(config)
        
        # Initialize Anthropic client
        client_kwargs = {
            'api_key': config.api_key,
            'timeout': config.timeout,
            'max_retries': config.max_retries,
        }
        
        if config.base_url:
            client_kwargs['base_url'] = config.base_url
            
        self.client = AsyncAnthropic(**client_kwargs)
        
        self.logger.info(f"Anthropic provider initialized with timeout={config.timeout}s")
    
    def _validate_config(self) -> None:
        """Validate Anthropic configuration."""
        if not self.config.api_key:
            raise InvalidConfigError("Anthropic API key is required", "anthropic")
        
        if not self.config.api_key.startswith('sk-ant-'):
            raise InvalidConfigError("Anthropic API key must start with 'sk-ant-'", "anthropic")
        
        if self.config.timeout <= 0:
            raise InvalidConfigError("Timeout must be positive", "anthropic")
    
    async def generate(
        self,
        prompt: str,
        model: str = 'claude-3-5-sonnet-20241022',
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate response using Anthropic's API.
        
        Args:
            prompt: Input prompt for the model
            model: Anthropic model to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Anthropic parameters
            
        Returns:
            AIResponse with generated content and metadata
            
        Raises:
            ProviderError: If API call fails
            RateLimitError: If rate limits are exceeded
            ModelNotFoundError: If model is not available
        """
        self.logger.debug(f"Generating with model={model}, temperature={temperature}")
        
        try:
            # Prepare request parameters
            request_params = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': temperature,
                'max_tokens': max_tokens or 1000,  # Anthropic requires max_tokens
                **kwargs
            }
            
            # Make API call with retry logic
            response = await self._make_api_call(request_params)
            
            # Extract response data
            content = response.content[0].text
            usage = response.usage
            
            # Calculate cost
            cost = self._calculate_cost(
                model=model,
                prompt_tokens=usage.input_tokens,
                completion_tokens=usage.output_tokens
            )
            
            # Create standardized response
            ai_response = AIResponse(
                content=content,
                prompt_tokens=usage.input_tokens,
                completion_tokens=usage.output_tokens,
                total_tokens=usage.input_tokens + usage.output_tokens,
                model=model,
                cost_usd=cost,
                provider="anthropic",
                metadata={
                    'stop_reason': response.stop_reason,
                    'response_id': response.id,
                    'model': response.model,
                    'role': response.role,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                }
            )
            
            self.logger.info(
                f"Generated response: {usage.input_tokens + usage.output_tokens} tokens, "
                f"${cost:.6f} cost, stop_reason={response.stop_reason}"
            )
            
            return ai_response
            
        except AnthropicRateLimitError as e:
            self.logger.warning(f"Rate limit exceeded: {e}")
            raise RateLimitError(str(e), "anthropic", model)
            
        except AuthenticationError as e:
            self.logger.error(f"Authentication failed: {e}")
            raise InvalidConfigError(f"Invalid API key: {e}", "anthropic")
            
        except APIError as e:
            if "model" in str(e).lower() and "not found" in str(e).lower():
                raise ModelNotFoundError(f"Model {model} not found: {e}", "anthropic", model)
            self.logger.error(f"Anthropic API error: {e}")
            raise ProviderError(f"API error: {e}", "anthropic", model)
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise ProviderError(f"Unexpected error: {e}", "anthropic", model)
    
    async def _make_api_call(self, params: Dict[str, Any]) -> Message:
        """Make API call with exponential backoff retry."""
        for attempt in range(self.config.max_retries + 1):
            try:
                return await self.client.messages.create(**params)
            except AnthropicRateLimitError:
                if attempt == self.config.max_retries:
                    raise
                wait_time = 2 ** attempt
                self.logger.warning(f"Rate limited, retrying in {wait_time}s (attempt {attempt + 1})")
                await asyncio.sleep(wait_time)
            except Exception:
                if attempt == self.config.max_retries:
                    raise
                wait_time = min(2 ** attempt, 60)
                self.logger.warning(f"API call failed, retrying in {wait_time}s (attempt {attempt + 1})")
                await asyncio.sleep(wait_time)
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on token usage and model pricing."""
        if model not in self.PRICING:
            self.logger.warning(f"Unknown model '{model}', using claude-3-5-sonnet pricing")
            model = 'claude-3-5-sonnet-20241022'
        
        pricing = self.PRICING[model]
        input_cost = (prompt_tokens / 1000) * pricing['input']
        output_cost = (completion_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    def get_available_models(self) -> List[str]:
        """Get list of supported Anthropic models."""
        return list(self.PRICING.keys())
    
    def estimate_cost(
        self, 
        prompt: str, 
        model: str, 
        max_tokens: Optional[int] = None
    ) -> float:
        """
        Estimate cost for a generation request.
        
        Args:
            prompt: Input prompt
            model: Anthropic model name
            max_tokens: Maximum tokens to generate
            
        Returns:
            Estimated cost in USD
        """
        # Rough estimation: ~4 characters per token
        estimated_prompt_tokens = len(prompt) // 4
        estimated_completion_tokens = max_tokens or 100
        
        return self._calculate_cost(
            model=model,
            prompt_tokens=estimated_prompt_tokens,
            completion_tokens=estimated_completion_tokens
        )