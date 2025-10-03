"""
Integration Hub - Cognitive Cities Architecture

Provides communication infrastructure for inter-triad coordination including
event bus and API gateway components.
"""

from . import event_bus
from . import api_gateway

__all__ = ['event_bus', 'api_gateway']