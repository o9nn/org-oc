# Generate and install CMake package config files
# Pattern follows atomspace/lib/CMakeLists.txt
set(INCLUDE_INSTALL_DIR include/)
set(LIB_INSTALL_DIR lib/)
set(PLN_CMAKE_DIR lib/cmake/PLN)

include(CMakePackageConfigHelpers)

configure_package_config_file(PLNConfig.cmake.in
	${CMAKE_CURRENT_BINARY_DIR}/PLNConfig.cmake
	INSTALL_DESTINATION ${PLN_CMAKE_DIR}
	PATH_VARS INCLUDE_INSTALL_DIR LIB_INSTALL_DIR CMAKE_INSTALL_PREFIX)

write_basic_package_version_file(
	"${CMAKE_CURRENT_BINARY_DIR}/PLNConfigVersion.cmake"
	VERSION ${SEMANTIC_VERSION}
	COMPATIBILITY SameMajorVersion
)

# Install export targets (no NAMESPACE to match monorepo convention)
INSTALL(EXPORT PLNTargets
	FILE PLNTargets.cmake
	DESTINATION ${PLN_CMAKE_DIR})

INSTALL(FILES
	${CMAKE_CURRENT_BINARY_DIR}/PLNConfigVersion.cmake
	${CMAKE_CURRENT_BINARY_DIR}/PLNConfig.cmake
	DESTINATION
	${PLN_CMAKE_DIR})
