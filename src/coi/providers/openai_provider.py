"""
OpenAI provider implementation for the AI experimentation platform.

This module provides integration with OpenAI's API including GPT-3.5, GPT-4,
and other OpenAI models with proper error handling and cost calculation.
"""

import asyncio
from typing import List, Optional, Dict, Any
import logging

try:
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletion
    from openai import RateLimitError as OpenAIRateLimitError
    from openai import AuthenticationError, APIError
except ImportError:
    raise ImportError("OpenAI package not found. Install with: pip install openai")

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


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider implementation.
    
    Supports GPT-3.5, GPT-4, and other OpenAI models with comprehensive
    error handling, cost calculation, and retry logic.
    """
    
    # Current pricing per 1K tokens (as of 2024)
    PRICING = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-4-turbo-preview': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
        'gpt-3.5-turbo-0125': {'input': 0.0015, 'output': 0.002},
    }
    
    def __init__(self, config: ProviderConfig):
        """Initialize OpenAI provider."""
        super().__init__(config)
        
        # Initialize OpenAI client
        client_kwargs = {
            'api_key': config.api_key,
            'timeout': config.timeout,
            'max_retries': config.max_retries,
        }
        
        if config.organization:
            client_kwargs['organization'] = config.organization
            
        if config.base_url:
            client_kwargs['base_url'] = config.base_url
            
        self.client = AsyncOpenAI(**client_kwargs)
        
        self.logger.info(f"OpenAI provider initialized with timeout={config.timeout}s")
    
    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.config.api_key:
            raise InvalidConfigError("OpenAI API key is required", "openai")
        
        if not self.config.api_key.startswith('sk-'):
            raise InvalidConfigError("OpenAI API key must start with 'sk-'", "openai")
        
        if self.config.timeout <= 0:
            raise InvalidConfigError("Timeout must be positive", "openai")
    
    async def generate(
        self,
        prompt: str,
        model: str = 'gpt-3.5-turbo',
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate response using OpenAI's API.
        
        Args:
            prompt: Input prompt for the model
            model: OpenAI model to use
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters
            
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
                **kwargs
            }
            
            if max_tokens:
                request_params['max_tokens'] = max_tokens
            
            # Make API call with retry logic
            response = await self._make_api_call(request_params)
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate cost
            cost = self._calculate_cost(
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens
            )
            
            # Create standardized response
            ai_response = AIResponse(
                content=content,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                model=model,
                cost_usd=cost,
                provider="openai",
                metadata={
                    'finish_reason': response.choices[0].finish_reason,
                    'response_id': response.id,
                    'created': response.created,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                }
            )
            
            self.logger.info(
                f"Generated response: {usage.total_tokens} tokens, "
                f"${cost:.6f} cost, finish_reason={response.choices[0].finish_reason}"
            )
            
            return ai_response
            
        except OpenAIRateLimitError as e:
            self.logger.warning(f"Rate limit exceeded: {e}")
            raise RateLimitError(str(e), "openai", model)
            
        except AuthenticationError as e:
            self.logger.error(f"Authentication failed: {e}")
            raise InvalidConfigError(f"Invalid API key: {e}", "openai")
            
        except APIError as e:
            if "model" in str(e).lower() and "not found" in str(e).lower():
                raise ModelNotFoundError(f"Model {model} not found: {e}", "openai", model)
            self.logger.error(f"OpenAI API error: {e}")
            raise ProviderError(f"API error: {e}", "openai", model)
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise ProviderError(f"Unexpected error: {e}", "openai", model)
    
    async def _make_api_call(self, params: Dict[str, Any]) -> ChatCompletion:
        """Make API call with exponential backoff retry."""
        for attempt in range(self.config.max_retries + 1):
            try:
                return await self.client.chat.completions.create(**params)
            except OpenAIRateLimitError:
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
            self.logger.warning(f"Unknown model '{model}', using gpt-3.5-turbo pricing")
            model = 'gpt-3.5-turbo'
        
        pricing = self.PRICING[model]
        input_cost = (prompt_tokens / 1000) * pricing['input']
        output_cost = (completion_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    def get_available_models(self) -> List[str]:
        """Get list of supported OpenAI models."""
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
            model: OpenAI model name
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