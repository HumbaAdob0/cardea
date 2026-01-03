#!/usr/bin/env python3
"""Health check script for Suricata service"""

import subprocess
import sys

try:
    # Check if Suricata process is running
    result = subprocess.run(['pgrep', 'suricata'], capture_output=True)
    if result.returncode == 0:
        print("Suricata service healthy")
        sys.exit(0)
    else:
        print("Suricata process not found")
        sys.exit(1)
except Exception as e:
    print(f"Suricata health check failed: {e}")
    sys.exit(1)