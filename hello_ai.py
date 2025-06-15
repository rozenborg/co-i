#!/usr/bin/env python3
"""
Hello AI World - Your First AI API Call

This script demonstrates the basics of calling OpenAI's API:
- Making a successful API call
- Handling errors gracefully
- Understanding token usage and costs
- Basic async programming patterns

Run this script to make your first AI API call and understand the fundamentals.
"""

import os
import asyncio
import sys
from typing import Dict, Any
from dataclasses import dataclass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # This loads .env file if it exists
except ImportError:
    print("⚠️  python-dotenv not found, using system environment variables only")

try:
    from openai import AsyncOpenAI
except ImportError:
    print("❌ OpenAI package not found. Install it with: pip install openai")
    sys.exit(1)


@dataclass
class AIResponse:
    """Container for AI response data"""
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    cost_usd: float


class OpenAIProvider:
    """Simple OpenAI provider for learning purposes"""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
    }
    
    def __init__(self, api_key: str):
        """Initialize the OpenAI client"""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = AsyncOpenAI(api_key=api_key)
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of an API call based on token usage"""
        if model not in self.PRICING:
            print(f"⚠️  Unknown model '{model}', using gpt-3.5-turbo pricing")
            model = 'gpt-3.5-turbo'
        
        pricing = self.PRICING[model]
        input_cost = (prompt_tokens / 1000) * pricing['input']
        output_cost = (completion_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    async def generate(self, prompt: str, model: str = 'gpt-3.5-turbo') -> AIResponse:
        """Generate a response using OpenAI's API"""
        try:
            print(f"🤖 Calling OpenAI API with model: {model}")
            print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,  # Keep it small for cost control
                temperature=0.7
            )
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate cost
            cost = self.calculate_cost(
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens
            )
            
            return AIResponse(
                content=content,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                model=model,
                cost_usd=cost
            )
            
        except Exception as e:
            print(f"❌ Error calling OpenAI API: {e}")
            raise


async def main():
    """Main function - Your first AI API call!"""
    
    print("🚀 Hello AI World - Making your first API call!")
    print("=" * 50)
    
    # Step 1: Get API key from environment (supports .env file)
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Please set your OPENAI_API_KEY")
        print("\n🔧 Two ways to do this:")
        print("1. Create a .env file with: OPENAI_API_KEY=sk-your-key-here")
        print("2. Export in terminal: export OPENAI_API_KEY=sk-your-key-here")
        print("\n📁 Current directory:", os.getcwd())
        print("🔍 Looking for .env file:", ".env file exists" if os.path.exists('.env') else ".env file not found")
        return
    
    # Show that we found the API key (but don't print it!)
    print(f"✅ OpenAI API key found (ends with: ...{api_key[-4:]})")
    
    # Step 2: Initialize provider
    try:
        provider = OpenAIProvider(api_key)
        print("✅ OpenAI provider initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize provider: {e}")
        return
    
    # Step 3: Make the API call
    test_prompt = "Explain what happens when you make an AI API call in simple terms."
    
    try:
        response = await provider.generate(test_prompt)
        
        # Step 4: Print the response
        print("\n🎉 API call successful!")
        print("=" * 50)
        print(f"Response: {response.content}")
        print()
        
        # Step 5: Show the cost breakdown
        print("💰 Cost Analysis:")
        print(f"   Model: {response.model}")
        print(f"   Prompt tokens: {response.prompt_tokens}")
        print(f"   Completion tokens: {response.completion_tokens}")
        print(f"   Total tokens: {response.total_tokens}")
        print(f"   Cost: ${response.cost_usd:.6f} USD")
        print()
        
        # Step 6: Explain what happened
        print("🧠 What just happened?")
        print("1. We sent your prompt to OpenAI's servers")
        print("2. Their model processed it and generated a response")
        print("3. We received the response along with usage statistics")
        print("4. We calculated the cost based on tokens used")
        print("5. Tokens are roughly 4 characters each in English")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print("\nCommon issues:")
        print("- Invalid API key")
        print("- Insufficient credits")
        print("- Network connectivity problems")
        print("- Rate limiting (too many requests)")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 