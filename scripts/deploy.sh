#!/bin/bash
# ============================================
# Cardea Platform Deployment Script
# ============================================
# This script deploys the Cardea platform to Azure using Terraform.
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - Terraform >= 1.0.0 installed
#   - Docker installed (for building containers)
#
# Usage:
#   ./deploy.sh [dev|prod]
#
# Example:
#   ./deploy.sh dev      # Deploy development environment
#   ./deploy.sh prod     # Deploy production environment
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$ROOT_DIR/infrastructure/terraform"

# Default to dev environment
ENVIRONMENT="${1:-dev}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# ============================================
# Pre-flight Checks
# ============================================
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed. Please install it: https://docs.microsoft.com/cli/azure/install-azure-cli"
    fi

    # Check if logged in to Azure
    if ! az account show &> /dev/null; then
        log_error "Not logged in to Azure. Please run: az login"
    fi

    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it: https://www.terraform.io/downloads"
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it: https://docs.docker.com/get-docker/"
    fi

    log_success "All pre-flight checks passed!"
}

# ============================================
# Initialize Terraform
# ============================================
init_terraform() {
    log_info "Initializing Terraform..."
    cd "$TERRAFORM_DIR"
    terraform init -upgrade
    log_success "Terraform initialized!"
}

# ============================================
# Plan Terraform Changes
# ============================================
plan_terraform() {
    log_info "Planning Terraform changes for $ENVIRONMENT environment..."
    cd "$TERRAFORM_DIR"
    terraform plan -var-file="${ENVIRONMENT}.tfvars" -out=tfplan
    log_success "Terraform plan created!"
}

# ============================================
# Apply Terraform Changes
# ============================================
apply_terraform() {
    log_info "Applying Terraform changes..."
    cd "$TERRAFORM_DIR"
    terraform apply tfplan
    log_success "Infrastructure deployed!"
}

# ============================================
# Build and Push Oracle Container
# ============================================
build_and_push_oracle() {
    log_info "Building Oracle container..."
    
    cd "$TERRAFORM_DIR"
    
    # Get ACR details from Terraform output
    ACR_SERVER=$(terraform output -raw acr_login_server 2>/dev/null || echo "")
    ACR_USERNAME=$(terraform output -raw acr_admin_username 2>/dev/null || echo "")
    ACR_PASSWORD=$(terraform output -raw acr_admin_password 2>/dev/null || echo "")
    
    if [ -z "$ACR_SERVER" ]; then
        log_warning "ACR not yet provisioned. Skipping container build."
        return
    fi
    
    log_info "Logging in to ACR: $ACR_SERVER"
    echo "$ACR_PASSWORD" | docker login "$ACR_SERVER" -u "$ACR_USERNAME" --password-stdin
    
    log_info "Building Oracle image..."
    cd "$ROOT_DIR/oracle"
    docker build -t "$ACR_SERVER/cardea-oracle:latest" .
    
    log_info "Pushing Oracle image to ACR..."
    docker push "$ACR_SERVER/cardea-oracle:latest"
    
    log_success "Oracle container built and pushed!"
}

# ============================================
# Build Dashboard
# ============================================
build_dashboard() {
    log_info "Building Dashboard..."
    
    cd "$TERRAFORM_DIR"
    ORACLE_URL=$(terraform output -raw oracle_url 2>/dev/null || echo "http://localhost:8000")
    
    cd "$ROOT_DIR/dashboard"
    
    # Install dependencies
    npm ci
    
    # Build with Oracle URL
    VITE_ORACLE_URL="$ORACLE_URL" npm run build
    
    log_success "Dashboard built!"
}

# ============================================
# Print Deployment Summary
# ============================================
print_summary() {
    log_info "Deployment Summary"
    echo "============================================"
    
    cd "$TERRAFORM_DIR"
    
    echo ""
    echo "Environment: $ENVIRONMENT"
    echo "Mode: $(terraform output -raw current_mode 2>/dev/null || echo 'Unknown')"
    echo ""
    echo "🌐 Dashboard URL:"
    echo "   $(terraform output -raw dashboard_url 2>/dev/null || echo 'Not yet deployed')"
    echo ""
    echo "🔌 Oracle API URL:"
    echo "   $(terraform output -raw oracle_url 2>/dev/null || echo 'Not yet deployed')"
    echo ""
    echo "📡 Sentry Webhook URL:"
    echo "   $(terraform output -raw sentry_webhook_url 2>/dev/null || echo 'Not yet deployed')"
    echo ""
    echo "============================================"
    echo ""
    
    log_info "To configure Sentry, run:"
    echo "   terraform output -raw sentry_env_config"
    echo ""
    
    log_success "Deployment complete!"
}

# ============================================
# Main
# ============================================
main() {
    echo ""
    echo "============================================"
    echo "  Cardea Platform Deployment"
    echo "  Environment: $ENVIRONMENT"
    echo "============================================"
    echo ""

    preflight_checks
    init_terraform
    plan_terraform

    # Ask for confirmation
    echo ""
    read -p "Do you want to apply these changes? (y/N) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Deployment cancelled."
        exit 0
    fi

    apply_terraform
    build_and_push_oracle
    build_dashboard
    print_summary
}

main "$@"
