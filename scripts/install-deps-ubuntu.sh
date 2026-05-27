#!/bin/bash
#
# OpenCog System Dependencies Installer for Ubuntu
#
# Supports: Ubuntu 20.04, 22.04, 24.04
#
# Usage: sudo ./install-deps-ubuntu.sh [OPTIONS]
#   --minimal     Install only core dependencies
#   --full        Install all dependencies including optional ones
#   --dev         Include development and debugging tools
#   --ros         Include ROS dependencies (requires ROS to be set up)
#   --help        Show this help message
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default options
INSTALL_MINIMAL=false
INSTALL_FULL=true
INSTALL_DEV=false
INSTALL_ROS=false

log() { echo -e "${GREEN}[INSTALL]${NC} $1"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    cat << EOF
OpenCog System Dependencies Installer for Ubuntu

Usage: sudo $(basename "$0") [OPTIONS]

Options:
  --minimal     Install only core dependencies (cogutil, atomspace)
  --full        Install all dependencies including optional ones (default)
  --dev         Include development and debugging tools
  --ros         Include ROS dependencies (requires ROS to be set up)
  --help        Show this help message

Supported Ubuntu versions:
  - Ubuntu 20.04 LTS (Focal)
  - Ubuntu 22.04 LTS (Jammy)
  - Ubuntu 24.04 LTS (Noble)

Example:
  sudo $(basename "$0")              # Full installation
  sudo $(basename "$0") --minimal    # Core dependencies only
  sudo $(basename "$0") --dev        # Full + development tools
  
EOF
}

detect_ubuntu_version() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$VERSION_ID"
    else
        echo "unknown"
    fi
}

# Core dependencies required for cogutil and atomspace
install_core() {
    log "Installing core build dependencies..."
    
    apt-get update
    apt-get install -y \
        build-essential \
        cmake \
        git \
        pkg-config \
        ccache
    
    log "Installing core libraries..."
    apt-get install -y \
        libboost-all-dev \
        guile-3.0-dev \
        cxxtest \
        binutils-dev \
        libiberty-dev
    
    log "Installing Python dependencies..."
    apt-get install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        cython3
}

# AtomSpace storage backends
install_storage() {
    log "Installing storage backend dependencies..."
    
    apt-get install -y \
        librocksdb-dev \
        libpqxx-dev \
        postgresql-client \
        unixodbc-dev \
        uuid-dev
        
    # OpenDHT for atomspace-dht (if available)
    apt-get install -y libopendht-dev || log_warn "libopendht-dev not available"
}

# Language processing dependencies
install_language() {
    log "Installing language processing dependencies..."
    
    apt-get install -y \
        flex \
        swig \
        autoconf \
        autoconf-archive \
        automake \
        libtool
}

# Server and API dependencies
install_server() {
    log "Installing server dependencies..."
    
    apt-get install -y \
        libssl-dev \
        nlohmann-json3-dev || apt-get install -y nlohmann-json-dev || true
        
    # gRPC for atomspace-rpc
    apt-get install -y \
        libgrpc++-dev \
        protobuf-compiler-grpc \
        libprotobuf-dev \
        protobuf-compiler || log_warn "gRPC not available"
}

# Computer vision and robotics
install_vision() {
    log "Installing vision and robotics dependencies..."
    
    apt-get install -y \
        libopencv-dev \
        liboctomap-dev
}

# Optional scientific computing
install_scientific() {
    log "Installing scientific computing dependencies..."
    
    apt-get install -y \
        libopenmpi-dev
}

# GUI dependencies
install_gui() {
    log "Installing GUI dependencies..."
    
    apt-get install -y \
        libgtk-3-dev
}

# Development and debugging tools
install_dev_tools() {
    log "Installing development tools..."
    
    apt-get install -y \
        valgrind \
        gdb \
        doxygen \
        graphviz \
        clang-format \
        clang-tidy \
        cppcheck
}

# ROS dependencies
install_ros_deps() {
    log "Installing ROS integration dependencies..."
    
    # Check if ROS is installed
    if [ -d /opt/ros ]; then
        apt-get install -y \
            ros-*-catkin || log_warn "catkin not available"
    else
        log_warn "ROS not found. Please install ROS first."
    fi
}

# Configure ldconfig for OpenCog libraries
configure_ldconfig() {
    log "Configuring library paths..."
    
    echo "/usr/local/lib/opencog" | tee /etc/ld.so.conf.d/opencog.conf
    ldconfig
}

# Main installation
main() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
    
    local ubuntu_version=$(detect_ubuntu_version)
    log_info "Detected Ubuntu version: ${ubuntu_version}"
    
    case "$ubuntu_version" in
        20.04|22.04|24.04)
            log_info "Ubuntu ${ubuntu_version} is supported"
            ;;
        *)
            log_warn "Ubuntu ${ubuntu_version} may not be fully supported"
            ;;
    esac
    
    log_info "Starting OpenCog dependency installation..."
    echo ""
    
    # Always install core
    install_core
    
    if [ "$INSTALL_MINIMAL" = false ]; then
        install_storage
        install_language
        install_server
        
        if [ "$INSTALL_FULL" = true ]; then
            install_vision
            install_scientific
            install_gui
        fi
    fi
    
    if [ "$INSTALL_DEV" = true ]; then
        install_dev_tools
    fi
    
    if [ "$INSTALL_ROS" = true ]; then
        install_ros_deps
    fi
    
    configure_ldconfig
    
    echo ""
    log "✅ OpenCog dependencies installed successfully!"
    log_info "You can now build OpenCog with: ./scripts/build-opencog.sh"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --minimal)
            INSTALL_MINIMAL=true
            INSTALL_FULL=false
            shift
            ;;
        --full)
            INSTALL_FULL=true
            INSTALL_MINIMAL=false
            shift
            ;;
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        --ros)
            INSTALL_ROS=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

main
