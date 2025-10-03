# OpenCog Unified Build System

This document describes the unified CMake build system for the OpenCog Organization repository.

## Overview

The OpenCog Organization repository contains 46+ individual OpenCog components, each with their own CMakeLists.txt and build requirements. The unified build system provides:

- **Component Discovery**: Automatically finds all buildable components
- **Dependency-Aware Organization**: Components are organized by dependency layers
- **Individual Component Builds**: Each component builds in its own isolated directory
- **Collective Build Targets**: Build entire layers or all components at once
- **Clear Status Reporting**: Know exactly what's available and what's missing

## Quick Start

```bash
# Clone the repository (if not already done)
git clone https://github.com/OpenCoq/opencog-org.git
cd opencog-org

# Configure the unified build system
mkdir build && cd build
cmake ..

# See all available build targets
make list-components

# Build a specific component
make cogutil

# Build all foundation components
make Foundation-layer

# Configure all available components
make configure-all

# Build all available components (may take a long time!)
make all-components
```

## Available Build Targets

### Individual Components

Build any individual component:
```bash
make <component-name>
```

Install any individual component:
```bash
make install-<component-name>
```

Available components include:
- **Foundation Layer**: cogutil, moses, blender_api_msgs
- **Core Layer**: atomspace, atomspace-rocks, atomspace-pgres, atomspace-ipfs, etc.
- **Logic Layer**: unify, ure
- **Cognitive Layer**: cogserver, attention, spacetime, pattern-index, etc.
- **Advanced Layer**: pln, miner, asmoses, benchmark
- **Learning Layer**: learn, generate
- **Language Layer**: lg-atomese
- **Robotics Layer**: vision, perception, sensory, ros-behavior-scripting, etc.
- **Integration Layer**: opencog, TinyCog
- **Specialized Components**: visualization, cheminformatics, agi-bio, etc.

### Layer-Based Targets

Build entire dependency layers:
```bash
make Foundation-layer    # Build all foundation components
make Core-layer         # Build all core components  
make Logic-layer        # Build all logic components
make Cognitive-layer    # Build all cognitive components
make Advanced-layer     # Build all advanced components
make Learning-layer     # Build all learning components
make Language-layer     # Build all language components
make Robotics-layer     # Build all robotics components
make Integration-layer  # Build all integration components
make Specialized-layer  # Build all specialized components
```

Install entire dependency layers:
```bash
make install-Foundation-layer    # Install all foundation components
make install-Core-layer         # Install all core components  
make install-Logic-layer        # Install all logic components
make install-Cognitive-layer    # Install all cognitive components
make install-Advanced-layer     # Install all advanced components
make install-Learning-layer     # Install all learning components
make install-Language-layer     # Install all language components
make install-Robotics-layer     # Install all robotics components
make install-Integration-layer  # Install all integration components
make install-Specialized-layer  # Install all specialized components
```

Uninstall entire dependency layers:
```bash
make uninstall-Foundation-layer    # Uninstall all foundation components
make uninstall-Core-layer         # Uninstall all core components  
make uninstall-Logic-layer        # Uninstall all logic components
make uninstall-Cognitive-layer    # Uninstall all cognitive components
make uninstall-Advanced-layer     # Uninstall all advanced components
make uninstall-Learning-layer     # Uninstall all learning components
make uninstall-Language-layer     # Uninstall all language components
make uninstall-Robotics-layer     # Uninstall all robotics components
make uninstall-Integration-layer  # Uninstall all integration components
make uninstall-Specialized-layer  # Uninstall all specialized components
```

### Collective Targets

```bash
make configure-all      # Configure all available components
make all-components     # Build all available components
make install-all        # Install all available components
make uninstall-all      # Uninstall all available components
make list-components    # Show available build targets and help
```

## How It Works

### Component Discovery

The unified build system automatically discovers available components by:
1. Checking each expected component directory for a `CMakeLists.txt` file
2. Registering components that are available for building
3. Creating individual build targets for each available component

### Isolated Builds

Each component is built in its own isolated directory (`<component>-build/`) to:
- Avoid conflicts between different component configurations
- Allow components to have different dependency requirements
- Enable parallel builds of independent components
- Maintain clean separation of build artifacts

### Dependency Layers

Components are organized into dependency layers based on the OpenCog dependency diagrams:

1. **Foundation**: Core utilities and base components
2. **Core**: AtomSpace and storage backends  
3. **Logic**: Unification and rule engines
4. **Cognitive**: Cognitive architecture components
5. **Advanced**: Advanced reasoning and mining
6. **Learning**: Machine learning frameworks
7. **Language**: Natural language processing
8. **Robotics**: Robotic and perception components
9. **Integration**: Main OpenCog applications
10. **Specialized**: Domain-specific applications

## Component Status

During configuration, you'll see a summary showing:
- **Available Components**: Components with CMakeLists.txt that can be built
- **Missing Components**: Expected components without CMakeLists.txt files
- **Availability Rate**: Percentage of expected components that are available

Example output:
```
Available Components (46):
  - cogutil
  - moses
  - atomspace
  [... more components ...]

Missing Components (6):
  - external-tools
  - ocpkg
  - profile
  [... missing components ...]

Discovery Statistics:
  Total components checked: 52
  Available for building: 46
  Missing CMakeLists.txt: 6
  Availability rate: 88% (46/52)
```

## Building Individual Components

When you build an individual component:

```bash
make cogutil
```

The system will:
1. Configure the component in `cogutil-build/`
2. Build the component using its own CMakeLists.txt
3. Report the build result

If a component fails to build due to missing dependencies, the error will be contained to that component and won't affect others.

## Installing Components

The unified build system provides centralized installation functionality for managing OpenCog components. Each component can be installed individually or as part of layer-based groups.

### Individual Component Installation

Install any individual component:
```bash
make install-cogutil     # Install the cogutil component
make install-atomspace   # Install the atomspace component
```

The system will:
1. Build the component (if not already built)
2. Install the component using its CMake install target
3. Place files in the system-wide installation directories

### Layer-Based Installation

Install entire dependency layers at once:
```bash
make install-Foundation-layer   # Install all foundation components
make install-Core-layer        # Install all core components
```

This is particularly useful for setting up dependencies in the correct order.

### Complete Installation

Install all available components:
```bash
make install-all
```

This will build and install every available component in the repository.

### Installation Requirements

- **Root Access**: Most installations require root/sudo access to install to system directories
- **Build Dependencies**: Components must be successfully built before installation
- **Disk Space**: Ensure adequate disk space for all component installations
- **Dependencies**: Some components may require others to be installed first

### Installation Locations

Components install to standard system locations:
- **Libraries**: `/usr/local/lib` or `/usr/lib`
- **Headers**: `/usr/local/include` or `/usr/include`
- **Executables**: `/usr/local/bin` or `/usr/bin`
- **Documentation**: `/usr/local/share/doc` or `/usr/share/doc`

Individual components may customize their installation paths through their own CMakeLists.txt files.

## Uninstalling Components

The unified build system provides uninstallation functionality to remove installed OpenCog components from your system.

### Individual Component Uninstallation

Uninstall any individual component:
```bash
make uninstall-cogutil     # Uninstall the cogutil component
make uninstall-atomspace   # Uninstall the atomspace component
```

The system will:
1. Locate the component's install manifest (if available)
2. Remove all files listed in the manifest
3. Report any files that couldn't be removed

### Layer-Based Uninstallation

Uninstall entire dependency layers:
```bash
make uninstall-Foundation-layer   # Uninstall all foundation components
make uninstall-Core-layer        # Uninstall all core components
```

This removes all components in the specified layer.

### Complete Uninstallation

Uninstall all components:
```bash
make uninstall-all
```

This will remove every installed OpenCog component from the system.

### Uninstallation Limitations

- **Install Manifests**: Uninstallation relies on CMake install manifests. If a component was installed without generating a manifest, automatic uninstallation may not be possible.
- **Root Access**: Uninstallation typically requires the same permissions as installation (root/sudo).
- **Manual Cleanup**: Some components may require manual cleanup of configuration files or data directories.
- **Dependency Order**: Uninstall components in reverse dependency order to avoid issues.

## System Requirements

Components have their own individual requirements. Common requirements across the OpenCog ecosystem include:

- **C++ Compiler**: GCC 7+ or Clang 6+
- **CMake**: 3.12+
- **Boost**: 1.60+
- **Python**: 3.6+
- **Guile**: 2.2+ or 3.0+

Individual components may have additional requirements like:
- Various databases (PostgreSQL, RocksDB)
- Machine learning libraries
- Robotics frameworks (ROS)
- Specialized libraries for specific domains

Check each component's README for specific requirements.

## Troubleshooting

### Component Won't Configure
If `make configure-<component>` fails:
1. Check the component's README for specific dependencies
2. Install missing dependencies for that component
3. Look at the error output in the component's build directory

### Component Won't Build  
If `make <component>` fails after configuration:
1. Check the build log in `<component>-build/`
2. Ensure all dependencies are properly installed
3. Try building dependencies first (e.g., build `cogutil` before `atomspace`)

### Missing Components
If a component shows as "Missing" in the discovery:
- The component may not have been ported to CMake yet
- The component may be deprecated or moved
- The component name may have changed

## Contributing

To add support for a new component:

1. Ensure the component has a working `CMakeLists.txt`
2. Add the component to the appropriate layer in the main `CMakeLists.txt`
3. Test that the component can be configured and built
4. Update this documentation

## Integration with Existing Workflows

This unified build system is designed to complement, not replace, existing build workflows:

- **Individual Development**: Developers can still build components individually in their own directories
- **CI/CD Integration**: The unified system provides clear targets for automated builds
- **Dependency Management**: Layer-based organization helps with dependency order
- **Status Monitoring**: Easy to see what's available and what's broken

The unified build system provides a "bird's eye view" of the entire OpenCog ecosystem while maintaining the flexibility of individual component builds.