# Cardea Infrastructure

> Cloud infrastructure configuration for Project Cardea

## Overview

This module contains Terraform configurations for deploying Cardea to Azure:

| Component | Azure Service | Purpose |
|-----------|--------------|---------|
| Dashboard | Static Web App | React frontend hosting |
| Oracle | Container Apps | FastAPI backend |
| Database | PostgreSQL Flexible Server | Persistent storage |
| Cache | Azure Cache for Redis | Session/caching layer |
| AI | Azure OpenAI | GPT-4o intelligence |
| Search | Azure AI Search | RAG for threat intel |
| Registry | Container Registry | Docker image storage |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure Cloud                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Resource Group                           │ │
│  │                                                             │ │
│  │  ┌─────────────┐    ┌─────────────────────────────────┐   │ │
│  │  │   Static    │    │      Container Apps Env          │   │ │
│  │  │   Web App   │    │  ┌──────────┐                   │   │ │
│  │  │ (Dashboard) │────│  │  Oracle  │                   │   │ │
│  │  └─────────────┘    │  │Container │                   │   │ │
│  │                     │  └────┬─────┘                   │   │ │
│  │                     └───────┼─────────────────────────┘   │ │
│  │                             │                              │ │
│  │          ┌──────────────────┼──────────────────┐          │ │
│  │          │                  │                  │          │ │
│  │    ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐    │ │
│  │    │PostgreSQL │     │   Redis   │     │  OpenAI   │    │ │
│  │    │  Flex     │     │   Cache   │     │ + Search  │    │ │
│  │    └───────────┘     └───────────┘     └───────────┘    │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              ▲                                 │
└──────────────────────────────┼─────────────────────────────────┘
                               │ HTTPS (webhook)
                               │
              ┌────────────────┴────────────────┐
              │        On-Premise Sentry        │
              │  ┌──────┐ ┌────────┐ ┌──────┐  │
              │  │ Zeek │ │Suricata│ │KitNET│  │
              │  └──────┘ └────────┘ └──────┘  │
              │            Bridge               │
              └─────────────────────────────────┘
```

## Quick Start

### Prerequisites

1. **Azure CLI** - Install and login:
   ```bash
   az login
   az account set --subscription "Your Subscription"
   ```

2. **Terraform** - Install v1.0.0+:
   ```bash
   brew install terraform  # macOS
   # or download from terraform.io
   ```

3. **Docker** - For building containers

### Deploy Development Environment

```bash
# Navigate to terraform directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan -var-file="dev.tfvars"

# Apply (creates all resources)
terraform apply -var-file="dev.tfvars"
```

### Deploy Production Environment

```bash
# Set sensitive variables via environment
export TF_VAR_db_admin_password="YourSecurePassword123!"
export TF_VAR_sentry_api_key="YourSentryApiKey"

# Apply production configuration
terraform apply -var-file="prod.tfvars"
```

### Using the Deployment Script

```bash
# Deploy dev environment
./scripts/deploy.sh dev

# Deploy production
./scripts/deploy.sh prod
```

## Configuration Files

| File | Purpose |
|------|---------|
| `main.tf` | Core provider and AI services |
| `variables.tf` | Input variable definitions |
| `oracle.tf` | Container Apps, DB, Redis, ACR |
| `dashboard.tf` | Static Web App configuration |
| `outputs.tf` | Output values for integration |
| `dev.tfvars` | Development environment values |
| `prod.tfvars` | Production environment values |

## Environment Differences

| Feature | Development | Production |
|---------|-------------|------------|
| OpenAI Model | gpt-4o-mini | gpt-4o |
| Search Tier | Free | Basic |
| DB SKU | B_Standard_B1ms | GP_Standard_D2s_v3 |
| Redis SKU | Basic C0 | Standard C0 |
| Container Replicas | 0-3 (scale to zero) | 2-10 |
| Log Retention | 30 days | 90 days |
| Estimated Cost | ~$30-50/month | ~$150-300/month |

## Connecting Sentry to Oracle

After deployment, configure your on-premise Sentry to communicate with Oracle:

### 1. Get Configuration

```bash
cd infrastructure/terraform
terraform output sentry_env_config
```

### 2. Update Sentry Environment

Add to `sentry/.env`:

```bash
ORACLE_WEBHOOK_URL=https://cardea-oracle.azurecontainerapps.io/api/alerts
ORACLE_API_KEY=your_generated_key
SENTRY_ID=sentry_home_001
```

### 3. Restart Sentry

```bash
cd sentry
docker compose down && docker compose up -d
```

### 4. Verify Connection

```bash
curl -X POST https://cardea-oracle.azurecontainerapps.io/api/alerts \
  -H "Content-Type: application/json" \
  -H "X-Sentry-API-Key: your_generated_key" \
  -d '{"test": true}'
```

## Security Considerations

### IP Whitelisting

For production, restrict Oracle access to known Sentry IPs:

```hcl
# In prod.tfvars
sentry_allowed_ips = [
  "203.0.113.10/32",   # Home Sentry
  "198.51.100.20/32",  # Office Sentry
]
```

### Secrets Management

Sensitive values should be set via environment variables:

```bash
export TF_VAR_db_admin_password="..."
export TF_VAR_sentry_api_key="..."
```

Or use Azure Key Vault integration (see `oracle.tf` comments).

### Network Security

- All traffic is encrypted (TLS 1.2+)
- Database uses SSL connections
- Redis uses TLS endpoint
- Container Apps has built-in DDoS protection

## Troubleshooting

### Common Issues

1. **Terraform init fails**
   ```bash
   rm -rf .terraform .terraform.lock.hcl
   terraform init
   ```

2. **Container App won't start**
   - Check logs: `az containerapp logs show -n cardea-oracle -g rg-cardea-dev`
   - Verify image exists in ACR
   - Check environment variables are set correctly

3. **Database connection refused**
   - Ensure firewall rules allow Azure services
   - Check connection string uses SSL

4. **Dashboard can't reach Oracle**
   - Verify CORS_ORIGINS includes the dashboard URL
   - Check Container App ingress is enabled

### Getting Outputs

```bash
# All outputs
terraform output

# Specific output
terraform output oracle_url

# Sensitive outputs
terraform output -raw db_password
terraform output -raw sentry_api_key
```

### Destroying Resources

```bash
# Destroy everything (careful!)
terraform destroy -var-file="dev.tfvars"
```

## CI/CD

GitHub Actions workflow (`.github/workflows/deploy.yml`) automates:

1. Building Oracle container → ACR
2. Deploying Dashboard → Static Web App
3. Deploying Oracle → Container Apps
4. Running database migrations
5. Smoke tests

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_CREDENTIALS` | Service principal JSON |
| `ACR_LOGIN_SERVER` | e.g., `cardeaacr.azurecr.io` |
| `ACR_USERNAME` | ACR admin username |
| `ACR_PASSWORD` | ACR admin password |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | SWA deployment token |
| `DATABASE_URL` | PostgreSQL connection string |
| `ORACLE_URL` | Oracle API URL |
| `DASHBOARD_URL` | Dashboard URL |

## Cost Optimization

### Development
- Use `is_production = false`
- Scale to zero when not in use
- Use free tier for AI Search
- Consider stopping/starting resources on schedule

### Production
- Enable autoscaling
- Use reserved capacity for predictable workloads
- Monitor with Azure Cost Management
- Set up budget alerts