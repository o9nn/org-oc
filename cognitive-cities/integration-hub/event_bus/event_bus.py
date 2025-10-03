"""
Cognitive Event Bus - Integration Hub

Event-driven communication system for inter-triad communication following 
System-5 CNS pathways. Manages communication between cerebral, somatic, 
and autonomic triads.
"""

import asyncio
from typing import Dict, List, Callable, Any, Optional
import logging
import json
from datetime import datetime
from enum import Enum
import weakref

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels for processing order."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class CognitiveEventBus:
    """
    Event bus for cognitive triad communication.
    
    Implements event-driven communication following CNS pathways
    with support for triad-specific routing and priority handling.
    """
    
    def __init__(self):
        """Initialize the cognitive event bus."""
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.event_filters: Dict[str, Callable] = {}
        
        # Define System-5 CNS communication pathways
        self.triad_connections = {
            "cerebral_to_somatic": {
                "allowed_events": ["action_commands", "behavioral_requests", "motor_intentions"],
                "pathway_type": "executive_control",
                "priority_weight": 1.2
            },
            "cerebral_to_autonomic": {
                "allowed_events": ["emotional_states", "attention_allocation", "cognitive_load"],
                "pathway_type": "emotional_regulation", 
                "priority_weight": 1.1
            },
            "somatic_to_autonomic": {
                "allowed_events": ["stress_indicators", "sensory_overload", "physical_state"],
                "pathway_type": "physiological_feedback",
                "priority_weight": 1.0
            },
            "somatic_to_cerebral": {
                "allowed_events": ["sensory_input", "motor_feedback", "behavioral_completion"],
                "pathway_type": "sensory_feedback",
                "priority_weight": 0.9
            },
            "autonomic_to_cerebral": {
                "allowed_events": ["emotional_feedback", "arousal_level", "homeostatic_status"],
                "pathway_type": "autonomic_feedback", 
                "priority_weight": 0.8
            },
            "autonomic_to_somatic": {
                "allowed_events": ["autonomic_commands", "stress_response", "energy_allocation"],
                "pathway_type": "autonomic_control",
                "priority_weight": 1.0
            }
        }
        
        # Event processing queue
        self.event_queue = asyncio.PriorityQueue()
        self.processing_active = False
        
        # Statistics tracking
        self.event_stats = {
            "total_published": 0,
            "total_delivered": 0,
            "total_filtered": 0,
            "pathway_usage": {pathway: 0 for pathway in self.triad_connections.keys()}
        }
        
        logger.info("CognitiveEventBus initialized with System-5 CNS pathways")
        
    async def publish_triad_event(self, source_triad: str, target_triad: str, 
                                 event_type: str, data: Any, 
                                 priority: EventPriority = EventPriority.MEDIUM) -> bool:
        """
        Publish events between triads following CNS pathways.
        
        Args:
            source_triad: Source triad name (cerebral, somatic, autonomic)
            target_triad: Target triad name
            event_type: Type of event being published
            data: Event data payload
            priority: Event priority level
            
        Returns:
            bool: True if event was successfully published
        """
        try:
            # Validate triad communication pathway
            pathway_key = f"{source_triad}_to_{target_triad}"
            if not self._validate_pathway(pathway_key, event_type):
                logger.warning(f"Invalid pathway: {pathway_key} for event: {event_type}")
                return False
                
            # Create event object
            event = {
                "id": self._generate_event_id(),
                "timestamp": datetime.now().isoformat(),
                "source_triad": source_triad,
                "target_triad": target_triad,
                "event_type": event_type,
                "data": data,
                "priority": priority,
                "pathway": pathway_key,
                "processed": False
            }
            
            # Apply pathway-specific priority weighting
            pathway_info = self.triad_connections[pathway_key]
            weighted_priority = priority.value * pathway_info["priority_weight"]
            
            # Add to processing queue
            await self.event_queue.put((weighted_priority, event))
            
            # Update statistics
            self.event_stats["total_published"] += 1
            self.event_stats["pathway_usage"][pathway_key] += 1
            
            logger.debug(f"Published event: {event_type} from {source_triad} to {target_triad}")
            
            # Start processing if not already active
            if not self.processing_active:
                asyncio.create_task(self._process_event_queue())
                
            return True
            
        except Exception as e:
            logger.error(f"Error publishing triad event: {e}")
            return False
            
    async def publish(self, event_type: str, data: Any, 
                     priority: EventPriority = EventPriority.MEDIUM) -> bool:
        """
        Publish general event to all subscribers.
        
        Args:
            event_type: Type of event
            data: Event data
            priority: Event priority
            
        Returns:
            bool: True if published successfully
        """
        try:
            event = {
                "id": self._generate_event_id(),
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data,
                "priority": priority,
                "pathway": "general",
                "processed": False
            }
            
            await self.event_queue.put((priority.value, event))
            
            if not self.processing_active:
                asyncio.create_task(self._process_event_queue())
                
            return True
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
            
    def subscribe(self, event_type: str, callback: Callable, 
                 triad_filter: Optional[str] = None) -> bool:
        """
        Subscribe to specific event types.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Callback function to handle events
            triad_filter: Optional triad filter to only receive events from specific triad
            
        Returns:
            bool: True if subscription successful
        """
        try:
            subscription_key = event_type
            if triad_filter:
                subscription_key = f"{triad_filter}.{event_type}"
                
            if subscription_key not in self.subscribers:
                self.subscribers[subscription_key] = []
                
            # Use weak reference to avoid memory leaks
            if hasattr(callback, '__self__'):
                # Method callback - use weak reference
                weak_callback = weakref.WeakMethod(callback)
            else:
                # Function callback - use weak reference
                weak_callback = weakref.ref(callback)
                
            self.subscribers[subscription_key].append(weak_callback)
            
            logger.debug(f"Subscribed to {subscription_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to {event_type}: {e}")
            return False
            
    def unsubscribe(self, event_type: str, callback: Callable, 
                   triad_filter: Optional[str] = None) -> bool:
        """
        Unsubscribe from event type.
        
        Args:
            event_type: Event type to unsubscribe from
            callback: Callback function to remove
            triad_filter: Optional triad filter
            
        Returns:
            bool: True if unsubscription successful
        """
        try:
            subscription_key = event_type
            if triad_filter:
                subscription_key = f"{triad_filter}.{event_type}"
                
            if subscription_key in self.subscribers:
                # Remove callback from subscribers list
                self.subscribers[subscription_key] = [
                    cb for cb in self.subscribers[subscription_key]
                    if cb() != callback  # Compare the dereferenced callback
                ]
                
                # Clean up empty subscription lists
                if not self.subscribers[subscription_key]:
                    del self.subscribers[subscription_key]
                    
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing from {event_type}: {e}")
            return False
            
    def add_event_filter(self, filter_name: str, filter_function: Callable[[Dict], bool]) -> None:
        """
        Add event filter to process events before delivery.
        
        Args:
            filter_name: Name of the filter
            filter_function: Function that returns True if event should be delivered
        """
        self.event_filters[filter_name] = filter_function
        logger.debug(f"Added event filter: {filter_name}")
        
    def remove_event_filter(self, filter_name: str) -> None:
        """Remove event filter."""
        if filter_name in self.event_filters:
            del self.event_filters[filter_name]
            logger.debug(f"Removed event filter: {filter_name}")
            
    async def _process_event_queue(self) -> None:
        """Process events from the queue."""
        self.processing_active = True
        
        try:
            while not self.event_queue.empty():
                try:
                    priority, event = await self.event_queue.get()
                    await self._deliver_event(event)
                    self.event_queue.task_done()
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    
        finally:
            self.processing_active = False
            
    async def _deliver_event(self, event: Dict[str, Any]) -> None:
        """Deliver event to subscribers."""
        try:
            # Apply event filters
            if not self._apply_event_filters(event):
                self.event_stats["total_filtered"] += 1
                return
                
            event_type = event["event_type"]
            source_triad = event.get("source_triad")
            
            # Find matching subscribers
            subscribers_to_notify = []
            
            # General event type subscribers
            if event_type in self.subscribers:
                subscribers_to_notify.extend(self.subscribers[event_type])
                
            # Triad-specific subscribers
            if source_triad:
                triad_specific_key = f"{source_triad}.{event_type}"
                if triad_specific_key in self.subscribers:
                    subscribers_to_notify.extend(self.subscribers[triad_specific_key])
                    
            # Deliver to all matching subscribers
            delivery_tasks = []
            for weak_callback in subscribers_to_notify:
                callback = weak_callback()  # Dereference weak reference
                if callback:  # Check if callback still exists
                    task = asyncio.create_task(self._safe_callback_invoke(callback, event))
                    delivery_tasks.append(task)
                    
            # Wait for all deliveries to complete
            if delivery_tasks:
                await asyncio.gather(*delivery_tasks, return_exceptions=True)
                
            # Mark event as processed
            event["processed"] = True
            self.event_history.append(event)
            self.event_stats["total_delivered"] += 1
            
            # Limit history size
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-500:]
                
            logger.debug(f"Delivered event {event['id']} to {len(subscribers_to_notify)} subscribers")
            
        except Exception as e:
            logger.error(f"Error delivering event: {e}")
            
    async def _safe_callback_invoke(self, callback: Callable, event: Dict[str, Any]) -> None:
        """Safely invoke callback with proper error handling."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as e:
            logger.error(f"Error in event callback: {e}")
            
    def _validate_pathway(self, pathway_key: str, event_type: str) -> bool:
        """Validate that the communication pathway is allowed for the event type."""
        if pathway_key not in self.triad_connections:
            return False
            
        pathway_info = self.triad_connections[pathway_key]
        allowed_events = pathway_info["allowed_events"]
        
        return event_type in allowed_events
        
    def _apply_event_filters(self, event: Dict[str, Any]) -> bool:
        """Apply all event filters to determine if event should be delivered."""
        for filter_name, filter_function in self.event_filters.items():
            try:
                if not filter_function(event):
                    logger.debug(f"Event filtered out by {filter_name}")
                    return False
            except Exception as e:
                logger.error(f"Error in event filter {filter_name}: {e}")
                # Continue processing if filter fails
                
        return True
        
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())[:8]
        
    def get_pathway_info(self, source_triad: str, target_triad: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific communication pathway."""
        pathway_key = f"{source_triad}_to_{target_triad}"
        return self.triad_connections.get(pathway_key)
        
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent event history."""
        return self.event_history[-limit:]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            "event_stats": self.event_stats.copy(),
            "active_subscriptions": len(self.subscribers),
            "active_filters": len(self.event_filters),
            "queue_size": self.event_queue.qsize(),
            "processing_active": self.processing_active,
            "history_size": len(self.event_history)
        }
        
    def clear_history(self) -> None:
        """Clear event history."""
        self.event_history.clear()
        logger.info("Event history cleared")
        
    async def shutdown(self) -> None:
        """Shutdown the event bus gracefully."""
        logger.info("Shutting down CognitiveEventBus...")
        
        # Wait for queue to be processed
        if not self.event_queue.empty():
            await self.event_queue.join()
            
        # Clear subscribers and filters
        self.subscribers.clear()
        self.event_filters.clear()
        
        logger.info("CognitiveEventBus shutdown complete")