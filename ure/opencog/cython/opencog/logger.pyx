from ure cimport ure_logger as c_ure_logger
from opencog.logger cimport cLogger, Logger

def ure_logger():
    """Create a Logger instance for URE"""
    cdef Logger logger = Logger()
    return logger
