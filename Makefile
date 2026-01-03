# Makefile for Project Cardea
# Provides atomic development workflow with clear separation of concerns

.PHONY: help dev-setup clean test lint format check-deps sentry-dev oracle-dev dashboard-dev

# Default target
help:
	@echo "Project Cardea - Hybrid AI Cybersecurity Platform"
	@echo ""
	@echo "Available targets:"
	@echo "  dev-setup      Set up development environment"
	@echo "  clean          Clean all build artifacts and containers"
	@echo "  test           Run all tests"
	@echo "  lint           Run linting across all components"
	@echo "  format         Format code across all components"
	@echo "  check-deps     Check for security vulnerabilities in dependencies"
	@echo ""
	@echo "Development servers:"
	@echo "  sentry-dev     Run Sentry (edge layer) in development mode"
	@echo "  oracle-dev     Run Oracle (cloud layer) in development mode"
	@echo "  dashboard-dev  Run Dashboard (UI layer) in development mode"
	@echo ""
	@echo "Integration:"
	@echo "  integration    Run full integration tests"
	@echo "  deploy-local   Deploy full stack locally"

# Development environment setup
dev-setup:
	@echo "Setting up Project Cardea development environment..."
	@scripts/setup-dev.sh

# Clean all artifacts
clean:
	@echo "Cleaning build artifacts..."
	@docker compose down -v --remove-orphans 2>/dev/null || true
	@docker system prune -f
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true

# Testing
test:
	@echo "Running all tests..."
	@make -C sentry test
	@make -C oracle test
	@make -C dashboard test
	@make -C shared test

# Code quality
lint:
	@echo "Running linting..."
	@scripts/lint-all.sh

format:
	@echo "Formatting code..."
	@scripts/format-all.sh

# Security
check-deps:
	@echo "Checking dependencies for vulnerabilities..."
	@scripts/security-check.sh

# Development servers
sentry-dev:
	@echo "Starting Sentry development environment..."
	@make -C sentry dev

oracle-dev:
	@echo "Starting Oracle development environment..."
	@make -C oracle dev

dashboard-dev:
	@echo "Starting Dashboard development environment..."
	@make -C dashboard dev

# Integration
integration:
	@echo "Running integration tests..."
	@scripts/integration-test.sh

deploy-local:
	@echo "Deploying full stack locally..."
	@docker compose up -d