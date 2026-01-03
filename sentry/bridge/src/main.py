#!/usr/bin/env python3
"""
Bridge Service - Orchestration and Alert Escalation
Main entry point for the Cardea Bridge service
"""

import os
import sys
import logging

# Add src to Python path for imports
sys.path.insert(0, '/app/src')

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    
    # Import our comprehensive bridge service
    from bridge_service import app
    
    # Configuration from environment
    host = os.getenv("BRIDGE_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))  # Use port 8001 to match docker-compose
    debug = os.getenv("DEV_MODE", "false").lower() == "true"
    
    logger.info(f"🚀 Starting Cardea Bridge Service on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info" if not debug else "debug"
    )