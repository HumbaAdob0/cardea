# Platform Awareness Documentation

## Overview

Cardea now features dynamic platform detection and environmental awareness, ensuring true portability across different Linux distributions and hardware configurations.

## Features

### 🔍 **Dynamic Platform Detection**
- **Operating System**: Automatically detects Linux distribution and version
- **Hardware**: CPU cores, memory, and disk information  
- **Network Interfaces**: Discovers and categorizes all network interfaces
- **Docker Capabilities**: Validates Docker availability and features

### 🌐 **Network Interface Auto-Detection**
- Automatically finds suitable network interfaces for monitoring
- Prioritizes ethernet over wireless interfaces
- Filters out loopback and Docker bridge interfaces
- Supports various naming conventions (eth0, enp*, wlp*, etc.)

### ⚡ **Performance Optimization**
- **Memory-based scaling**: Adjusts service limits based on available RAM
- **CPU optimization**: Configures thread counts based on available cores
- **Distribution-specific tuning**: Optimizes for Ubuntu, Arch, CentOS, etc.

## Usage

### Quick Platform Detection
```bash
# Show full platform report
make platform-info

# Or use directly
python3 shared/utils/platform_cli.py report
```

### Automated Setup
```bash
# Platform-aware setup (replaces manual configuration)
make dev-setup

# This runs setup-platform.sh which:
# 1. Detects your platform
# 2. Generates optimized configuration 
# 3. Creates platform-specific Docker compose
# 4. Validates network interfaces
```

### Manual Platform Commands
```bash
# Get recommended network interface
python3 shared/utils/platform_cli.py interface

# Generate environment config
python3 shared/utils/platform_cli.py config

# Validate deployment readiness
python3 shared/utils/platform_cli.py validate
```

## Platform Support

### ✅ **Fully Supported**
- **Ubuntu/Debian**: libpcap optimization, high performance mode
- **Arch Linux**: Raw socket optimization, maximum performance mode
- **CentOS/RHEL/Fedora**: SELinux awareness, balanced performance mode

### 🔧 **Configuration Files Generated**

1. **`.env`** - Platform-specific environment variables
   ```bash
   ZEEK_INTERFACE=enp0s3        # Auto-detected interface
   ZEEK_PERFORMANCE_MODE=high   # Based on platform
   USE_HOST_NETWORKING=true     # If supported
   ZEEK_MEMORY_LIMIT=2g         # Based on available RAM
   ```

2. **`docker-compose.platform.yml`** - Optimized Docker configuration
   - Memory limits based on system RAM
   - CPU allocation based on available cores
   - Network mode selection (host vs bridge)

3. **`start-platform.sh`** - Platform-aware startup script

## Architecture

### Platform Detection Flow
```
System Scan → Interface Discovery → Docker Validation → Optimization Selection → Config Generation
```

### Supported Optimizations
- **Packet Capture Method**: libpcap, raw_socket, standard
- **Performance Mode**: maximum, high, balanced
- **Security Constraints**: SELinux detection and configuration
- **Resource Allocation**: Dynamic based on hardware

## Examples

### Ubuntu 22.04 with 8GB RAM
```bash
# Auto-detects:
ZEEK_INTERFACE=enp0s3
ZEEK_PERFORMANCE_MODE=high
ZEEK_MEMORY_LIMIT=2g
SURICATA_THREADS=4
USE_HOST_NETWORKING=true
```

### Arch Linux with 16GB RAM
```bash
# Auto-detects:
ZEEK_INTERFACE=wlp3s0
ZEEK_PERFORMANCE_MODE=maximum
ZEEK_MEMORY_LIMIT=4g
SURICATA_THREADS=8
USE_HOST_NETWORKING=true
```

### CentOS with SELinux
```bash
# Auto-detects:
ZEEK_INTERFACE=eth0
ZEEK_PERFORMANCE_MODE=balanced
SELINUX_ENABLED=true
DOCKER_SECURITY_OPT=--security-opt label=type:container_runtime_t
```

## Benefits

1. **Zero Manual Configuration**: No more hardcoded interface names
2. **Optimal Performance**: Platform-specific tuning automatically applied
3. **Universal Compatibility**: Works across Linux distributions
4. **Security Awareness**: Detects and configures for security frameworks
5. **Resource Efficiency**: Scales to available hardware automatically

## Migration

### From Hardcoded Setup
```bash
# Old way (hardcoded)
export ZEEK_INTERFACE=eth0
docker compose up

# New way (platform-aware)
make dev-setup          # Detects platform and generates config
cd sentry && ./start-platform.sh    # Starts with optimizations
```

The platform detection ensures Cardea works optimally whether deployed on a ThinkPad, cloud VM, or production server, automatically adapting to the environment.