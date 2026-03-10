# Generate and install CMake package config files
set(INCLUDE_INSTALL_DIR include/)
set(LIB_INSTALL_DIR lib/)

set(ATOMSPACE_STORAGE_CMAKE_DIR lib/cmake/AtomSpaceStorage)

include(CMakePackageConfigHelpers)
configure_package_config_file(AtomSpaceStorageConfig.cmake.in
	${CMAKE_CURRENT_BINARY_DIR}/AtomSpaceStorageConfig.cmake
	INSTALL_DESTINATION ATOMSPACE_STORAGE_CMAKE_DIR
	PATH_VARS INCLUDE_INSTALL_DIR LIB_INSTALL_DIR)

write_basic_package_version_file(
	"${CMAKE_CURRENT_BINARY_DIR}/AtomSpaceStorageConfigVersion.cmake"
	VERSION ${SEMANTIC_VERSION}
	COMPATIBILITY SameMajorVersion
)

# Install export targets
INSTALL(EXPORT AtomSpaceStorageTargets
	FILE AtomSpaceStorageTargets.cmake
	DESTINATION ${ATOMSPACE_STORAGE_CMAKE_DIR})

INSTALL(FILES
	${CMAKE_CURRENT_BINARY_DIR}/AtomSpaceStorageConfigVersion.cmake
	${CMAKE_CURRENT_BINARY_DIR}/AtomSpaceStorageConfig.cmake
	DESTINATION
	${ATOMSPACE_STORAGE_CMAKE_DIR})
