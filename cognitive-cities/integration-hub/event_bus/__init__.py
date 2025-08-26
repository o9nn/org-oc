"""
Event Bus Package - Integration Hub

Event-driven communication system for inter-triad communication.
"""

from .event_bus import CognitiveEventBus, EventPriority

__all__ = ['CognitiveEventBus', 'EventPriority']