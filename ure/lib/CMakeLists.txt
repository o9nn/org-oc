# Generate and install CMake package config files
# Pattern follows atomspace/lib/CMakeLists.txt
set(INCLUDE_INSTALL_DIR include/)
set(LIB_INSTALL_DIR lib/)
set(URE_CMAKE_DIR lib/cmake/URE)

include(CMakePackageConfigHelpers)

configure_package_config_file(UREConfig.cmake.in
	${CMAKE_CURRENT_BINARY_DIR}/UREConfig.cmake
	INSTALL_DESTINATION ${URE_CMAKE_DIR}
	PATH_VARS INCLUDE_INSTALL_DIR LIB_INSTALL_DIR CMAKE_INSTALL_PREFIX)

write_basic_package_version_file(
	"${CMAKE_CURRENT_BINARY_DIR}/UREConfigVersion.cmake"
	VERSION ${SEMANTIC_VERSION}
	COMPATIBILITY SameMajorVersion
)

# Install export targets (no NAMESPACE to match monorepo convention)
INSTALL(EXPORT URETargets
	FILE URETargets.cmake
	DESTINATION ${URE_CMAKE_DIR})

INSTALL(FILES
	${CMAKE_CURRENT_BINARY_DIR}/UREConfigVersion.cmake
	${CMAKE_CURRENT_BINARY_DIR}/UREConfig.cmake
	DESTINATION
	${URE_CMAKE_DIR})
