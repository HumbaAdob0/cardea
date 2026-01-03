#!/bin/bash
# Development Environment Setup Script for Project Cardea

set -e

echo "🛡️  Setting up Project Cardea development environment..."

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is required but not installed."
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is required but not installed."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is required but not installed."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed."
        exit 1
    fi
    
    echo "✅ All prerequisites found"
}

# Setup shared libraries
setup_shared() {
    echo "📚 Setting up shared libraries..."
    cd shared
    
    # Python package
    if [ ! -f "setup.py" ]; then
        cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="cardea-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    python_requires=">=3.9",
)
EOF
    fi
    
    # TypeScript package
    if [ ! -f "package.json" ]; then
        cat > package.json << 'EOF'
{
  "name": "@cardea/shared",
  "version": "0.1.0",
  "description": "Shared types and utilities for Project Cardea",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  },
  "files": [
    "dist/"
  ]
}
EOF
    fi
    
    cd ..
}

# Create development Docker compose
create_dev_compose() {
    echo "🐳 Creating development Docker Compose..."
    
    cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  # Development database for Oracle
  postgres-dev:
    image: postgres:15
    environment:
      POSTGRES_DB: cardea_dev
      POSTGRES_USER: cardea
      POSTGRES_PASSWORD: cardea_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

  # Redis for caching and sessions
  redis-dev:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Development network monitoring (lightweight)
  zeek-dev:
    build: ./sentry/services/zeek
    volumes:
      - ./sentry/data/zeek:/usr/local/zeek/logs
    network_mode: host
    profiles:
      - sentry

volumes:
  postgres_dev_data:
EOF
}

# Setup Git hooks
setup_git_hooks() {
    echo "🪝 Setting up Git hooks..."
    
    mkdir -p .git/hooks
    
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for Project Cardea

echo "🔍 Running pre-commit checks..."

# Run linting
make lint || {
    echo "❌ Linting failed. Please fix the issues before committing."
    exit 1
}

# Run quick tests
make test || {
    echo "❌ Tests failed. Please fix the issues before committing."
    exit 1
}

echo "✅ Pre-commit checks passed"
EOF

    chmod +x .git/hooks/pre-commit
}

# Create environment template
create_env_template() {
    echo "🔧 Creating environment template..."
    
    cat > .env.template << 'EOF'
# Project Cardea Environment Configuration

# Development/Production
NODE_ENV=development
LOG_LEVEL=debug

# Oracle (Cloud) Configuration
ORACLE_API_URL=http://localhost:8000
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Sentry (Edge) Configuration
SENTRY_ID=sentry_001
ORACLE_WEBHOOK_URL=http://oracle:8000/api/alerts

# Dashboard Configuration
NEXTAUTH_SECRET=your_nextauth_secret
NEXTAUTH_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://cardea:cardea_dev_password@localhost:5432/cardea_dev

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key
EOF

    # Create local environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        cp .env.template .env
        echo "📝 Created .env file from template. Please update with your configuration."
    fi
}

# Main setup execution
main() {
    check_prerequisites
    setup_shared
    create_dev_compose
    setup_git_hooks
    create_env_template
    
    echo "🎉 Development environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Update .env with your configuration"
    echo "2. Run 'make sentry-dev' to start edge development"
    echo "3. Run 'make oracle-dev' to start cloud development"  
    echo "4. Run 'make dashboard-dev' to start UI development"
    echo ""
    echo "See docs/ for detailed component documentation."
}

main "$@"