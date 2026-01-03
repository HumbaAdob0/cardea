# Shared Libraries
> Common utilities and types across Cardea components

## Overview
Shared code used by Sentry, Oracle, and Dashboard:
- **Types**: TypeScript/Python type definitions
- **Utils**: Common utility functions
- **Constants**: Configuration constants
- **Protocols**: Communication protocols between layers

## Structure
```
shared/
├── types/          # Type definitions
├── utils/          # Utility functions
├── constants/      # Configuration constants
└── protocols/      # Inter-service communication
```

## Usage
```python
# Python components
from cardea_shared import AlertProtocol, SecurityTypes

# TypeScript/JavaScript
import { AlertType, NetworkNode } from '@cardea/shared'
```

See [Shared Library Documentation](../docs/shared/) for detailed API reference.