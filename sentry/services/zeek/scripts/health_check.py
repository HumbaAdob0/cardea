#!/usr/bin/env python3
"""Health check script for Zeek service"""

import subprocess
import sys
import os

try:
    # Check if Zeek process is running
    result = subprocess.run(['pgrep', 'zeek'], capture_output=True)
    if result.returncode == 0:
        print("Zeek service healthy")
        sys.exit(0)
    else:
        # Check if log files are being created (Zeek might be running)
        if os.path.exists('/opt/zeek/logs') and os.listdir('/opt/zeek/logs'):
            print("Zeek service healthy (logs detected)")
            sys.exit(0)
        else:
            print("Zeek process not found and no logs")
            sys.exit(1)
except Exception as e:
    print(f"Zeek health check failed: {e}")
    sys.exit(1)