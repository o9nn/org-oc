cmake_minimum_required(VERSION 3.16)
project(agents)

# Set the data directory for OpenCog
IF (NOT DEFINED DATADIR)
	SET (DATADIR "${CMAKE_INSTALL_PREFIX}/share/opencog")
ENDIF (NOT DEFINED DATADIR)

# Add subdirectories
ADD_SUBDIRECTORY(scm)
ADD_SUBDIRECTORY(examples)

# Install documentation files
install(FILES README.md LICENSE
	DESTINATION "${DATADIR}/agents")