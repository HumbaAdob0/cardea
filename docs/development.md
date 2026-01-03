# Development Guide

## Project Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.9+
- Git

### Initial Setup
```bash
# Clone repository
git clone https://github.com/gauciv/cardea.git
cd cardea

# Setup development environment
make dev-setup

# Configure environment
cp .env.template .env
# Edit .env with your configuration
```

## Architecture Overview

Project Cardea follows a modular, atomic development approach with clear separation of concerns:

### 1. Sentry (Edge Layer)
**Location**: `sentry/`
**Purpose**: On-premise network monitoring
**Tech Stack**: Docker, Zeek, Suricata, KitNET, Python

```bash
# Development
make sentry-dev

# Components
sentry/
├── services/       # Monitoring services (Zeek, Suricata, KitNET)
├── bridge/         # Python orchestration
├── web/           # Local setup interface
└── config/        # Configuration management
```

### 2. Oracle (Cloud Layer)
**Location**: `oracle/`
**Purpose**: AI-powered threat analysis
**Tech Stack**: FastAPI, Azure AI, Supabase, Python

```bash
# Development
make oracle-dev

# Components
oracle/
├── api/           # FastAPI application
├── ai/            # Azure AI integration
├── database/      # Supabase models
└── services/      # Business logic
```

### 3. Dashboard (User Layer)
**Location**: `dashboard/`
**Purpose**: Web-based management interface
**Tech Stack**: Next.js, React, Shadcn UI, TypeScript

```bash
# Development
make dashboard-dev

# Components
dashboard/
├── components/    # UI components
├── pages/         # Next.js pages
├── hooks/         # React hooks
└── services/      # API integration
```

### 4. Shared Libraries
**Location**: `shared/`
**Purpose**: Common types and utilities
**Languages**: Python, TypeScript

## Development Workflow

### Atomic Development Principles
1. **Module Independence**: Each component (Sentry, Oracle, Dashboard) can run independently
2. **Clear Contracts**: Well-defined APIs between layers
3. **Test-Driven**: Each component has comprehensive tests
4. **Portable**: Platform-agnostic with containerization

### Development Process
1. **Start with Phase**: Work on one phase/component at a time
2. **Test Atomically**: Ensure each component works before integration
3. **Document Changes**: Update relevant documentation
4. **Integration Testing**: Test component interactions

### Code Quality Standards
- **Linting**: `make lint` - Consistent code style
- **Testing**: `make test` - Comprehensive test coverage
- **Security**: `make check-deps` - Vulnerability scanning
- **Formatting**: `make format` - Automated code formatting

## Component Development

### Sentry Development
```bash
# Start development environment
make sentry-dev

# Key development areas:
# - Network monitoring integration
# - KitNET anomaly detection
# - Bridge service orchestration
# - Local web interface
```

### Oracle Development
```bash
# Start development environment
make oracle-dev

# Key development areas:
# - FastAPI backend
# - Azure AI integration
# - RAG system implementation
# - Alert processing logic
```

### Dashboard Development
```bash
# Start development environment
make dashboard-dev

# Key development areas:
# - React components
# - Network visualization
# - Real-time updates
# - User authentication
```

## Testing Strategy

### Unit Tests
- Component-level testing
- Mock external dependencies
- High code coverage (>80%)

### Integration Tests
- Cross-component communication
- API contract validation
- End-to-end workflows

### Security Tests
- Dependency vulnerability scanning
- API security testing
- Network security validation

## Deployment

### Local Deployment
```bash
# Full stack locally
make deploy-local

# Individual components
docker compose up sentry
docker compose up oracle
docker compose up dashboard
```

### Production Deployment
- Sentry: On-premise hardware deployment
- Oracle: Cloud deployment (Azure/AWS)
- Dashboard: Web hosting (Vercel/Netlify)

## Troubleshooting

### Common Issues
1. **Port Conflicts**: Check if ports 3000, 8000, 5432 are available
2. **Docker Issues**: Restart Docker daemon
3. **Environment Variables**: Verify .env configuration
4. **Network Access**: Ensure proper firewall configuration

### Debug Commands
```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f [service_name]

# Reset environment
make clean && make dev-setup
```

## Contributing

### Code Contribution Process
1. **Fork Repository**: Create your feature branch
2. **Atomic Development**: Work on one component at a time
3. **Test Thoroughly**: Ensure all tests pass
4. **Document Changes**: Update relevant documentation
5. **Submit PR**: Clear description of changes

### Code Style
- Follow existing code patterns
- Use meaningful variable names
- Add comprehensive comments
- Follow security best practices

See [CONTRIBUTING.md](../.github/CONTRIBUTING.md) for detailed guidelines.