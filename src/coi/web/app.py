"""
Flask application for the AI experimentation platform.

This module creates and configures the Flask web application for the
chat-based AI app generation platform.
"""

import asyncio
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging

from ..utils.config import load_config
from ..providers.factory import ProviderFactory
from ..tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)
    
    # Load configuration
    config = load_config()
    
    # Initialize tools
    web_search = WebSearchTool()
    
    @app.route('/')
    def index():
        """Main application page."""
        return render_template('index.html')
    
    @app.route('/api/providers')
    def get_providers():
        """Get available AI providers."""
        try:
            available = ProviderFactory.get_available_providers(config)
            return jsonify({
                'success': True,
                'providers': available
            })
        except Exception as e:
            logger.error(f"Error getting providers: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """Handle chat messages."""
        try:
            data = request.get_json()
            
            message = data.get('message', '')
            provider_name = data.get('provider', 'openai')
            
            if not message:
                return jsonify({
                    'success': False,
                    'error': 'Message is required'
                }), 400
            
            # Create provider
            provider = ProviderFactory.create_provider(provider_name, config)
            
            # For now, just echo the message with provider info
            # TODO: Implement actual AI generation with function calling
            response_text = f"Echo from {provider_name}: {message}"
            
            return jsonify({
                'success': True,
                'response': response_text,
                'provider': provider_name,
                'tokens': {
                    'prompt': 0,
                    'completion': 0,
                    'total': 0
                },
                'cost': 0.0
            })
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/search', methods=['POST'])
    def search():
        """Handle web search requests."""
        try:
            data = request.get_json()
            query = data.get('query', '')
            
            if not query:
                return jsonify({
                    'success': False,
                    'error': 'Query is required'
                }), 400
            
            # Run async search in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(web_search.execute(query))
                
                return jsonify({
                    'success': result.success,
                    'content': result.content,
                    'error': result.error,
                    'metadata': result.metadata
                })
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app