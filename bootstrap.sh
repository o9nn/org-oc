#!/bin/bash
#
# OpenCog Bootstrap Script
#
# One-command setup for new developers. Installs dependencies and builds core packages.
#
# Usage:
#   ./bootstrap.sh           # Install deps + build core packages
#   ./bootstrap.sh --full    # Install deps + build everything
#   ./bootstrap.sh --minimal # Install deps + build cogutil/atomspace only
#   ./bootstrap.sh --deps    # Install dependencies only
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[BOOTSTRAP]${NC} $1"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# Default options
MODE="default"
DEPS_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            MODE="full"
            shift
            ;;
        --minimal)
            MODE="minimal"
            shift
            ;;
        --deps|--deps-only)
            DEPS_ONLY=true
            shift
            ;;
        --help|-h)
            cat << EOF
OpenCog Bootstrap Script

Usage: $(basename "$0") [OPTIONS]

Options:
  --minimal    Build only cogutil and atomspace
  --full       Build all available packages
  --deps       Install dependencies only (no build)
  --help       Show this help

Examples:
  $(basename "$0")           # Install deps + build core
  $(basename "$0") --full    # Install deps + build everything
  $(basename "$0") --deps    # Install dependencies only
EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

log "OpenCog Bootstrap"
log "================="
echo ""

# Check OS
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    log_info "Detected OS: $PRETTY_NAME"
else
    log_info "OS detection failed, assuming Ubuntu-compatible"
fi

# Install dependencies
log "Step 1: Installing system dependencies..."
if [[ -f scripts/install-deps-ubuntu.sh ]]; then
    if [[ "$MODE" == "minimal" ]]; then
        sudo scripts/install-deps-ubuntu.sh --minimal
    else
        sudo scripts/install-deps-ubuntu.sh
    fi
else
    log_info "Dependency installer not found, please install manually"
fi

if [[ "$DEPS_ONLY" == true ]]; then
    log "Dependencies installed. Use ./scripts/build-opencog.sh to build."
    exit 0
fi

echo ""
log "Step 2: Building OpenCog packages..."

# Build based on mode
case $MODE in
    minimal)
        ./scripts/build-opencog.sh --tier 1 --install
        ;;
    full)
        ./scripts/build-opencog.sh --install
        ;;
    *)
        # Default: build core packages (tiers 0-3)
        ./scripts/build-opencog.sh --tier 3 --install
        ;;
esac

echo ""
log "✅ Bootstrap complete!"
log_info ""
log_info "What's next:"
log_info "  • Run tests: cd build/cogutil-build && make test"
log_info "  • Build more: ./scripts/build-opencog.sh --tier 5"
log_info "  • Full build: ./scripts/build-opencog.sh --install"
log_info ""
log_info "Documentation: CMAKE_BUILD_GUIDE.md"
