"""
Web search tool for AI function calling.

This module provides a web search tool that can be used by AI models
to search the internet for current information.
"""

import json
import asyncio
from typing import Dict, Any, Optional
import logging

try:
    import requests
except ImportError:
    raise ImportError("requests package not found. Install with: pip install requests")

from .base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """
    Web search tool using DuckDuckGo Instant Answer API.
    
    This tool allows AI models to search the web for current information
    without requiring API keys or complex setup.
    """
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for current information, news, and facts"
        )
        self.base_url = "https://api.duckduckgo.com/"
        self.timeout = 10
    
    async def execute(self, query: str, **kwargs) -> ToolResult:
        """
        Execute web search.
        
        Args:
            query: Search query string
            **kwargs: Additional parameters (unused)
            
        Returns:
            ToolResult with search results
        """
        try:
            self.logger.debug(f"Searching for: {query}")
            
            # Use asyncio to run the blocking requests call
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._search, query)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            return ToolResult(
                success=False,
                content="",
                error=f"Search failed: {str(e)}"
            )
    
    def _search(self, query: str) -> ToolResult:
        """
        Perform synchronous web search.
        
        Args:
            query: Search query string
            
        Returns:
            ToolResult with search results
        """
        try:
            # DuckDuckGo Instant Answer API
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'AI-Experimentation-Platform/1.0'
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            results = []
            
            # Abstract (direct answer)
            if data.get('Abstract'):
                results.append(f"Answer: {data['Abstract']}")
                if data.get('AbstractURL'):
                    results.append(f"Source: {data['AbstractURL']}")
            
            # Definition
            if data.get('Definition'):
                results.append(f"Definition: {data['Definition']}")
                if data.get('DefinitionURL'):
                    results.append(f"Source: {data['DefinitionURL']}")
            
            # Related topics
            if data.get('RelatedTopics'):
                topics = []
                for topic in data['RelatedTopics'][:3]:  # Limit to 3 topics
                    if isinstance(topic, dict) and topic.get('Text'):
                        topics.append(topic['Text'])
                if topics:
                    results.append(f"Related: {' | '.join(topics)}")
            
            # Infobox
            if data.get('Infobox') and data['Infobox'].get('content'):
                info_items = []
                for item in data['Infobox']['content'][:3]:  # Limit to 3 items
                    if item.get('label') and item.get('value'):
                        info_items.append(f"{item['label']}: {item['value']}")
                if info_items:
                    results.append(f"Info: {' | '.join(info_items)}")
            
            if results:
                content = "\\n".join(results)
            else:
                content = f"No direct answers found for '{query}'. Try rephrasing your search."
            
            return ToolResult(
                success=True,
                content=content,
                metadata={
                    'query': query,
                    'source': 'DuckDuckGo',
                    'has_abstract': bool(data.get('Abstract')),
                    'has_definition': bool(data.get('Definition')),
                    'related_topics_count': len(data.get('RelatedTopics', []))
                }
            )
            
        except requests.RequestException as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Network error: {str(e)}"
            )
        except json.JSONDecodeError as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Failed to parse search results: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Unexpected error: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for this tool's parameters.
        
        Returns:
            OpenAI function calling schema
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to find information about"
                        }
                    },
                    "required": ["query"]
                }
            }
        }