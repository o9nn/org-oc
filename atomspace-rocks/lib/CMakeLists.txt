# Generate and install CMake package config files
set(INCLUDE_INSTALL_DIR include/)
set(LIB_INSTALL_DIR lib/)
set(ATOMSPACE_ROCKS_CMAKE_DIR lib/cmake/AtomSpaceRocks)
include(CMakePackageConfigHelpers)
configure_package_config_file(${CMAKE_CURRENT_SOURCE_DIR}/../cmake/AtomSpaceRocksConfig.cmake.in
	${CMAKE_CURRENT_BINARY_DIR}/AtomSpaceRocksConfig.cmake
	INSTALL_DESTINATION ATOMSPACE_ROCKS_CMAKE_DIR
	PATH_VARS INCLUDE_INSTALL_DIR LIB_INSTALL_DIR)
write_basic_package_version_file(
	"${CMAKE_CURRENT_BINARY_DIR}/AtomSpaceRocksConfigVersion.cmake"
	VERSION ${SEMANTIC_VERSION}
	COMPATIBILITY SameMajorVersion
)
# Install export targets
INSTALL(EXPORT AtomSpaceRocksTargets
	FILE AtomSpaceRocksTargets.cmake
	DESTINATION ${ATOMSPACE_ROCKS_CMAKE_DIR})
INSTALL(EXPORT AtomSpaceMonoSpaceTargets
	FILE AtomSpaceMonoSpaceTargets.cmake
	DESTINATION ${ATOMSPACE_ROCKS_CMAKE_DIR})
INSTALL(FILES
	${CMAKE_CURRENT_BINARY_DIR}/AtomSpaceRocksConfigVersion.cmake
	${CMAKE_CURRENT_BINARY_DIR}/AtomSpaceRocksConfig.cmake
	DESTINATION
	${ATOMSPACE_ROCKS_CMAKE_DIR})
