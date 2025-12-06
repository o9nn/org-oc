cmake_minimum_required(VERSION 3.16)
project(pair_agent)

# Set the data directory for OpenCog
IF (NOT DEFINED DATADIR)
	SET (DATADIR "${CMAKE_INSTALL_PREFIX}/share/opencog")
ENDIF (NOT DEFINED DATADIR)

# Install Scheme files
install(FILES 
	count-agent.scm
	generate-agent.scm
	DESTINATION "${DATADIR}/agents/scm/pair-agent")

# Install documentation
install(FILES
	README.md
	Design-Generate.md
	DESTINATION "${DATADIR}/agents/scm/pair-agent")
