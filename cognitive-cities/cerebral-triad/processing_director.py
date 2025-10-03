"""
Processing Director - Cerebral Triad

Central coordination service that manages processing across the cerebral triad
using ECAN attention allocation and task routing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from cognitive_core.shared_libraries.atomspace_manager import CognitiveAtomSpaceManager
from cognitive_core.shared_libraries.membrane_controller import MembraneController
from opencog.atomspace import types
from opencog.type_constructors import *
import logging
import asyncio
from typing import Dict, Any, List, Queue
import queue
from enum import Enum

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels for processing queue management."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class ProcessingDirector:
    """
    Processing Director implementing central cerebral coordination.
    
    Coordinates processing across cerebral triad using ECAN attention
    allocation and manages task routing between hemisphere services.
    """
    
    def __init__(self):
        """Initialize the Processing Director with coordination capabilities."""
        self.atomspace_manager = CognitiveAtomSpaceManager()
        self.membrane_controller = MembraneController(self.atomspace_manager.get_atomspace())
        
        self.service_name = "processing-director"
        self.triad = "cerebral"
        self.role = "central_coordination"
        
        # Initialize task queue and attention management
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = {}
        self.service_registry = {}
        
        # ECAN attention parameters
        self.ecan_enabled = True
        self.attention_budget = 1000.0
        self.current_attention_allocation = {}
        
        # Initialize service in AtomSpace
        self._initialize_service()
        
        # Initialize attention and coordination systems
        self._initialize_attention_system()
        
        logger.info("ProcessingDirector initialized with ECAN attention allocation")
        
    def _initialize_service(self):
        """Initialize service representation in AtomSpace."""
        # Create service atom and triad membership
        self.service_atom = self.atomspace_manager.create_triad_atom(
            "CerebralTriad",
            self.service_name
        )
        
        # Create coordination membrane rules
        self._create_coordination_membrane_rules()
        
    def _create_coordination_membrane_rules(self):
        """Create membrane rules for coordination processing."""
        # Rule for task prioritization
        context = AndLink(
            EvaluationLink(
                PredicateNode("TaskPending"),
                ConceptNode(self.service_name)
            ),
            GreaterThanLink(
                EvaluationLink(
                    PredicateNode("AttentionAvailable"),
                    ConceptNode(self.service_name)
                ),
                NumberNode(0.1)
            )
        )
        
        action = ExecutionOutputLink(
            GroundedSchemaNode("py: process_task_queue"),
            ConceptNode(self.service_name)
        )
        
        goal = EvaluationLink(
            PredicateNode("OptimalTaskDistribution"),
            ConceptNode(self.service_name)
        )
        
        self.coordination_rule = self.membrane_controller.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad="CerebralCoordinationMembrane"
        )
        
    def _initialize_attention_system(self):
        """Initialize ECAN attention allocation system."""
        # Create attention nodes for each hemisphere and processing type
        self.attention_nodes = {
            "right_hemisphere": ConceptNode("RightHemisphereAttention"),
            "left_hemisphere": ConceptNode("LeftHemisphereAttention"),
            "analytical_processing": ConceptNode("AnalyticalProcessingAttention"),
            "creative_processing": ConceptNode("CreativeProcessingAttention")
        }
        
        # Initialize attention values
        for node_name, node in self.attention_nodes.items():
            # Set initial attention values using ECAN-style importance
            node.av = {"sti": 50, "lti": 0, "vlti": False}
            
        # Register cerebral triad services
        self._register_triad_services()
        
    def _register_triad_services(self):
        """Register available cerebral triad services."""
        self.service_registry = {
            "thought-service": {
                "hemisphere": "right",
                "processing_type": "intuitive",
                "capabilities": ["creative_thinking", "possibility_exploration"],
                "load": 0.0
            },
            "processing-service": {
                "hemisphere": "neutral",
                "processing_type": "analytical", 
                "capabilities": ["logical_reasoning", "problem_solving"],
                "load": 0.0
            },
            "output-service": {
                "hemisphere": "left",
                "processing_type": "applied",
                "capabilities": ["structured_output", "practical_application"],
                "load": 0.0
            }
        }
        
    async def coordinate_processing(self, task_queue: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Coordinate processing across cerebral triad using ECAN attention.
        
        Args:
            task_queue: List of tasks to process and coordinate
            
        Returns:
            Coordination results and task assignments
        """
        try:
            logger.debug(f"Coordinating processing for {len(task_queue)} tasks")
            
            # Add tasks to priority queue
            for task in task_queue:
                await self._enqueue_task(task)
                
            # Allocate attention based on task requirements
            attention_allocation = await self._allocate_attention()
            
            # Route tasks to appropriate services
            routing_results = await self._route_tasks()
            
            # Monitor and balance processing load
            load_balancing = await self._balance_processing_load()
            
            coordination_result = {
                "service": self.service_name,
                "processed_tasks": len(task_queue),
                "attention_allocation": attention_allocation,
                "routing_results": routing_results,
                "load_balancing": load_balancing,
                "coordination_efficiency": self._calculate_coordination_efficiency()
            }
            
            logger.info(f"Coordinated {len(task_queue)} tasks across cerebral triad")
            return coordination_result
            
        except Exception as e:
            logger.error(f"Error in processing coordination: {e}")
            return {"error": str(e), "service": self.service_name}
            
    async def _enqueue_task(self, task: Dict[str, Any]) -> None:
        """Add task to priority queue with appropriate priority."""
        priority = self._determine_task_priority(task)
        task_id = task.get("id", len(self.active_tasks))
        
        # Create priority tuple (priority, task_id, task)
        priority_item = (priority.value, task_id, task)
        self.task_queue.put(priority_item)
        
        logger.debug(f"Enqueued task {task_id} with priority {priority.name}")
        
    def _determine_task_priority(self, task: Dict[str, Any]) -> TaskPriority:
        """Determine task priority based on task characteristics."""
        urgency = task.get("urgency", "medium")
        complexity = task.get("complexity", "medium") 
        attention_requirement = task.get("attention_requirement", 0.5)
        
        if urgency == "urgent" or attention_requirement > 0.8:
            return TaskPriority.URGENT
        elif urgency == "high" or complexity == "high":
            return TaskPriority.HIGH
        elif urgency == "low" and complexity == "low":
            return TaskPriority.LOW
        else:
            return TaskPriority.MEDIUM
            
    async def _allocate_attention(self) -> Dict[str, float]:
        """Allocate attention using ECAN-inspired mechanism."""
        if not self.ecan_enabled:
            return {"attention_disabled": True}
            
        # Calculate attention requirements for pending tasks
        attention_requirements = await self._calculate_attention_requirements()
        
        # Apply ECAN-style attention spreading
        attention_allocation = {}
        remaining_budget = self.attention_budget
        
        for service_name, requirement in attention_requirements.items():
            # Calculate allocation based on importance and availability
            service_info = self.service_registry.get(service_name, {})
            current_load = service_info.get("load", 0.0)
            
            # Reduce allocation if service is heavily loaded
            load_factor = max(0.1, 1.0 - current_load)
            allocation = min(requirement * load_factor, remaining_budget * 0.4)
            
            attention_allocation[service_name] = allocation
            remaining_budget -= allocation
            
        # Update current attention allocation
        self.current_attention_allocation = attention_allocation
        
        logger.debug(f"Allocated attention: {attention_allocation}")
        return attention_allocation
        
    async def _calculate_attention_requirements(self) -> Dict[str, float]:
        """Calculate attention requirements for each service."""
        requirements = {}
        
        # Scan task queue to estimate requirements
        temp_queue = []
        
        while not self.task_queue.empty():
            try:
                priority, task_id, task = self.task_queue.get_nowait()
                temp_queue.append((priority, task_id, task))
                
                # Determine which service should handle this task
                target_service = self._select_target_service(task)
                
                if target_service:
                    attention_need = task.get("attention_requirement", 0.3)
                    requirements[target_service] = requirements.get(target_service, 0) + attention_need
                    
            except queue.Empty:
                break
                
        # Restore tasks to queue
        for item in temp_queue:
            self.task_queue.put(item)
            
        return requirements
        
    async def _route_tasks(self) -> List[Dict[str, Any]]:
        """Route tasks to appropriate services based on capabilities."""
        routing_results = []
        
        while not self.task_queue.empty():
            try:
                priority, task_id, task = self.task_queue.get_nowait()
                
                # Select target service for task
                target_service = self._select_target_service(task)
                
                if target_service and self._can_allocate_to_service(target_service, task):
                    # Route task to service
                    routing_result = await self._route_to_service(target_service, task)
                    routing_results.append(routing_result)
                    
                    # Update service load
                    self._update_service_load(target_service, task)
                    
                else:
                    # Re-queue task if no service available
                    self.task_queue.put((priority, task_id, task))
                    break
                    
            except queue.Empty:
                break
                
        return routing_results
        
    def _select_target_service(self, task: Dict[str, Any]) -> str:
        """Select target service based on task requirements."""
        task_type = task.get("type", "general")
        processing_style = task.get("processing_style", "neutral")
        
        # Route based on task characteristics
        if task_type == "creative" or processing_style == "intuitive":
            return "thought-service"
        elif task_type == "analytical" or processing_style == "logical":
            return "processing-service"
        elif task_type == "output" or processing_style == "applied":
            return "output-service"
        else:
            # Default to processing service for general tasks
            return "processing-service"
            
    def _can_allocate_to_service(self, service_name: str, task: Dict[str, Any]) -> bool:
        """Check if service can handle additional task based on attention and load."""
        service_info = self.service_registry.get(service_name, {})
        current_load = service_info.get("load", 0.0)
        
        # Check if service is not overloaded
        if current_load > 0.8:
            return False
            
        # Check if sufficient attention is allocated
        allocated_attention = self.current_attention_allocation.get(service_name, 0)
        required_attention = task.get("attention_requirement", 0.3)
        
        return allocated_attention >= required_attention
        
    async def _route_to_service(self, service_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to specific service."""
        routing_message = {
            "target_service": service_name,
            "task": task,
            "allocated_attention": self.current_attention_allocation.get(service_name, 0),
            "routing_timestamp": asyncio.get_event_loop().time()
        }
        
        logger.debug(f"Routing task {task.get('id')} to {service_name}")
        
        return {
            "task_id": task.get("id"),
            "routed_to": service_name,
            "attention_allocated": self.current_attention_allocation.get(service_name, 0),
            "status": "routed"
        }
        
    def _update_service_load(self, service_name: str, task: Dict[str, Any]) -> None:
        """Update service load metrics."""
        if service_name in self.service_registry:
            current_load = self.service_registry[service_name].get("load", 0.0)
            task_load = task.get("computational_load", 0.1)
            
            # Update load (with simple decay factor)
            new_load = min(1.0, current_load + task_load)
            self.service_registry[service_name]["load"] = new_load
            
    async def _balance_processing_load(self) -> Dict[str, Any]:
        """Monitor and balance processing load across services."""
        load_status = {}
        
        for service_name, service_info in self.service_registry.items():
            current_load = service_info.get("load", 0.0)
            load_status[service_name] = {
                "current_load": current_load,
                "status": "overloaded" if current_load > 0.8 else "normal"
            }
            
            # Apply load decay over time
            decay_factor = 0.1
            service_info["load"] = max(0.0, current_load - decay_factor)
            
        return {
            "load_status": load_status,
            "balancing_action": "load_decay_applied"
        }
        
    def _calculate_coordination_efficiency(self) -> float:
        """Calculate coordination efficiency metric."""
        total_services = len(self.service_registry)
        active_services = sum(1 for info in self.service_registry.values() if info.get("load", 0) > 0)
        
        if total_services == 0:
            return 0.0
            
        # Calculate efficiency based on service utilization and attention allocation
        utilization_efficiency = active_services / total_services
        attention_efficiency = min(1.0, sum(self.current_attention_allocation.values()) / self.attention_budget)
        
        return (utilization_efficiency + attention_efficiency) / 2
        
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and coordination metrics."""
        return {
            "service": self.service_name,
            "triad": self.triad,
            "role": self.role,
            "status": "active",
            "ecan_enabled": self.ecan_enabled,
            "attention_budget": self.attention_budget,
            "current_attention_allocation": self.current_attention_allocation,
            "service_registry": self.service_registry,
            "pending_tasks": self.task_queue.qsize(),
            "coordination_efficiency": self._calculate_coordination_efficiency()
        }