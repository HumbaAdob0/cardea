# Oracle - Cloud Layer
> AI-powered threat analysis and management

## Overview
The Oracle module provides cloud-based threat intelligence through:
- **FastAPI**: RESTful API backend
- **Azure AI**: GPT-4o/Phi-4 reasoning engine
- **RAG System**: Threat intelligence knowledge base
- **Supabase**: Time-series data storage

## Architecture
```
Sentry Alerts → FastAPI → Azure AI → RAG → Dashboard
                      ↓
                   Supabase
```

## Quick Start
```bash
# Development mode
make dev

# Deploy to cloud
make deploy
```

## Components
- `api/` - FastAPI application and routes
- `ai/` - Azure AI integration and RAG
- `database/` - Supabase schema and models
- `services/` - Business logic and threat analysis

See [Oracle Documentation](../docs/oracle/) for detailed information.