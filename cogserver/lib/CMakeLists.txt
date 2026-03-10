# Auto-generated cmake package config install
# Exports CogServerTargets for downstream find_package() discovery

# build_type is used in CogServerConfig.cmake.in
string(TOUPPER "${CMAKE_BUILD_TYPE}" build_type)

export(EXPORT CogServerTargets
	FILE "${CMAKE_CURRENT_BINARY_DIR}/CogServer/CogServerTargets.cmake"
)

set(ConfigPackageLocation lib/cmake/CogServer)

install(EXPORT CogServerTargets
	FILE CogServerTargets.cmake
	DESTINATION ${ConfigPackageLocation}
)

include(CMakePackageConfigHelpers)

configure_package_config_file(CogServerConfig.cmake.in
	${CMAKE_CURRENT_BINARY_DIR}/CogServerConfig.cmake
	INSTALL_DESTINATION lib/CogServer/cmake
	PATH_VARS CMAKE_INSTALL_PREFIX
)

write_basic_package_version_file(
	"${CMAKE_CURRENT_BINARY_DIR}/CogServerConfigVersion.cmake"
	VERSION ${SEMANTIC_VERSION}
	COMPATIBILITY SameMajorVersion
)

INSTALL(FILES
	${CMAKE_CURRENT_BINARY_DIR}/CogServerConfigVersion.cmake
	${CMAKE_CURRENT_BINARY_DIR}/CogServerConfig.cmake
	DESTINATION ${ConfigPackageLocation}
)
