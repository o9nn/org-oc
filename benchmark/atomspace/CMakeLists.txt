# Build file for the atomspace synthetic benchmarks

# The benchmark uses TLB (Transaction Log Buffer) from AtomSpaceStorage.
IF (ATOMSPACE_STORAGE_FOUND)
ADD_EXECUTABLE (atomspace_bm
	AtomSpaceBenchmark.cc
	atomspace_bm.cc
)

TARGET_LINK_LIBRARIES (atomspace_bm
	${ATOMSPACE_LIBRARIES}
	${ATOMSPACE_STORAGE_LIBRARIES}
	${COGUTIL_LIBRARY}
)

IF (HAVE_CYTHON)
	INCLUDE_DIRECTORIES (
		${Python3_INCLUDE_DIRS}
	)
	TARGET_LINK_LIBRARIES (atomspace_bm
		PythonEval
		# ${ATOMSPACE_PythonEval_LIBRARY}
		${Python3_LIBRARIES}
	)
ENDIF(HAVE_CYTHON)

INSTALL(TARGETS atomspace_bm RUNTIME DESTINATION "bin")
ELSE (ATOMSPACE_STORAGE_FOUND)
	MESSAGE(STATUS "AtomSpaceStorage not found: skipping TLB-based atomspace benchmark.")
ENDIF (ATOMSPACE_STORAGE_FOUND)
