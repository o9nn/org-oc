#!/usr/bin/env bash
# build-opencog.sh — Build and install all 44 OpenCog packages from the
# workspace sources in dependency-tier order, mirroring unified-build.yml.
#
# Critical path: cogutil -> atomspace -> unify -> ure -> pln -> python-attic
# Tiers: T0(2) → T1(8) → T2(17) → T3(6) → T4(8) → T5(3)  = 44 packages
#
# Usage (run automatically as onCreateCommand):
#   bash .devcontainer/build-opencog.sh [WORKSPACE_DIR]
#
# All per-package build failures are non-fatal – the script continues so that
# every package that CAN build does build.

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WORKSPACE="${1:-${WORKSPACE:-/workspaces/org-oc}}"
INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"
CMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE:-Release}"
NPROC=$(nproc 2>/dev/null || echo 2)
BUILD_LOG_DIR="${BUILD_LOG_DIR:-/tmp/opencog-build-logs}"

# CMake flags — keep in sync with unified-build.yml
# Note: avoid Boost_NO_SYSTEM_PATHS/BOOST_ROOT overrides; they prevent cmake
# from finding Boost libraries in the Ubuntu multiarch path
# (/usr/lib/x86_64-linux-gnu/) and break packages that detect Boost before
# loading cogutil's cmake modules (e.g. atomspace-rpc, atomspace-websockets).
CMAKE_EXTRA_FLAGS=(
    "-DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX}"
    "-DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

BUILT=(); FAILED=(); SKIPPED=()

log()   { echo -e "${BLUE}[opencog]${NC} $*"; }
ok()    { echo -e "${GREEN}[  OK  ]${NC} $*"; }
warn()  { echo -e "${YELLOW}[ WARN ]${NC} $*"; }
fail()  { echo -e "${RED}[ FAIL ]${NC} $*"; }
header(){ echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }

mkdir -p "${BUILD_LOG_DIR}"

# build_cmake <package-name>
# Builds the package at ${WORKSPACE}/<package-name> using CMake and installs
# it to INSTALL_PREFIX.  Returns 0 on success, 1 on failure.
build_cmake() {
    local pkg="$1"
    local src="${WORKSPACE}/${pkg}"
    local bld="/tmp/oc-build/${pkg}"
    local log_base="${BUILD_LOG_DIR}/${pkg}"

    if [ ! -d "${src}" ]; then
        warn "Source not found: ${src} — skipping ${pkg}"
        SKIPPED+=("${pkg}")
        return 0
    fi

    log "Building ${pkg} …"
    mkdir -p "${bld}"

    # cmake configure (must be run from the build directory)
    if ! ( cd "${bld}" && cmake "${src}" "${CMAKE_EXTRA_FLAGS[@]}" ) \
            > "${log_base}-cmake.log" 2>&1; then
        fail "${pkg}: cmake configure failed (see ${log_base}-cmake.log)"
        FAILED+=("${pkg}")
        return 1
    fi

    # make
    if ! make -C "${bld}" -j"${NPROC}" \
            > "${log_base}-make.log" 2>&1; then
        fail "${pkg}: make failed (see ${log_base}-make.log)"
        FAILED+=("${pkg}")
        return 1
    fi

    # install (needs write access to INSTALL_PREFIX)
    # Use "cmake --install" instead of "make install" so that packages with
    # no install() rules (stub/placeholder CMakeLists.txt) succeed silently
    # instead of failing with "No rule to make target 'install'".
    if ! sudo cmake --install "${bld}" \
            > "${log_base}-install.log" 2>&1; then
        fail "${pkg}: cmake --install failed (see ${log_base}-install.log)"
        FAILED+=("${pkg}")
        return 1
    fi

    sudo ldconfig
    ok "${pkg}"
    BUILT+=("${pkg}")
    return 0
}

# build_autotools <package-name>
# For packages that use autotools (currently only link-grammar).
build_autotools() {
    local pkg="$1"
    local src="${WORKSPACE}/${pkg}"
    local bld="/tmp/oc-build/${pkg}"
    local log_base="${BUILD_LOG_DIR}/${pkg}"

    if [ ! -d "${src}" ]; then
        warn "Source not found: ${src} — skipping ${pkg}"
        SKIPPED+=("${pkg}")
        return 0
    fi

    log "Building ${pkg} (autotools) …"
    mkdir -p "${bld}"

    # autogen
    if [ -f "${src}/autogen.sh" ]; then
        if ! ( cd "${src}" && bash autogen.sh --no-configure ) \
                > "${log_base}-autogen.log" 2>&1; then
            warn "${pkg}: autogen.sh had issues — continuing anyway (see ${log_base}-autogen.log)"
        fi
    fi

    # configure
    if ! ( cd "${bld}" && "${src}/configure" --prefix="${INSTALL_PREFIX}" ) \
            > "${log_base}-configure.log" 2>&1; then
        fail "${pkg}: configure failed (see ${log_base}-configure.log)"
        FAILED+=("${pkg}")
        return 1
    fi

    # make / install
    if ! make -C "${bld}" -j"${NPROC}" \
            > "${log_base}-make.log" 2>&1; then
        fail "${pkg}: make failed (see ${log_base}-make.log)"
        FAILED+=("${pkg}")
        return 1
    fi

    if ! sudo make -C "${bld}" install \
            > "${log_base}-install.log" 2>&1; then
        fail "${pkg}: make install failed (see ${log_base}-install.log)"
        FAILED+=("${pkg}")
        return 1
    fi

    sudo ldconfig
    ok "${pkg}"
    BUILT+=("${pkg}")
    return 0
}

# try_build_cmake / try_build_autotools  — non-fatal wrappers
try_build_cmake()      { build_cmake      "$@" || true; }
try_build_autotools()  { build_autotools  "$@" || true; }

# ---------------------------------------------------------------------------
# Main build sequence — tiers mirror unified-build.yml
# ---------------------------------------------------------------------------
log "OpenCog devcontainer build starting"
log "Workspace : ${WORKSPACE}"
log "Install   : ${INSTALL_PREFIX}"
log "Parallelism: ${NPROC} jobs"
log "Build logs: ${BUILD_LOG_DIR}"

# -----------------------------------------------------------------------
# Tier 0 — no OpenCog dependencies
# -----------------------------------------------------------------------
header "Tier 0 — cogutil, link-grammar"
try_build_cmake     cogutil
try_build_autotools link-grammar

# -----------------------------------------------------------------------
# Tier 1 — depends on cogutil (and/or no OpenCog deps)
# -----------------------------------------------------------------------
header "Tier 1 — atomspace, moses, profile, language-learning, external-tools, ocpkg, relex, motor"
try_build_cmake atomspace
try_build_cmake moses
try_build_cmake profile
try_build_cmake language-learning
try_build_cmake external-tools
try_build_cmake ocpkg
try_build_cmake relex
try_build_cmake motor

# -----------------------------------------------------------------------
# Tier 2 — depends on cogutil + atomspace
# atomspace-storage and unify are built first because T3 depends on them.
# -----------------------------------------------------------------------
header "Tier 2 — atomspace-storage, unify, spacetime, and other T2 packages"
try_build_cmake atomspace-storage
try_build_cmake unify
try_build_cmake spacetime
try_build_cmake agi-bio
try_build_cmake atomspace-agents
try_build_cmake atomspace-rpc
try_build_cmake cheminformatics
try_build_cmake generate
try_build_cmake matrix
try_build_cmake pattern-index
try_build_cmake sensory
try_build_cmake vision
try_build_cmake benchmark
try_build_cmake atomspace-ipfs
try_build_cmake atomspace-websockets
try_build_cmake atomspace-metta
try_build_cmake atomspace-dht

# -----------------------------------------------------------------------
# Tier 3 — depends on T2 packages
# -----------------------------------------------------------------------
header "Tier 3 — atomspace-bridge, atomspace-pgres, atomspace-rocks, cogserver, lg-atomese, ure"
try_build_cmake atomspace-bridge
try_build_cmake atomspace-pgres
try_build_cmake atomspace-rocks
try_build_cmake cogserver
try_build_cmake lg-atomese
try_build_cmake ure

# -----------------------------------------------------------------------
# Tier 4 — depends on T3 packages
# -----------------------------------------------------------------------
header "Tier 4 — asmoses, atomspace-cog, atomspace-restful, attention, learn, miner, pln, visualization"
try_build_cmake asmoses
try_build_cmake atomspace-cog
try_build_cmake atomspace-restful
try_build_cmake attention
try_build_cmake learn
try_build_cmake miner
try_build_cmake pln
try_build_cmake visualization

# -----------------------------------------------------------------------
# Tier 5 — depends on T4 packages (critical path terminus)
# -----------------------------------------------------------------------
header "Tier 5 — python-attic, dimensional-embedding, opencog"
try_build_cmake python-attic
try_build_cmake dimensional-embedding
try_build_cmake opencog

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
TOTAL=$(( ${#BUILT[@]} + ${#FAILED[@]} + ${#SKIPPED[@]} ))
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  OpenCog build summary (${TOTAL} packages)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
_built_str=$([ ${#BUILT[@]}   -gt 0 ] && echo "${BUILT[*]}"   || echo "none")
_failed_str=$([ ${#FAILED[@]} -gt 0 ] && echo "${FAILED[*]}"  || echo "none")
_skip_str=$([ ${#SKIPPED[@]}  -gt 0 ] && echo "${SKIPPED[*]}" || echo "none")
echo -e "  ${GREEN}Built   : ${#BUILT[@]}${NC}  — ${_built_str}"
echo -e "  ${RED}Failed  : ${#FAILED[@]}${NC}  — ${_failed_str}"
echo -e "  ${YELLOW}Skipped : ${#SKIPPED[@]}${NC}  — ${_skip_str}"
echo ""

if [ ${#BUILT[@]} -eq 0 ]; then
    warn "No packages were built successfully."
    warn "Check build logs in ${BUILD_LOG_DIR}"
else
    ok "OpenCog devcontainer environment is ready!"
    log "Run 'cogserver' to start the CogServer (port 17001)."
    log "Run 'guile' and load opencog modules to use AtomSpace."
fi
