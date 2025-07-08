"""
Tools for AI function calling.

This package contains tool implementations that can be called by AI models
to extend their capabilities with web search, calculations, and other functions.
"""

from .base import BaseTool
from .web_search import WebSearchTool

__all__ = ["BaseTool", "WebSearchTool"]