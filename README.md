# Project Cardea

> A hybrid, agentic AI cybersecurity platform for Small-to-Medium Enterprises

## Overview

Project Cardea provides cost-effective 24/7 cybersecurity monitoring through a dual-layer architecture:

- **Cardea Sentry (The Reflex)** - Local edge detection system running on-premise
- **Cardea Oracle (The Brain)** - Cloud-based AI threat analysis and management

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cardea Sentry │────│  Cardea Oracle  │────│   Web Dashboard │
│   (Edge Layer)  │    │  (Cloud Layer)  │    │  (User Layer)   │
│                 │    │                 │    │                 │
│ • Zeek          │    │ • FastAPI       │    │ • Next.js       │
│ • Suricata      │    │ • Azure AI      │    │ • React Flow    │
│ • KitNET        │    │ • Supabase      │    │ • Shadcn UI     │
│ • Bridge        │    │ • RAG System    │    │ • Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
cardea/
├── sentry/           # Edge layer (local network monitoring)
├── oracle/           # Cloud layer (AI threat analysis)
├── dashboard/        # User interface (web application)
├── shared/           # Common libraries and utilities
├── infrastructure/   # Deployment and DevOps
├── docs/            # Documentation
└── scripts/         # Development and utility scripts
```

## Development Philosophy

- **Modularity**: Clear separation between edge, cloud, and UI components
- **Portability**: Platform-agnostic design with containerization
- **Atomic Development**: Each component works independently before integration
- **Presentable Code**: Production-ready, well-documented codebase

## Quick Start

1. **Development Environment**: `make dev-setup`
2. **Run Sentry**: `make sentry-dev`
3. **Run Oracle**: `make oracle-dev`
4. **Run Dashboard**: `make dashboard-dev`

See [Development Guide](docs/development.md) for detailed setup instructions.

## License

MIT License - see [LICENSE](LICENSE) for details.
