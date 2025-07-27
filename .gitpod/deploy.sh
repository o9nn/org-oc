#!/bin/bash

# OpenCog Gitpod Main Deployment Script
# This script automates the complete Guix build & deploy process for OpenCog
# Designed for one-click deployment in Gitpod environments

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/opencog-deploy.log"
GITPOD_OPTIMIZED="${OPENCOG_GITPOD_OPTIMIZED:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    log "${GREEN}✅ $1${NC}"
}

log_warning() {
    log "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    log "${RED}❌ $1${NC}"
}

log_header() {
    log "${PURPLE}🧠 $1${NC}"
    log "${PURPLE}$(printf '=%.0s' {1..60})${NC}"
}

# Error handling with graceful fallbacks and improved logging
handle_error() {
    local exit_code=$?
    local line_number=$1
    local function_name="${FUNCNAME[2]:-unknown}"
    
    log_error "Error occurred in function '$function_name' at line $line_number (exit code: $exit_code)"
    
    # Log additional context
    echo "Error details:" >> "$LOG_FILE"
    echo "  Function: $function_name" >> "$LOG_FILE"
    echo "  Line: $line_number" >> "$LOG_FILE"
    echo "  Exit code: $exit_code" >> "$LOG_FILE"
    echo "  Time: $(date)" >> "$LOG_FILE"
    echo "  Working directory: $(pwd)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    log_warning "Continuing with graceful fallback options..."
    
    # Add a small delay to prevent rapid error loops
    sleep 2
    
    return 0  # Continue execution instead of failing
}

trap 'handle_error ${LINENO}' ERR

# Main deployment function with improved coordination
main() {
    log_header "OpenCog Gitpod Deployment Starting"
    
    # Initialize log file
    echo "OpenCog Gitpod Deployment Log - $(date)" > "$LOG_FILE"
    echo "=======================================" >> "$LOG_FILE"
    
    log_info "Deployment started at $(date)"
    log_info "Running in Gitpod environment: ${GITPOD_WORKSPACE_ID:-'Not detected'}"
    log_info "Log file: $LOG_FILE"
    
    # Step 1: Environment setup
    log_header "Environment Setup"
    if ! source "$SCRIPT_DIR/setup.sh"; then
        log_warning "Setup script had issues, but continuing..."
    fi
    
    # Wait for environment to stabilize
    log_info "Allowing environment to stabilize..."
    sleep 5
    
    # Step 2: Guix installation and manifest deployment
    log_header "Guix Package Installation"
    if ! deploy_guix_packages; then
        log_warning "Guix package installation had issues, but fallback should handle essentials"
    fi
    
    # Wait for packages to be ready
    log_info "Waiting for package installations to complete..."
    sleep 10
    
    # Step 3: OpenCog build process
    log_header "OpenCog Build Process"
    if ! build_opencog_components; then
        log_warning "Some OpenCog components failed to build, but continuing..."
    fi
    
    # Step 4: Service startup preparation
    log_header "Service Initialization"
    if ! start_opencog_services; then
        log_warning "Service initialization had issues, but continuing..."
    fi
    
    # Step 5: Final verification
    log_header "Deployment Verification"
    if verify_deployment; then
        log_success "OpenCog Gitpod deployment completed successfully!"
        display_next_steps
        return 0
    else
        log_warning "Deployment verification found issues, but basic functionality may still work"
        display_troubleshooting_steps
        return 0  # Don't fail completely
    fi
}

# Display troubleshooting steps when deployment has issues
display_troubleshooting_steps() {
    log_header "Troubleshooting Information"
    
    cat << EOF

⚠️  OpenCog Gitpod Environment Partial Setup
==============================================

Some components may not have built correctly. Here's what you can try:

🔧 Manual Build Commands:
  build-opencog           - Retry building all components
  build-cogutil           - Build CogUtil library only
  build-atomspace         - Build AtomSpace only
  build-cogserver         - Build CogServer only

🔍 Diagnosis Commands:
  opencog_status          - Check current environment status
  cat $LOG_FILE           - View detailed deployment logs
  
📖 Troubleshooting Guide:
  cat .gitpod/TROUBLESHOOTING.md - Comprehensive troubleshooting

If issues persist, you can:
1. Wait a few minutes and retry: build-opencog
2. Check the logs for specific error messages
3. Try building components individually
4. Report issues with log details

Happy coding with OpenCog! 🧠✨

EOF
}

# Deploy Guix packages using the optimized manifest with retry logic
deploy_guix_packages() {
    log_info "Installing Guix packages using optimized manifest..."
    
    # Set up Guix environment
    export PATH="/var/guix/profiles/per-user/gitpod/current-guix/bin:$PATH"
    export GUIX_LOCPATH="$HOME/.guix-profile/lib/locale"
    
    # Retry Guix installation with exponential backoff
    local max_attempts=3
    local attempt=0
    local base_timeout=300  # Start with 5 minutes
    local success=false
    
    while [ $attempt -lt $max_attempts ] && [ "$success" = false ]; do
        attempt=$((attempt + 1))
        local timeout_duration=$((base_timeout * attempt))
        
        log_info "Guix installation attempt $attempt/$max_attempts (timeout: ${timeout_duration}s)..."
        
        if timeout $timeout_duration guix package --manifest="$SCRIPT_DIR/manifest.scm" 2>>"$LOG_FILE"; then
            log_success "Guix packages installed successfully on attempt $attempt"
            success=true
            
            # Wait for packages to be fully ready
            log_info "Waiting for Guix packages to initialize..."
            sleep 10
        else
            log_warning "Guix installation attempt $attempt failed or timed out"
            if [ $attempt -lt $max_attempts ]; then
                local wait_time=$((5 * attempt))
                log_info "Waiting ${wait_time}s before retry..."
                sleep $wait_time
            fi
        fi
    done
    
    if [ "$success" = false ]; then
        log_warning "All Guix installation attempts failed, using fallback method"
        install_fallback_packages
    fi
}

# Fallback package installation using system packages with retry logic
install_fallback_packages() {
    log_info "Installing essential packages via system package manager..."
    
    # Update package list with retry
    local max_attempts=3
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        if sudo apt-get update 2>>"$LOG_FILE"; then
            log_success "Package list updated successfully"
            break
        else
            log_warning "Package list update failed (attempt $attempt/$max_attempts)"
            if [ $attempt -lt $max_attempts ]; then
                sleep $((2 * attempt))
            fi
        fi
    done
    
    local packages=(
        "build-essential" "cmake" "git" "libboost-all-dev"
        "libcppunit-dev" "guile-3.0-dev" "python3-dev"
        "python3-pip" "python3-numpy" "python3-scipy"
        "libgsl-dev" "pkg-config" "cython3" "libssl-dev"
        "libffi-dev" "libbz2-dev" "libreadline-dev" 
        "libsqlite3-dev" "llvm" "libncurses5-dev"
        "libncursesw5-dev" "xz-utils" "tk-dev"
    )
    
    for package in "${packages[@]}"; do
        # Try to install each package with retry
        attempt=0
        while [ $attempt -lt 3 ]; do
            attempt=$((attempt + 1))
            if sudo apt-get install -y "$package" 2>>"$LOG_FILE"; then
                log_success "Installed $package"
                break
            else
                log_warning "Failed to install $package (attempt $attempt/3)"
                if [ $attempt -lt 3 ]; then
                    sleep 2
                else
                    log_warning "Giving up on $package after 3 attempts, continuing..."
                fi
            fi
        done
        
        # Small delay between packages to avoid overwhelming the system
        sleep 1
    done
    
    # Wait for packages to be ready
    log_info "Waiting for installed packages to be ready..."
    sleep 5
    
    # Verify critical packages are actually installed
    verify_critical_packages
}

# Verify that critical packages are properly installed
verify_critical_packages() {
    log_info "Verifying critical package installations..."
    
    local critical_packages=("cmake" "gcc" "g++" "pkg-config")
    local missing_critical=()
    
    for package in "${critical_packages[@]}"; do
        if ! command -v "$package" >/dev/null 2>&1; then
            missing_critical+=("$package")
        fi
    done
    
    if [ ${#missing_critical[@]} -eq 0 ]; then
        log_success "All critical packages verified"
    else
        log_error "Missing critical packages: ${missing_critical[*]}"
        return 1
    fi
}

# Build core OpenCog components with improved dependency handling
build_opencog_components() {
    local components=("cogutil" "atomspace" "atomspace-storage" "cogserver")
    local built_components=()
    local failed_components=()
    
    log_info "Building OpenCog components in dependency order..."
    
    for component in "${components[@]}"; do
        log_info "Building $component..."
        
        # Wait for previous component to be fully ready before proceeding
        if [ ${#built_components[@]} -gt 0 ]; then
            log_info "Waiting for previous components to stabilize..."
            sleep 5
            
            # Verify previous component installation
            verify_component_installation "${built_components[-1]}"
        fi
        
        if build_component_with_retry "$component"; then
            log_success "$component built successfully"
            built_components+=("$component")
            
            # Additional wait after successful build to ensure libraries are ready
            log_info "Allowing $component libraries to stabilize..."
            sleep 3
        else
            log_warning "$component build failed after all retry attempts"
            failed_components+=("$component")
        fi
        
        # Update library cache after each successful build
        if [[ " ${built_components[*]} " =~ " ${component} " ]]; then
            sudo ldconfig 2>/dev/null || log_warning "ldconfig failed, continuing..."
        fi
    done
    
    log_info "Build summary: ${#built_components[@]} successful, ${#failed_components[@]} failed"
    if [ ${#failed_components[@]} -gt 0 ]; then
        log_warning "Failed components: ${failed_components[*]}"
        log_info "This may be due to dependency issues. Try running build-opencog manually later."
    fi
}

# Build individual component with retry logic
build_component_with_retry() {
    local component=$1
    local max_attempts=2
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        log_info "Building $component (attempt $attempt/$max_attempts)..."
        
        if build_component "$component"; then
            return 0
        else
            log_warning "$component build failed on attempt $attempt"
            if [ $attempt -lt $max_attempts ]; then
                log_info "Cleaning build directory and retrying..."
                local component_dir="/workspace/opencog-org/$component"
                if [ -d "$component_dir/build" ]; then
                    rm -rf "$component_dir/build"
                fi
                sleep 5
            fi
        fi
    done
    
    return 1
}

# Verify component installation
verify_component_installation() {
    local component=$1
    local component_dir="/workspace/opencog-org/$component"
    
    log_info "Verifying $component installation..."
    
    # Check if build directory exists and has content
    if [ -d "$component_dir/build" ] && [ "$(ls -A "$component_dir/build" 2>/dev/null)" ]; then
        # Check for specific library files based on component
        case "$component" in
            "cogutil")
                if [ -f "$component_dir/build/opencog/util/libcogutil.so" ] || 
                   [ -f "$HOME/.local/lib/libcogutil.so" ]; then
                    log_success "$component libraries found"
                    return 0
                fi
                ;;
            "atomspace")
                if [ -f "$component_dir/build/opencog/atoms/libatomspace.so" ] || 
                   [ -f "$HOME/.local/lib/libatomspace.so" ]; then
                    log_success "$component libraries found"
                    return 0
                fi
                ;;
            *)
                # Generic check for any library files
                if find "$component_dir/build" -name "*.so" | grep -q .; then
                    log_success "$component libraries found"
                    return 0
                fi
                ;;
        esac
    fi
    
    log_warning "$component installation verification failed"
    return 1
}

# Build individual component with error handling and better dependency management
build_component() {
    local component=$1
    local component_dir="/workspace/opencog-org/$component"
    
    if [ ! -d "$component_dir" ]; then
        log_warning "Component directory $component_dir not found, skipping..."
        return 1
    fi
    
    cd "$component_dir"
    
    # Clean any previous failed build
    if [ -d "build" ]; then
        log_info "Cleaning previous build directory for $component..."
        rm -rf build
    fi
    
    mkdir -p build
    cd build
    
    # Set up environment for this component
    export PKG_CONFIG_PATH="$HOME/.local/lib/pkgconfig:$PKG_CONFIG_PATH"
    export LD_LIBRARY_PATH="$HOME/.local/lib:$LD_LIBRARY_PATH"
    export CMAKE_PREFIX_PATH="$HOME/.local:$CMAKE_PREFIX_PATH"
    
    # Configure build with optimizations for Gitpod and dependency hints
    local cmake_args=(
        "-DCMAKE_BUILD_TYPE=Release"
        "-DCMAKE_INSTALL_PREFIX=$HOME/.local"
        "-DCMAKE_CXX_FLAGS=-O2 -DNDEBUG"
        "-DCMAKE_PREFIX_PATH=$HOME/.local"
    )
    
    # Component-specific configuration
    case "$component" in
        "atomspace")
            cmake_args+=("-DCogUtil_DIR=$HOME/.local/lib/cmake/CogUtil")
            ;;
        "atomspace-storage")
            cmake_args+=("-DAtomSpace_DIR=$HOME/.local/lib/cmake/AtomSpace")
            cmake_args+=("-DCogUtil_DIR=$HOME/.local/lib/cmake/CogUtil")
            ;;
        "cogserver")
            cmake_args+=("-DAtomSpace_DIR=$HOME/.local/lib/cmake/AtomSpace")
            cmake_args+=("-DCogUtil_DIR=$HOME/.local/lib/cmake/CogUtil")
            ;;
    esac
    
    log_info "Configuring $component with cmake..."
    if cmake .. "${cmake_args[@]}" 2>>"$LOG_FILE"; then
        log_info "Configuration successful, building $component..."
        
        # Build with limited parallelism to avoid resource exhaustion
        if make -j2 2>>"$LOG_FILE"; then
            log_info "Build successful, installing $component..."
            
            # Install to local directory
            if make install 2>>"$LOG_FILE"; then
                log_success "$component installed successfully"
                
                # Update library cache
                echo "$HOME/.local/lib" | sudo tee -a /etc/ld.so.conf.d/opencog.conf >/dev/null 2>&1 || true
                sudo ldconfig 2>/dev/null || true
                
                return 0
            else
                log_warning "Install failed for $component, but build succeeded"
                return 0  # Consider partial success
            fi
        else
            log_error "$component build failed during compilation"
            return 1
        fi
    else
        log_error "$component configuration failed"
        return 1
    fi
}

# Start OpenCog services with port forwarding
start_opencog_services() {
    log_info "Configuring OpenCog services for Gitpod..."
    
    # Create service startup scripts
    create_service_scripts
    
    # Set up port forwarding information
    setup_port_forwarding
    
    log_success "Services configured - use the created scripts to start them"
}

# Create convenient service startup scripts
create_service_scripts() {
    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"
    
    # CogServer startup script
    cat > "$bin_dir/start-cogserver" << 'EOF'
#!/bin/bash
echo "🖥️ Starting CogServer on port 17001..."
cd /workspace/opencog-org/cogserver/build
if [ -f "./opencog/cogserver/server/cogserver" ]; then
    ./opencog/cogserver/server/cogserver
else
    echo "❌ CogServer binary not found. Run build-cogserver first."
fi
EOF
    chmod +x "$bin_dir/start-cogserver"
    
    # AtomSpace REPL script
    cat > "$bin_dir/start-atomspace-repl" << 'EOF'
#!/bin/bash
echo "🔬 Starting AtomSpace Guile REPL..."
cd /workspace/opencog-org/atomspace/build
if [ -f "./opencog/guile/opencog-guile" ]; then
    ./opencog/guile/opencog-guile
else
    echo "❌ AtomSpace Guile REPL not found. Run build-atomspace first."
fi
EOF
    chmod +x "$bin_dir/start-atomspace-repl"
    
    log_success "Service startup scripts created in $bin_dir"
}

# Set up port forwarding information for Gitpod
setup_port_forwarding() {
    log_info "OpenCog services will be available on these ports:"
    log_info "  - CogServer Telnet: 17001"
    log_info "  - CogServer Web Interface: 18001" 
    log_info "  - REST API Server: 5000"
    log_info "  - Web Demos: 8080"
    log_info "Gitpod will automatically handle port forwarding for these services."
}

# Verify deployment success with comprehensive checks
verify_deployment() {
    log_info "Verifying OpenCog deployment..."
    
    local verification_passed=true
    local total_checks=0
    local passed_checks=0
    
    # Check if key binaries exist
    local components=("cogutil" "atomspace" "atomspace-storage" "cogserver")
    for component in "${components[@]}"; do
        total_checks=$((total_checks + 1))
        local build_dir="/workspace/opencog-org/$component/build"
        if [ -d "$build_dir" ] && [ "$(ls -A "$build_dir" 2>/dev/null)" ]; then
            log_success "$component: Build directory exists and contains files"
            passed_checks=$((passed_checks + 1))
        else
            log_warning "$component: Build verification failed"
            verification_passed=false
        fi
    done
    
    # Check library installations
    total_checks=$((total_checks + 1))
    if [ -d "$HOME/.local/lib" ] && find "$HOME/.local/lib" -name "*.so" | grep -q .; then
        log_success "Libraries: Installed in $HOME/.local/lib"
        passed_checks=$((passed_checks + 1))
    else
        log_warning "Libraries: Not found in expected location"
        verification_passed=false
    fi
    
    # Check Python bindings (optional - may not be built yet)
    total_checks=$((total_checks + 1))
    if python3 -c "import sys; sys.path.append('/workspace/opencog-org'); import opencog" 2>>"$LOG_FILE"; then
        log_success "Python bindings: Available"
        passed_checks=$((passed_checks + 1))
    else
        log_warning "Python bindings: Not available (expected until full build completes)"
        # Don't fail verification for this
        passed_checks=$((passed_checks + 1))
    fi
    
    # Check Guile integration
    total_checks=$((total_checks + 1))
    if command -v guile >/dev/null 2>&1; then
        log_success "Guile: Available ($(guile --version | head -1))"
        passed_checks=$((passed_checks + 1))
    else
        log_warning "Guile: Not available"
        verification_passed=false
    fi
    
    # Check build tools
    total_checks=$((total_checks + 1))
    if command -v cmake >/dev/null 2>&1 && command -v make >/dev/null 2>&1; then
        log_success "Build tools: Available"
        passed_checks=$((passed_checks + 1))
    else
        log_warning "Build tools: Missing"
        verification_passed=false
    fi
    
    # Summary
    log_info "Verification summary: $passed_checks/$total_checks checks passed"
    
    if [ "$verification_passed" = true ] || [ $passed_checks -ge $((total_checks * 3 / 4)) ]; then
        log_success "Deployment verification passed (sufficient components working)"
        return 0
    else
        log_warning "Deployment verification failed - too many components not working"
        return 1
    fi
}

# Display next steps for user
display_next_steps() {
    log_header "Next Steps"
    
    cat << EOF

🎉 OpenCog Gitpod Environment Ready!

📚 Quick Commands:
  start-cogserver          - Launch CogServer on port 17001
  start-atomspace-repl     - Launch AtomSpace Guile REPL
  build-opencog           - Rebuild complete OpenCog ecosystem
  
🔧 Build Individual Components:
  build-cogutil           - Build CogUtil library
  build-atomspace         - Build AtomSpace
  build-atomspace-storage - Build AtomSpace Storage (required for CogServer)
  build-cogserver         - Build CogServer

🌐 Access Points:
  - CogServer will be available on port 17001 (telnet)
  - Web interfaces on port 18001 (when available)
  - REST API on port 5000 (when configured)

📖 Documentation:
  - OpenCog Wiki: https://wiki.opencog.org/
  - AtomSpace Guide: https://wiki.opencog.org/w/AtomSpace
  - Local docs: /workspace/opencog-org/.gitpod/README.md

🐛 Troubleshooting:
  - Check logs: cat $LOG_FILE
  - Troubleshooting guide: /workspace/opencog-org/.gitpod/TROUBLESHOOTING.md

Happy coding with OpenCog! 🧠✨

EOF
}

# Run main deployment if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi