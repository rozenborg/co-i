# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Experimentation Platform built in Python that provides a unified interface for managing AI model experiments across multiple providers (OpenAI, Anthropic, etc.). The project follows a provider-agnostic architecture with sound software engineering practices.

## Development Commands

### Testing
```bash
# Run all tests with coverage
pytest tests/ -v --cov=src/coi --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_providers.py -v

# Run tests without slow integration tests
pytest tests/ -m "not slow"
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Running the Application
```bash
# Main entry point (requires .env configuration)
python main.py

# Or run the simple hello world script
python hello_ai.py
```

## Architecture

### Provider System
- **Base Provider (`src/coi/providers/base.py`)**: Abstract interface defining the contract all AI providers must implement
- **Provider Implementations**: Currently supports OpenAI with extensible architecture for additional providers
- **Standard Response Format**: All providers return `AIResponse` objects with consistent structure (content, tokens, cost, metadata)

### Configuration Management
- **Environment-based config** (`src/coi/utils/config.py`): Loads from `.env` files and environment variables
- **Provider availability detection**: Automatically detects which providers are configured
- **Validation**: Ensures required configuration is present before startup

### Core Components
- `src/coi/core/`: Core platform logic (currently minimal, intended for experiment management)
- `src/coi/providers/`: AI provider implementations with consistent interface
- `src/coi/utils/`: Utilities for configuration and logging

### Error Handling
- Custom exception hierarchy: `ProviderError`, `RateLimitError`, `InvalidConfigError`, `ModelNotFoundError`
- Graceful degradation when providers are unavailable
- Comprehensive logging with structured error reporting

## Configuration

### Required Environment Variables
At least one AI provider must be configured:
- `OPENAI_API_KEY`: OpenAI API key (format: sk-...)
- `ANTHROPIC_API_KEY`: Anthropic API key
- `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT`: Azure OpenAI credentials

### Optional Configuration
- `LOG_LEVEL`: Logging level (default: INFO)
- `DEFAULT_MODEL`: Default model to use (default: gpt-3.5-turbo)
- `DEFAULT_TEMPERATURE`: Default temperature (default: 0.7)
- `DEFAULT_MAX_TOKENS`: Default max tokens (default: 150)
- `REQUEST_TIMEOUT`: API request timeout (default: 30)
- `MAX_RETRIES`: Max retry attempts (default: 3)

## Development Patterns

### Adding New Providers
1. Inherit from `BaseProvider` in `src/coi/providers/`
2. Implement required abstract methods: `generate()`, `get_available_models()`, `estimate_cost()`, `_validate_config()`
3. Return standardized `AIResponse` objects
4. Add provider to factory/registration system
5. Add configuration validation and environment variable support

### Testing Strategy
- Mock external API calls using `unittest.mock`
- Test configuration validation thoroughly
- Include both unit tests and integration tests
- Use pytest markers for slow/integration tests

### Code Organization
- Follow the existing package structure under `src/coi/`
- Use dataclasses for configuration and response objects
- Implement proper logging with structured messages
- Include type hints throughout the codebase