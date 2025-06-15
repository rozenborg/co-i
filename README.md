# AI Experimentation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![API](https://img.shields.io/badge/API-OpenAPI%203.0-green.svg)](https://swagger.io/specification/)

> A unified platform for managing AI model experimentation and deployment across multiple providers.

## Overview

The AI Experimentation Platform solves the complexity of managing AI model experiments across multiple providers and environments. Instead of writing custom integration code for each AI provider, managing prompt versions manually, or building your own evaluation infrastructure, this platform provides a unified interface for:

- **Multi-provider AI orchestration** - Work with OpenAI, Anthropic, Azure OpenAI, and custom enterprise APIs through a single interface
- **Experiment management** - Organize AI experiments into projects with clear goals, hypotheses, and measurable outcomes
- **Prompt engineering** - Version control your prompts and system messages with A/B testing capabilities
- **Model comparison** - Compare outputs across different models and providers with automated evaluation metrics
- **Production deployment** - Deploy proven experiments to production with monitoring and observability built-in

**Who is this for?**
- Development teams building AI-powered applications
- ML engineers running experiments across multiple models
- Product teams testing AI features with different providers
- Enterprises needing audit trails and cost monitoring for AI usage

## Features

### ✅ Current Features

**Core Platform**
- 🔌 **Provider-agnostic architecture** - Pluggable backends for any AI provider
- 📊 **Project-based organization** - Group related experiments with goals and success metrics
- 📝 **Prompt version control** - Full lifecycle management of prompts and system messages
- ⚖️ **Model comparison** - Side-by-side evaluation across providers with automated scoring
- 🛠️ **Tool calling support** - Function calling and tool integration across compatible models
- 📈 **Built-in observability** - Performance, cost, and quality metrics with real-time monitoring

**Technical Infrastructure**
- 🗄️ **Flexible database support** - SQLite for development, PostgreSQL for production
- 🔐 **Environment-based security** - Secure credential management and API key rotation
- 🌐 **RESTful API** - Complete OpenAPI 3.0 specification with interactive documentation
- ⚛️ **Modern web interface** - React-based dashboard with real-time updates
- 🐳 **Docker support** - One-command deployment with docker-compose
- 📋 **Audit logging** - Complete audit trail for enterprise compliance requirements

**AI Provider Support**
- OpenAI (GPT-3.5, GPT-4, GPT-4 Turbo)
- Anthropic (Claude 3 family)
- Azure OpenAI Service
- Custom enterprise APIs
- *More providers added regularly*

### 🚧 Planned Features

**Advanced Experimentation**
- 🧪 **A/B testing framework** - Statistical significance testing for prompt variations
- 📊 **Advanced analytics** - Detailed performance analytics and cost optimization insights
- 🔄 **Automated retraining** - Trigger model fine-tuning based on experiment results
- 🎯 **Custom evaluation metrics** - Define domain-specific success criteria

**Enterprise Features**
- 👥 **Team collaboration** - Role-based access control and shared workspaces
- 🔗 **CI/CD integration** - GitHub Actions and Jenkins plugins for automated testing
- 📺 **Advanced monitoring** - Integration with Prometheus, Grafana, and DataDog
- ☁️ **Cloud deployment** - One-click deployment to AWS, GCP, and Azure

## Quick Start

Get the platform running locally in under 5 minutes:

### Prerequisites
- Docker and Docker Compose
- At least one AI provider API key (OpenAI, Anthropic, etc.)

### 1. Clone and Start

```bash
git clone https://github.com/rozenborg/co-i.git
cd co-i
cp .env.example .env
```

### 2. Configure API Keys

Edit `.env` with your AI provider credentials:

```bash
# Required: At least one AI provider
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key

# Database (defaults to SQLite for development)
DATABASE_URL=sqlite:///./data/experiments.db

# Security
JWT_SECRET=your-random-secret-key
```

### 3. Launch Platform

```bash
docker-compose up -d
```

### 4. Access Interface

- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5. Create Your First Experiment

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support Bot",
    "description": "Compare response quality across models",
    "goal": "Achieve >90% customer satisfaction"
  }'
```

## Installation

### Local Development

**Requirements:**
- Python 3.9+
- Node.js 18+
- PostgreSQL (optional, SQLite used by default)

```bash
# Backend setup
git clone https://github.com/rozenborg/co-i.git
cd co-i/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start development servers
cd ../backend && python app.py  # API server on :8000
cd ../frontend && npm start     # Web interface on :3000
```

### Docker Deployment

**Single-node deployment:**

```bash
# Production-ready setup
git clone https://github.com/rozenborg/co-i.git
cd co-i
cp docker-compose.prod.yml docker-compose.yml
cp .env.production .env

# Configure production settings
nano .env

# Deploy
docker-compose up -d
```

**Multi-node deployment with external database:**

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    image: coi/api:latest
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres.example.com:5432/coi
      - REDIS_URL=redis://redis.example.com:6379
    deploy:
      replicas: 3
      
  web:
    image: coi/web:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Production Considerations

**Database:**
- Use PostgreSQL for production workloads
- Configure connection pooling (recommended: pgbouncer)
- Set up automated backups

**Security:**
- Use strong JWT secrets (32+ characters)
- Configure HTTPS with proper certificates
- Implement rate limiting
- Regular security updates

**Monitoring:**
- Enable application metrics collection
- Set up log aggregation
- Configure alerting for API failures

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///./data/experiments.db` | No |
| `REDIS_URL` | Redis for caching and queues | None (in-memory) | No |
| `JWT_SECRET` | Secret for authentication tokens | Random | **Yes** |
| `OPENAI_API_KEY` | OpenAI API credentials | None | No* |
| `ANTHROPIC_API_KEY` | Anthropic API credentials | None | No* |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | None | No* |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | None | No* |
| `LOG_LEVEL` | Application log level | `INFO` | No |
| `ENABLE_AUDIT_LOG` | Enable detailed audit logging | `false` | No |
| `MAX_CONCURRENT_REQUESTS` | Rate limit per provider | `10` | No |

*At least one AI provider must be configured

### Provider Configuration

**OpenAI:**
```json
{
  "provider": "openai",
  "config": {
    "api_key": "sk-...",
    "organization": "org-...",
    "models": ["gpt-4", "gpt-3.5-turbo"],
    "max_tokens": 4096,
    "temperature": 0.7
  }
}
```

**Anthropic:**
```json
{
  "provider": "anthropic",
  "config": {
    "api_key": "sk-ant-...",
    "models": ["claude-3-opus", "claude-3-sonnet"],
    "max_tokens": 4096,
    "temperature": 0.7
  }
}
```

**Custom Provider:**
```json
{
  "provider": "custom",
  "config": {
    "endpoint": "https://api.yourcompany.com/v1/chat",
    "api_key": "your-key",
    "headers": {
      "Custom-Header": "value"
    },
    "models": ["your-model-name"]
  }
}
```

## API Documentation

### Core Endpoints

**Projects Management**
```http
GET    /api/v1/projects              # List all projects
POST   /api/v1/projects              # Create new project
GET    /api/v1/projects/{id}         # Get project details
PUT    /api/v1/projects/{id}         # Update project
DELETE /api/v1/projects/{id}         # Delete project
```

**Experiments**
```http
GET    /api/v1/projects/{id}/experiments     # List experiments
POST   /api/v1/projects/{id}/experiments     # Create experiment
GET    /api/v1/experiments/{id}              # Get experiment
POST   /api/v1/experiments/{id}/run          # Execute experiment
GET    /api/v1/experiments/{id}/results      # Get results
```

**Prompts & Templates**
```http
GET    /api/v1/prompts                       # List prompt templates
POST   /api/v1/prompts                       # Create prompt template
GET    /api/v1/prompts/{id}/versions         # List prompt versions
POST   /api/v1/prompts/{id}/versions         # Create new version
```

### Example API Usage

**Create and run an experiment:**

```python
import requests

# Create project
project = requests.post('http://localhost:8000/api/v1/projects', json={
    'name': 'Product Description Generator',
    'description': 'Compare models for e-commerce product descriptions',
    'goal': 'Generate engaging, accurate product descriptions'
}).json()

# Create experiment
experiment = requests.post(f'http://localhost:8000/api/v1/projects/{project["id"]}/experiments', json={
    'name': 'A/B Test: GPT-4 vs Claude-3',
    'prompt_template': 'Generate a product description for: {product_name}',
    'models': ['gpt-4', 'claude-3-opus'],
    'test_cases': [
        {'product_name': 'Wireless Bluetooth Headphones'},
        {'product_name': 'Organic Cotton T-Shirt'},
        {'product_name': 'Smart Home Security Camera'}
    ],
    'evaluation_criteria': ['relevance', 'creativity', 'accuracy']
}).json()

# Run experiment
results = requests.post(f'http://localhost:8000/api/v1/experiments/{experiment["id"]}/run').json()
print(f"Experiment completed: {results['status']}")
```

### Interactive API Documentation

Full OpenAPI documentation available at: `http://localhost:8000/docs`

## Adding Custom AI Providers

The platform supports custom AI providers through a plugin architecture:

### 1. Create Provider Class

```python
# providers/custom_provider.py
from .base import BaseProvider
import requests

class CustomProvider(BaseProvider):
    def __init__(self, config):
        self.api_key = config['api_key']
        self.endpoint = config['endpoint']
        self.models = config['models']
    
    async def generate(self, prompt, model, **kwargs):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            **kwargs
        }
        
        response = requests.post(self.endpoint, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    
    def get_available_models(self):
        return self.models
    
    async def estimate_cost(self, prompt, model, **kwargs):
        # Implement cost calculation logic
        input_tokens = len(prompt.split()) * 1.3  # Rough approximation
        return input_tokens * 0.0001  # $0.0001 per token
```

### 2. Register Provider

```python
# config/providers.py
from providers.custom_provider import CustomProvider

AVAILABLE_PROVIDERS = {
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
    'azure': AzureProvider,
    'custom': CustomProvider,  # Add your provider
}
```

### 3. Configure in Environment

```bash
# .env
CUSTOM_PROVIDER_API_KEY=your-api-key
CUSTOM_PROVIDER_ENDPOINT=https://api.yourcompany.com/v1/chat
CUSTOM_PROVIDER_MODELS=model-1,model-2,model-3
```

### Provider Interface

All providers must implement:

```python
class BaseProvider:
    async def generate(self, prompt: str, model: str, **kwargs) -> str:
        """Generate response from AI model"""
        pass
    
    def get_available_models(self) -> List[str]:
        """Return list of available models"""
        pass
    
    async def estimate_cost(self, prompt: str, model: str, **kwargs) -> float:
        """Estimate cost for request"""
        pass
    
    def validate_config(self, config: dict) -> bool:
        """Validate provider configuration"""
        pass
```

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork the repository**
2. **Create a development environment:**

```bash
git clone https://github.com/yourusername/co-i.git
cd co-i
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

3. **Run tests:**

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Code Style

- **Python**: Black formatter, flake8 linting, type hints required
- **JavaScript/React**: ESLint + Prettier, functional components preferred
- **Commit messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/)

### Pull Request Process

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes with tests
3. Ensure all tests pass: `npm run test && pytest`
4. Update documentation if needed
5. Submit pull request with clear description

### Areas We Need Help

- 🔌 **New AI provider integrations** (Cohere, Hugging Face, local models)
- 📊 **Advanced evaluation metrics** (BLEU, ROUGE, custom domain metrics)
- 🎨 **UI/UX improvements** (data visualization, mobile responsiveness)
- 📝 **Documentation** (tutorials, video guides, API examples)
- 🐛 **Bug fixes and performance optimization**

### Reporting Issues

Use GitHub Issues with these labels:
- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Documentation improvements
- `provider` - AI provider related issues
- `performance` - Performance optimization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 AI Experimentation Platform Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Support

- 📖 **Documentation**: [docs.co-i.dev](https://docs.co-i.dev)
- 💬 **Community Discussions**: [GitHub Discussions](https://github.com/rozenborg/co-i/discussions)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/rozenborg/co-i/issues)
- 📧 **Email**: support@co-i.dev

**Built with ❤️ for the AI development community** 