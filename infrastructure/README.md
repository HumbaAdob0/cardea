# Infrastructure Configuration
> Deployment and DevOps for Project Cardea

## Overview
This module contains deployment configurations and infrastructure-as-code:
- **Docker**: Container configurations
- **Terraform**: Cloud infrastructure
- **CI/CD**: GitHub Actions workflows
- **Monitoring**: Observability stack

## Structure
```
infrastructure/
├── docker/         # Container configurations
├── terraform/      # Infrastructure as Code
├── k8s/           # Kubernetes manifests
├── monitoring/    # Observability stack
└── scripts/       # Deployment scripts
```

## Deployment Targets
- **Development**: Local Docker containers
- **Staging**: Cloud staging environment
- **Production**: Multi-region deployment

See [Infrastructure Documentation](../docs/infrastructure/) for detailed information.