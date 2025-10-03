#
# OpenCog Organization Repository - Unified CMake Build System
#
# This CMakeLists.txt provides a unified build system for the entire OpenCog
# ecosystem. It identifies available components and provides a centralized
# way to build them, either individually or collectively.
#
# Components in this repository are designed to be built independently,
# each with their own dependencies. This unified build system provides:
# - Discovery of available components  
# - Individual component build targets
# - Collective build coordination
# - Clear reporting of what can be built
#
# Usage:
#   mkdir build && cd build
#   cmake ..                           # Configure and discover components
#   make help                          # See available targets
#   make <component>                   # Build specific component
#   make all-components               # Attempt to build all available components
#

CMAKE_MINIMUM_REQUIRED(VERSION 3.12)

# Python venv seems to need this
IF(CMAKE_VERSION VERSION_GREATER 3.31)
   CMAKE_POLICY(SET CMP0177 NEW)
ENDIF(CMAKE_VERSION VERSION_GREATER 3.31)

# Fix for modern CMake Boost module policy
IF(CMAKE_VERSION VERSION_GREATER_EQUAL 3.30)
    CMAKE_POLICY(SET CMP0167 OLD)
ENDIF()

PROJECT(opencog-org)

# ----------------------------------------------------------
# Build configuration
#

# Default build type
IF (CMAKE_BUILD_TYPE STREQUAL "")
	SET(CMAKE_BUILD_TYPE Release)
ENDIF (CMAKE_BUILD_TYPE STREQUAL "")

MESSAGE(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

# Global definitions
ADD_DEFINITIONS(-DPROJECT_SOURCE_DIR="${CMAKE_SOURCE_DIR}"
                -DPROJECT_BINARY_DIR="${CMAKE_BINARY_DIR}")

# ----------------------------------------------------------
# Component discovery and target creation
#

# Initialize tracking lists
SET(AVAILABLE_COMPONENTS "")
SET(MISSING_COMPONENTS "")

# Function to check if a component is available and create targets for it
FUNCTION(REGISTER_OPENCOG_COMPONENT component_name component_path layer)
    SET(component_full_path "${CMAKE_SOURCE_DIR}/${component_path}")
    
    IF(EXISTS "${component_full_path}/CMakeLists.txt")
        LIST(APPEND AVAILABLE_COMPONENTS "${component_name}")
        SET(AVAILABLE_COMPONENTS ${AVAILABLE_COMPONENTS} PARENT_SCOPE)
        
        # Create a target for building this component individually
        ADD_CUSTOM_TARGET(${component_name}
            COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}/${component_name}-build
            COMMENT "Building ${component_name} component"
            VERBATIM
        )
        
        # Create a target for configuring this component
        ADD_CUSTOM_TARGET(configure-${component_name}
            COMMAND ${CMAKE_COMMAND} -S ${component_full_path} -B ${CMAKE_BINARY_DIR}/${component_name}-build
            COMMENT "Configuring ${component_name} component"
            VERBATIM
        )
        
        # Create a target for installing this component
        ADD_CUSTOM_TARGET(install-${component_name}
            COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}/${component_name}-build --target install
            COMMENT "Installing ${component_name} component"
            VERBATIM
        )
        
        # Create a target for uninstalling this component (if supported)
        ADD_CUSTOM_TARGET(uninstall-${component_name}
            COMMAND sh -c "if [ -f ${CMAKE_BINARY_DIR}/${component_name}-build/install_manifest.txt ]; then xargs rm < ${CMAKE_BINARY_DIR}/${component_name}-build/install_manifest.txt; else echo 'No install manifest found for ${component_name}, cannot uninstall automatically'; fi"
            COMMENT "Uninstalling ${component_name} component"
            VERBATIM
        )
        
        # Create dependency between build and configure, and install and build
        ADD_DEPENDENCIES(${component_name} configure-${component_name})
        ADD_DEPENDENCIES(install-${component_name} ${component_name})
        
        # Track components by layer for layer-specific install targets
        SET(${layer}_LAYER_COMPONENTS ${${layer}_LAYER_COMPONENTS} ${component_name} PARENT_SCOPE)
        
        MESSAGE(STATUS "✓ Registered component: ${component_name} (${layer} layer)")
    ELSE()
        LIST(APPEND MISSING_COMPONENTS "${component_name}")
        SET(MISSING_COMPONENTS ${MISSING_COMPONENTS} PARENT_SCOPE)
        MESSAGE(STATUS "⚠ Component not available: ${component_name} (no CMakeLists.txt)")
    ENDIF()
ENDFUNCTION()

# ----------------------------------------------------------
# Register components by dependency layer
#

MESSAGE(STATUS "")
MESSAGE(STATUS "=============================================================")
MESSAGE(STATUS "OpenCog Organization Repository - Component Discovery")
MESSAGE(STATUS "=============================================================")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Foundation Layer Components ---")
REGISTER_OPENCOG_COMPONENT("cogutil" "cogutil" "Foundation")
REGISTER_OPENCOG_COMPONENT("moses" "moses" "Foundation") 
REGISTER_OPENCOG_COMPONENT("blender_api_msgs" "blender_api_msgs" "Foundation")
REGISTER_OPENCOG_COMPONENT("external-tools" "external-tools" "Foundation")
REGISTER_OPENCOG_COMPONENT("ocpkg" "ocpkg" "Foundation")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Core Layer Components ---")
REGISTER_OPENCOG_COMPONENT("atomspace" "atomspace" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-rocks" "atomspace-rocks" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-pgres" "atomspace-pgres" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-ipfs" "atomspace-ipfs" "Core") 
REGISTER_OPENCOG_COMPONENT("atomspace-websockets" "atomspace-websockets" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-restful" "atomspace-restful" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-bridge" "atomspace-bridge" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-metta" "atomspace-metta" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-rpc" "atomspace-rpc" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-cog" "atomspace-cog" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-agents" "atomspace-agents" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-dht" "atomspace-dht" "Core")
REGISTER_OPENCOG_COMPONENT("atomspace-storage" "atomspace-storage" "Core")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Logic Layer Components ---")
REGISTER_OPENCOG_COMPONENT("unify" "unify" "Logic")
REGISTER_OPENCOG_COMPONENT("ure" "ure" "Logic")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Cognitive Layer Components ---")
REGISTER_OPENCOG_COMPONENT("cogserver" "cogserver" "Cognitive")
REGISTER_OPENCOG_COMPONENT("attention" "attention" "Cognitive")
REGISTER_OPENCOG_COMPONENT("spacetime" "spacetime" "Cognitive")
REGISTER_OPENCOG_COMPONENT("pattern-index" "pattern-index" "Cognitive")
REGISTER_OPENCOG_COMPONENT("dimensional-embedding" "dimensional-embedding" "Cognitive")
REGISTER_OPENCOG_COMPONENT("profile" "profile" "Cognitive")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Advanced Layer Components ---")
REGISTER_OPENCOG_COMPONENT("pln" "pln" "Advanced")
REGISTER_OPENCOG_COMPONENT("miner" "miner" "Advanced")
REGISTER_OPENCOG_COMPONENT("asmoses" "asmoses" "Advanced")
REGISTER_OPENCOG_COMPONENT("benchmark" "benchmark" "Advanced")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Learning Layer Components ---")
REGISTER_OPENCOG_COMPONENT("learn" "learn" "Learning")
REGISTER_OPENCOG_COMPONENT("generate" "generate" "Learning")
REGISTER_OPENCOG_COMPONENT("language-learning" "language-learning" "Learning")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Language Layer Components ---")
REGISTER_OPENCOG_COMPONENT("lg-atomese" "lg-atomese" "Language")
REGISTER_OPENCOG_COMPONENT("relex" "relex" "Language")
REGISTER_OPENCOG_COMPONENT("link-grammar" "link-grammar" "Language")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Robotics Layer Components ---")
REGISTER_OPENCOG_COMPONENT("vision" "vision" "Robotics")
REGISTER_OPENCOG_COMPONENT("perception" "perception" "Robotics") 
REGISTER_OPENCOG_COMPONENT("sensory" "sensory" "Robotics")
REGISTER_OPENCOG_COMPONENT("ros-behavior-scripting" "ros-behavior-scripting" "Robotics")
REGISTER_OPENCOG_COMPONENT("robots_config" "robots_config" "Robotics")
REGISTER_OPENCOG_COMPONENT("pau2motors" "pau2motors" "Robotics")
REGISTER_OPENCOG_COMPONENT("motor" "motor" "Robotics")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Integration Layer Components ---")
REGISTER_OPENCOG_COMPONENT("opencog" "opencog" "Integration")
REGISTER_OPENCOG_COMPONENT("TinyCog" "TinyCog" "Integration")

MESSAGE(STATUS "")
MESSAGE(STATUS "--- Discovering Specialized Components ---")
REGISTER_OPENCOG_COMPONENT("visualization" "visualization" "Specialized")
REGISTER_OPENCOG_COMPONENT("cheminformatics" "cheminformatics" "Specialized")
REGISTER_OPENCOG_COMPONENT("agi-bio" "agi-bio" "Specialized")
REGISTER_OPENCOG_COMPONENT("ghost_bridge" "ghost_bridge" "Specialized")
REGISTER_OPENCOG_COMPONENT("matrix" "matrix" "Specialized")
REGISTER_OPENCOG_COMPONENT("python-attic" "python-attic" "Specialized")
REGISTER_OPENCOG_COMPONENT("atomese-simd" "atomese-simd" "Specialized")

# ----------------------------------------------------------
# Collective build targets
#

# Target to configure all available components
ADD_CUSTOM_TARGET(configure-all
    COMMENT "Configuring all available components..."
)

# Target to build all available components  
ADD_CUSTOM_TARGET(all-components
    COMMENT "Building all available components..."
)

# Target to install all available components
ADD_CUSTOM_TARGET(install-all
    COMMENT "Installing all available components..."
)

# Target to uninstall all available components  
ADD_CUSTOM_TARGET(uninstall-all
    COMMENT "Uninstalling all available components..."
)

# Add dependencies for collective targets
FOREACH(component ${AVAILABLE_COMPONENTS})
    ADD_DEPENDENCIES(configure-all configure-${component})
    ADD_DEPENDENCIES(all-components ${component})
    ADD_DEPENDENCIES(install-all install-${component})
    ADD_DEPENDENCIES(uninstall-all uninstall-${component})
ENDFOREACH()

# Layer-specific targets
FOREACH(layer Foundation Core Logic Cognitive Advanced Learning Language Robotics Integration Specialized)
    ADD_CUSTOM_TARGET(${layer}-layer
        COMMENT "Building all ${layer} layer components..."
    )
    ADD_CUSTOM_TARGET(install-${layer}-layer
        COMMENT "Installing all ${layer} layer components..."
    )
    ADD_CUSTOM_TARGET(uninstall-${layer}-layer
        COMMENT "Uninstalling all ${layer} layer components..."
    )
ENDFOREACH()

# Add layer dependencies after all components are registered
# Foundation layer components
ADD_DEPENDENCIES(Foundation-layer cogutil moses blender_api_msgs external-tools ocpkg)
ADD_DEPENDENCIES(install-Foundation-layer install-cogutil install-moses install-blender_api_msgs install-external-tools install-ocpkg)
ADD_DEPENDENCIES(uninstall-Foundation-layer uninstall-cogutil uninstall-moses uninstall-blender_api_msgs uninstall-external-tools uninstall-ocpkg)

# Core layer components  
ADD_DEPENDENCIES(Core-layer atomspace atomspace-rocks atomspace-pgres atomspace-ipfs atomspace-websockets atomspace-restful atomspace-bridge atomspace-metta atomspace-rpc atomspace-cog atomspace-agents atomspace-dht atomspace-storage)
ADD_DEPENDENCIES(install-Core-layer install-atomspace install-atomspace-rocks install-atomspace-pgres install-atomspace-ipfs install-atomspace-websockets install-atomspace-restful install-atomspace-bridge install-atomspace-metta install-atomspace-rpc install-atomspace-cog install-atomspace-agents install-atomspace-dht install-atomspace-storage)
ADD_DEPENDENCIES(uninstall-Core-layer uninstall-atomspace uninstall-atomspace-rocks uninstall-atomspace-pgres uninstall-atomspace-ipfs uninstall-atomspace-websockets uninstall-atomspace-restful uninstall-atomspace-bridge uninstall-atomspace-metta uninstall-atomspace-rpc uninstall-atomspace-cog uninstall-atomspace-agents uninstall-atomspace-dht uninstall-atomspace-storage)

# Logic layer components
ADD_DEPENDENCIES(Logic-layer unify ure)  
ADD_DEPENDENCIES(install-Logic-layer install-unify install-ure)
ADD_DEPENDENCIES(uninstall-Logic-layer uninstall-unify uninstall-ure)

# Cognitive layer components
ADD_DEPENDENCIES(Cognitive-layer cogserver attention spacetime pattern-index dimensional-embedding profile)
ADD_DEPENDENCIES(install-Cognitive-layer install-cogserver install-attention install-spacetime install-pattern-index install-dimensional-embedding install-profile)
ADD_DEPENDENCIES(uninstall-Cognitive-layer uninstall-cogserver uninstall-attention uninstall-spacetime uninstall-pattern-index uninstall-dimensional-embedding uninstall-profile)

# Advanced layer components
ADD_DEPENDENCIES(Advanced-layer pln miner asmoses benchmark)
ADD_DEPENDENCIES(install-Advanced-layer install-pln install-miner install-asmoses install-benchmark)
ADD_DEPENDENCIES(uninstall-Advanced-layer uninstall-pln uninstall-miner uninstall-asmoses uninstall-benchmark)

# Learning layer components
ADD_DEPENDENCIES(Learning-layer learn generate language-learning)
ADD_DEPENDENCIES(install-Learning-layer install-learn install-generate install-language-learning)
ADD_DEPENDENCIES(uninstall-Learning-layer uninstall-learn uninstall-generate uninstall-language-learning)

# Language layer components
ADD_DEPENDENCIES(Language-layer lg-atomese relex link-grammar)
ADD_DEPENDENCIES(install-Language-layer install-lg-atomese install-relex install-link-grammar)
ADD_DEPENDENCIES(uninstall-Language-layer uninstall-lg-atomese uninstall-relex uninstall-link-grammar)

# Robotics layer components
ADD_DEPENDENCIES(Robotics-layer vision perception sensory ros-behavior-scripting robots_config pau2motors motor)
ADD_DEPENDENCIES(install-Robotics-layer install-vision install-perception install-sensory install-ros-behavior-scripting install-robots_config install-pau2motors install-motor)
ADD_DEPENDENCIES(uninstall-Robotics-layer uninstall-vision uninstall-perception uninstall-sensory uninstall-ros-behavior-scripting uninstall-robots_config uninstall-pau2motors uninstall-motor)

# Integration layer components
ADD_DEPENDENCIES(Integration-layer opencog TinyCog)
ADD_DEPENDENCIES(install-Integration-layer install-opencog install-TinyCog)
ADD_DEPENDENCIES(uninstall-Integration-layer uninstall-opencog uninstall-TinyCog)

# Specialized layer components
ADD_DEPENDENCIES(Specialized-layer visualization cheminformatics agi-bio ghost_bridge matrix python-attic atomese-simd)
ADD_DEPENDENCIES(install-Specialized-layer install-visualization install-cheminformatics install-agi-bio install-ghost_bridge install-matrix install-python-attic install-atomese-simd)
ADD_DEPENDENCIES(uninstall-Specialized-layer uninstall-visualization uninstall-cheminformatics uninstall-agi-bio uninstall-ghost_bridge uninstall-matrix uninstall-python-attic uninstall-atomese-simd)

# ----------------------------------------------------------
# Documentation and utility targets
#

# Create a help file at configure time
SET(HELP_FILE "${CMAKE_BINARY_DIR}/help.txt")
FILE(WRITE ${HELP_FILE} "Available OpenCog components:\n")
FILE(APPEND ${HELP_FILE} "Individual components:\n")

FOREACH(component ${AVAILABLE_COMPONENTS})
    FILE(APPEND ${HELP_FILE} "  make ${component}\n")
ENDFOREACH()

FILE(APPEND ${HELP_FILE} "\nIndividual component install:\n")
FOREACH(component ${AVAILABLE_COMPONENTS})
    FILE(APPEND ${HELP_FILE} "  make install-${component}\n")
ENDFOREACH()

FILE(APPEND ${HELP_FILE} "\nIndividual component uninstall:\n")
FOREACH(component ${AVAILABLE_COMPONENTS})
    FILE(APPEND ${HELP_FILE} "  make uninstall-${component}\n")
ENDFOREACH()

FILE(APPEND ${HELP_FILE} "\nCollective targets:\n")
FILE(APPEND ${HELP_FILE} "  make configure-all   # Configure all components\n")
FILE(APPEND ${HELP_FILE} "  make all-components  # Build all components\n")
FILE(APPEND ${HELP_FILE} "  make install-all     # Install all components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-all   # Uninstall all components\n")
FILE(APPEND ${HELP_FILE} "\nLayer targets:\n")
FILE(APPEND ${HELP_FILE} "  make Foundation-layer  # Build foundation components\n")
FILE(APPEND ${HELP_FILE} "  make Core-layer      # Build core components\n")
FILE(APPEND ${HELP_FILE} "  make Logic-layer     # Build logic components\n")
FILE(APPEND ${HELP_FILE} "  make Cognitive-layer # Build cognitive components\n")
FILE(APPEND ${HELP_FILE} "  make Advanced-layer  # Build advanced components\n")
FILE(APPEND ${HELP_FILE} "  make Learning-layer  # Build learning components\n")
FILE(APPEND ${HELP_FILE} "  make Language-layer  # Build language components\n")
FILE(APPEND ${HELP_FILE} "  make Robotics-layer  # Build robotics components\n")
FILE(APPEND ${HELP_FILE} "  make Integration-layer # Build integration components\n")
FILE(APPEND ${HELP_FILE} "  make Specialized-layer # Build specialized components\n")
FILE(APPEND ${HELP_FILE} "\nLayer install targets:\n")
FILE(APPEND ${HELP_FILE} "  make install-Foundation-layer  # Install foundation components\n")
FILE(APPEND ${HELP_FILE} "  make install-Core-layer      # Install core components\n")
FILE(APPEND ${HELP_FILE} "  make install-Logic-layer     # Install logic components\n")
FILE(APPEND ${HELP_FILE} "  make install-Cognitive-layer # Install cognitive components\n")
FILE(APPEND ${HELP_FILE} "  make install-Advanced-layer  # Install advanced components\n")
FILE(APPEND ${HELP_FILE} "  make install-Learning-layer  # Install learning components\n")
FILE(APPEND ${HELP_FILE} "  make install-Language-layer  # Install language components\n")
FILE(APPEND ${HELP_FILE} "  make install-Robotics-layer  # Install robotics components\n")
FILE(APPEND ${HELP_FILE} "  make install-Integration-layer # Install integration components\n")
FILE(APPEND ${HELP_FILE} "  make install-Specialized-layer # Install specialized components\n")
FILE(APPEND ${HELP_FILE} "\nLayer uninstall targets:\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Foundation-layer  # Uninstall foundation components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Core-layer      # Uninstall core components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Logic-layer     # Uninstall logic components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Cognitive-layer # Uninstall cognitive components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Advanced-layer  # Uninstall advanced components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Learning-layer  # Uninstall learning components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Language-layer  # Uninstall language components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Robotics-layer  # Uninstall robotics components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Integration-layer # Uninstall integration components\n")
FILE(APPEND ${HELP_FILE} "  make uninstall-Specialized-layer # Uninstall specialized components\n")
FILE(APPEND ${HELP_FILE} "\nUtility targets:\n")
FILE(APPEND ${HELP_FILE} "  make list-components # Show this help\n")
FILE(APPEND ${HELP_FILE} "\nSee CMAKE_BUILD_GUIDE.md for detailed documentation\n")

# Create a target that shows available build targets
ADD_CUSTOM_TARGET(list-components
    COMMAND ${CMAKE_COMMAND} -E cat ${HELP_FILE}
    VERBATIM
)

# ----------------------------------------------------------
# Build Summary
#

# Function to print a list with proper formatting
FUNCTION(PRINT_COMPONENT_LIST list_name component_list)
    LIST(LENGTH ${component_list} list_length)
    IF(list_length GREATER 0)
        MESSAGE(STATUS "${list_name} (${list_length}):")
        FOREACH(component ${${component_list}})
            MESSAGE(STATUS "  - ${component}")
        ENDFOREACH()
    ELSE()
        MESSAGE(STATUS "${list_name}: None")
    ENDIF()
ENDFUNCTION()

MESSAGE(STATUS "")
MESSAGE(STATUS "=============================================================")
MESSAGE(STATUS "OpenCog Unified Build System - Discovery Summary")
MESSAGE(STATUS "=============================================================")

PRINT_COMPONENT_LIST("Available Components" AVAILABLE_COMPONENTS)
MESSAGE(STATUS "")
PRINT_COMPONENT_LIST("Missing Components (no CMakeLists.txt)" MISSING_COMPONENTS)

LIST(LENGTH AVAILABLE_COMPONENTS num_available)
LIST(LENGTH MISSING_COMPONENTS num_missing)
MATH(EXPR total_components "${num_available} + ${num_missing}")

MESSAGE(STATUS "")
MESSAGE(STATUS "Discovery Statistics:")
MESSAGE(STATUS "  Total components checked: ${total_components}")
MESSAGE(STATUS "  Available for building: ${num_available}")
MESSAGE(STATUS "  Missing CMakeLists.txt: ${num_missing}")

IF(num_available GREATER 0)
    MATH(EXPR availability_rate "${num_available} * 100 / ${total_components}")
    MESSAGE(STATUS "  Availability rate: ${availability_rate}% (${num_available}/${total_components})")
ENDIF()

MESSAGE(STATUS "")
MESSAGE(STATUS "Quick Start:")
MESSAGE(STATUS "  make list-components   # Show all available build targets")
MESSAGE(STATUS "  make <component>       # Build individual component") 
MESSAGE(STATUS "  make configure-all     # Configure all components")
MESSAGE(STATUS "  make all-components    # Build all available components")
MESSAGE(STATUS "  make install-all       # Install all available components")
MESSAGE(STATUS "  make uninstall-all     # Uninstall all available components")
MESSAGE(STATUS "  make Foundation-layer  # Build foundation layer")
MESSAGE(STATUS "  make install-Foundation-layer # Install foundation layer")
MESSAGE(STATUS "")
MESSAGE(STATUS "Examples:")
MESSAGE(STATUS "  make cogutil           # Build the cogutil component")
MESSAGE(STATUS "  make install-cogutil   # Install the cogutil component")
MESSAGE(STATUS "  make uninstall-cogutil # Uninstall the cogutil component")
MESSAGE(STATUS "  make atomspace         # Build the atomspace component")
MESSAGE(STATUS "  make install-atomspace # Install the atomspace component")
MESSAGE(STATUS "  make Core-layer        # Build all core components")
MESSAGE(STATUS "  make install-Core-layer # Install all core components")
MESSAGE(STATUS "")
MESSAGE(STATUS "Documentation: See CMAKE_BUILD_GUIDE.md for detailed usage")
MESSAGE(STATUS "")
MESSAGE(STATUS "Note: Individual components are built in their own build")
MESSAGE(STATUS "directories to avoid conflicts and dependency issues.")
MESSAGE(STATUS "=============================================================")