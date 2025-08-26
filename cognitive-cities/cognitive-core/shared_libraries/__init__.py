"""
Cognitive Cities Shared Libraries

This package provides core shared libraries for the Cognitive Cities Architecture,
including AtomSpace integration and membrane-based process control.
"""

from .atomspace_manager import CognitiveAtomSpaceManager
from .membrane_controller import MembraneController

__all__ = ['CognitiveAtomSpaceManager', 'MembraneController']