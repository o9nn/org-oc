#!/bin/bash
#
# OpenCog Build Orchestrator Script
# 
# This script manages the complete build process for all OpenCog packages
# with proper dependency ordering, parallel builds, and progress tracking.
#
# Usage: ./build-opencog.sh [OPTIONS]
#   --tier N          Build up to tier N (0-6)
#   --package PKG     Build specific package and its dependencies
#   --skip PKG        Skip specific packages (comma-separated)
#   --parallel N      Max parallel jobs (default: nproc)
#   --install         Install after building
#   --test            Run tests after building
#   --clean           Clean build directories first
#   --dry-run         Show what would be built without building
#   --verbose         Enable verbose output
#   --help            Show this help message
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}/.."
BUILD_ROOT="${REPO_ROOT}/build"
INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"
CMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE:-Release}"
STATUS_FILE="${BUILD_ROOT}/build-status.json"
LOG_DIR="${BUILD_ROOT}/logs"

# Default options
MAX_TIER=6
TARGET_PACKAGE=""
SKIP_PACKAGES=""
PARALLEL_JOBS=$(nproc 2>/dev/null || echo 4)
DO_INSTALL=false
DO_TEST=false
DO_CLEAN=false
DRY_RUN=false
VERBOSE=false

# Build order by tier (generated from dependency analysis)
declare -A TIER_PACKAGES=(
    [0]="cogutil link-grammar external-tools ocpkg language-learning blender_api_msgs"
    [1]="atomspace moses"
    [2]="atomspace-storage unify spacetime generate pattern-index atomspace-agents atomspace-rpc atomspace-websockets atomspace-ipfs atomspace-metta atomspace-dht atomspace-bridge sensory vision agi-bio cheminformatics TinyCog"
    [3]="atomspace-rocks atomspace-pgres cogserver lg-atomese ure atomese-simd"
    [4]="attention learn miner matrix dimensional-embedding"
    [5]="pln asmoses visualization atomspace-cog atomspace-restful"
    [6]="opencog python-attic benchmark"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Timing
START_TIME=$(date +%s)

# Help function
show_help() {
    cat << EOF
OpenCog Build Orchestrator

Usage: $(basename "$0") [OPTIONS]

Options:
  --tier N          Build up to tier N (0-6)
                    Tier 0: Foundation (cogutil, moses, link-grammar, etc.)
                    Tier 1: Core (atomspace)
                    Tier 2: Extensions (atomspace-*, unify, spacetime, etc.)
                    Tier 3: Storage & Logic (cogserver, ure, atomspace-rocks, etc.)
                    Tier 4: Cognitive (attention, learn, miner, etc.)
                    Tier 5: Advanced (pln, asmoses, visualization, etc.)
                    Tier 6: Integration (opencog, python-attic, benchmark)
                    
  --package PKG     Build specific package and its dependencies
  --skip PKG        Skip specific packages (comma-separated)
  --parallel N      Max parallel jobs (default: $(nproc))
  --install         Install packages after building
  --test            Run tests after building
  --clean           Clean build directories first
  --dry-run         Show what would be built without building
  --verbose         Enable verbose output
  --help            Show this help message

Examples:
  $(basename "$0")                    # Build all packages
  $(basename "$0") --tier 2           # Build tiers 0-2 only
  $(basename "$0") --package pln      # Build pln and dependencies
  $(basename "$0") --clean --install  # Clean build and install
  $(basename "$0") --dry-run          # Preview build order

Environment Variables:
  INSTALL_PREFIX    Installation prefix (default: /usr/local)
  CMAKE_BUILD_TYPE  Build type (default: Release)
  
EOF
}

# Logging functions
log() {
    echo -e "${GREEN}[BUILD]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
    fi
}

# Initialize status file
init_status() {
    mkdir -p "${BUILD_ROOT}" "${LOG_DIR}"
    cat > "${STATUS_FILE}" << EOF
{
    "start_time": "$(date -Iseconds)",
    "status": "running",
    "packages": {}
}
EOF
}

# Update package status
update_status() {
    local pkg=$1
    local status=$2
    local duration=$3
    
    # Use Python for JSON manipulation (more reliable than jq)
    python3 << EOF
import json
import os

status_file = "${STATUS_FILE}"
try:
    with open(status_file, 'r') as f:
        data = json.load(f)
except:
    data = {"packages": {}}

data["packages"]["$pkg"] = {
    "status": "$status",
    "duration": "$duration",
    "timestamp": "$(date -Iseconds)"
}

with open(status_file, 'w') as f:
    json.dump(data, f, indent=2)
EOF
}

# Check if package has CMakeLists.txt
has_cmake() {
    local pkg=$1
    [ -f "${REPO_ROOT}/${pkg}/CMakeLists.txt" ]
}

# Check if package uses autotools
has_autotools() {
    local pkg=$1
    [ -f "${REPO_ROOT}/${pkg}/configure.ac" ] || [ -f "${REPO_ROOT}/${pkg}/autogen.sh" ]
}

# Build a single package
build_package() {
    local pkg=$1
    local pkg_start=$(date +%s)
    local build_dir="${BUILD_ROOT}/${pkg}-build"
    local log_file="${LOG_DIR}/${pkg}.log"
    
    log "Building: ${pkg}"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "  [DRY-RUN] Would build ${pkg}"
        return 0
    fi
    
    # Check if package exists
    if [ ! -d "${REPO_ROOT}/${pkg}" ]; then
        log_warn "Package directory not found: ${pkg}"
        update_status "$pkg" "skipped" "0"
        return 0
    fi
    
    # Clean if requested
    if [ "$DO_CLEAN" = true ] && [ -d "$build_dir" ]; then
        log_debug "Cleaning ${build_dir}"
        rm -rf "$build_dir"
    fi
    
    mkdir -p "$build_dir"
    
    # Build based on build system
    if has_cmake "$pkg"; then
        log_debug "Using CMake for ${pkg}"
        (
            cd "$build_dir"
            cmake "${REPO_ROOT}/${pkg}" \
                -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}" \
                -DCMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE}" \
                -DCMAKE_MODULE_PATH="${INSTALL_PREFIX}/lib/cmake" \
                2>&1 | tee -a "$log_file"
            
            make -j"${PARALLEL_JOBS}" 2>&1 | tee -a "$log_file"
            
            if [ "$DO_INSTALL" = true ]; then
                sudo make install 2>&1 | tee -a "$log_file"
                sudo ldconfig
            fi
            
            if [ "$DO_TEST" = true ]; then
                make test 2>&1 | tee -a "$log_file" || true
            fi
        )
    elif has_autotools "$pkg"; then
        log_debug "Using autotools for ${pkg}"
        (
            cd "${REPO_ROOT}/${pkg}"
            if [ -f "autogen.sh" ]; then
                ./autogen.sh --no-configure 2>&1 | tee -a "$log_file" || true
            fi
            
            cd "$build_dir"
            "${REPO_ROOT}/${pkg}/configure" \
                --prefix="${INSTALL_PREFIX}" \
                2>&1 | tee -a "$log_file"
            
            make -j"${PARALLEL_JOBS}" 2>&1 | tee -a "$log_file"
            
            if [ "$DO_INSTALL" = true ]; then
                sudo make install 2>&1 | tee -a "$log_file"
                sudo ldconfig
            fi
        )
    else
        log_warn "Unknown build system for ${pkg}, skipping"
        update_status "$pkg" "skipped" "0"
        return 0
    fi
    
    local pkg_end=$(date +%s)
    local pkg_duration=$((pkg_end - pkg_start))
    
    log "✅ Completed: ${pkg} (${pkg_duration}s)"
    update_status "$pkg" "success" "$pkg_duration"
}

# Get dependencies for a package
get_dependencies() {
    local pkg=$1
    # Use the dependency analyzer if available
    if [ -f "${REPO_ROOT}/build/dependency-graph.json" ]; then
        python3 -c "
import json
with open('${REPO_ROOT}/build/dependency-graph.json') as f:
    data = json.load(f)
deps = data.get('packages', {}).get('$pkg', {}).get('internal_dependencies', [])
print(' '.join(deps))
"
    fi
}

# Build a specific package with its dependencies
build_with_deps() {
    local target=$1
    local deps=$(get_dependencies "$target")
    
    log_info "Building ${target} with dependencies: ${deps:-none}"
    
    # Build dependencies first
    for dep in $deps; do
        if ! is_skipped "$dep"; then
            build_with_deps "$dep"
        fi
    done
    
    # Build the target
    if ! is_skipped "$target"; then
        build_package "$target"
    fi
}

# Check if package should be skipped
is_skipped() {
    local pkg=$1
    [[ ",$SKIP_PACKAGES," == *",$pkg,"* ]]
}

# Main build function
main_build() {
    init_status
    
    log_info "OpenCog Build Orchestrator"
    log_info "=========================="
    log_info "Build type: ${CMAKE_BUILD_TYPE}"
    log_info "Install prefix: ${INSTALL_PREFIX}"
    log_info "Max parallel jobs: ${PARALLEL_JOBS}"
    log_info "Build tiers: 0-${MAX_TIER}"
    
    if [ -n "$SKIP_PACKAGES" ]; then
        log_info "Skipping packages: ${SKIP_PACKAGES}"
    fi
    
    echo ""
    
    # Build specific package with dependencies
    if [ -n "$TARGET_PACKAGE" ]; then
        build_with_deps "$TARGET_PACKAGE"
    else
        # Build by tier
        for tier in $(seq 0 $MAX_TIER); do
            local packages=${TIER_PACKAGES[$tier]}
            
            if [ -z "$packages" ]; then
                continue
            fi
            
            log_info "Building Tier ${tier}: ${packages}"
            
            for pkg in $packages; do
                if is_skipped "$pkg"; then
                    log_info "Skipping ${pkg}"
                    continue
                fi
                
                if has_cmake "$pkg" || has_autotools "$pkg"; then
                    build_package "$pkg" || {
                        log_error "Failed to build ${pkg}"
                        update_status "$pkg" "failed" "0"
                        # Continue to next package
                    }
                else
                    log_debug "Skipping ${pkg} (no build system)"
                fi
            done
            
            echo ""
        done
    fi
    
    # Summary
    local end_time=$(date +%s)
    local total_duration=$((end_time - START_TIME))
    
    echo ""
    log_info "Build Complete!"
    log_info "Total time: ${total_duration}s ($(( total_duration / 60 ))m $(( total_duration % 60 ))s)"
    log_info "Status file: ${STATUS_FILE}"
    log_info "Logs directory: ${LOG_DIR}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tier)
            MAX_TIER="$2"
            shift 2
            ;;
        --package)
            TARGET_PACKAGE="$2"
            shift 2
            ;;
        --skip)
            SKIP_PACKAGES="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL_JOBS="$2"
            shift 2
            ;;
        --install)
            DO_INSTALL=true
            shift
            ;;
        --test)
            DO_TEST=true
            shift
            ;;
        --clean)
            DO_CLEAN=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
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

# Run main build
main_build
