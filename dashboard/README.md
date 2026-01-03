# Dashboard - User Interface
> Web-based management and monitoring interface

## Overview
The Dashboard provides business owners with:
- **Network Visualization**: React Flow network mapping
- **Real-time Alerts**: Push notifications and status updates
- **Simple Controls**: "Confirm Block" / "Authorize" actions
- **Device Management**: Sentry pairing and configuration

## Architecture
```
Oracle API → Next.js → React Components → Shadcn UI
           ↘ WebSockets ↗
```

## Quick Start
```bash
# Development mode
make dev

# Build for production
make build
```

## Components
- `components/` - Reusable UI components
- `pages/` - Next.js pages and routing
- `hooks/` - Custom React hooks
- `services/` - API integration

See [Dashboard Documentation](../docs/dashboard/) for detailed information.