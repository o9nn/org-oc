cmake_minimum_required(VERSION 3.16)
project(examples)

# Set the data directory for OpenCog
IF (NOT DEFINED DATADIR)
	SET (DATADIR "${CMAKE_INSTALL_PREFIX}/share/opencog")
ENDIF (NOT DEFINED DATADIR)

# Install example Scheme files
install(FILES 
	pair-count.scm
	README.md
	DESTINATION "${DATADIR}/agents/examples")
