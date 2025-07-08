#!/usr/bin/env python3
"""
Web server for the AI experimentation platform.

This script runs the Flask web application for the chat-based AI app builder.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from coi.web import create_app
from coi.utils.config import load_config, validate_config
from coi.utils.logging import setup_logging

def main():
    """Main entry point for the web server."""
    # Load and validate configuration
    config = load_config()
    
    # Setup logging
    setup_logging(
        level=config.log_level,
        log_file=config.log_file,
        enable_debug=config.enable_debug
    )
    
    # Validate configuration
    try:
        validate_config(config)
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file or environment variables.")
        sys.exit(1)
    
    # Create and run the Flask app
    app = create_app()
    
    print("Starting AI App Builder...")
    print("Open your browser and go to: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    main()