"""
Web interface for the AI experimentation platform.

This package provides a Flask-based web interface for interacting with
AI models and building applications through a chat interface.
"""

from .app import create_app

__all__ = ["create_app"]