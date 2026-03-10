# Generate and install CMake package config files
# Pattern follows atomspace/lib/CMakeLists.txt
set(INCLUDE_INSTALL_DIR include/)
set(LIB_INSTALL_DIR lib/)
set(COGSERVER_CMAKE_DIR lib/cmake/CogServer)

include(CMakePackageConfigHelpers)

configure_package_config_file(CogServerConfig.cmake.in
	${CMAKE_CURRENT_BINARY_DIR}/CogServerConfig.cmake
	INSTALL_DESTINATION ${COGSERVER_CMAKE_DIR}
	PATH_VARS INCLUDE_INSTALL_DIR LIB_INSTALL_DIR CMAKE_INSTALL_PREFIX)

write_basic_package_version_file(
	"${CMAKE_CURRENT_BINARY_DIR}/CogServerConfigVersion.cmake"
	VERSION ${SEMANTIC_VERSION}
	COMPATIBILITY SameMajorVersion
)

# Install export targets (no NAMESPACE to match monorepo convention)
INSTALL(EXPORT CogServerTargets
	FILE CogServerTargets.cmake
	DESTINATION ${COGSERVER_CMAKE_DIR})

INSTALL(FILES
	${CMAKE_CURRENT_BINARY_DIR}/CogServerConfigVersion.cmake
	${CMAKE_CURRENT_BINARY_DIR}/CogServerConfig.cmake
	DESTINATION
	${COGSERVER_CMAKE_DIR})
