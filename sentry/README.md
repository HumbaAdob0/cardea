# Sentry - Edge Layer
> Local network monitoring and anomaly detection

## Overview
The Sentry module handles on-premise network monitoring using:
- **Zeek**: Passive network analysis and logging
- **Suricata**: Real-time intrusion detection
- **KitNET**: AI-based anomaly scoring
- **Bridge**: Orchestration and alert escalation

## Architecture
```
Network Traffic → Zeek → KitNET → Bridge → Oracle (Cloud)
                ↘ Suricata ↗
```

## Quick Start
```bash
# Development mode
make dev

# Production deployment
make deploy
```

## Components
- `services/` - Core monitoring services (Zeek, Suricata, KitNET)
- `bridge/` - Python orchestration service
- `config/` - Configuration management
- `web/` - Local setup interface

See [Sentry Documentation](../docs/sentry/) for detailed information.