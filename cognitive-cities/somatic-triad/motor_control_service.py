"""
Motor Control Service - Somatic Triad

Movement coordination service that executes motor commands through Eva animation 
system integration and manages physical and behavioral actions.
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
from typing import Dict, Any, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class MotorControlService:
    """
    Motor Control Service implementing movement coordination.
    
    Executes motor commands through Eva animation system integration
    and coordinates physical and behavioral actions.
    """
    
    def __init__(self):
        """Initialize the Motor Control Service with Eva integration."""
        self.atomspace_manager = CognitiveAtomSpaceManager()
        self.membrane_controller = MembraneController(self.atomspace_manager.get_atomspace())
        
        self.service_name = "motor-control-service"
        self.triad = "somatic"
        self.coordination_type = "movement"
        
        # Eva integration parameters
        self.eva_integration = True
        self.behavior_queue = []
        self.active_behaviors = {}
        
        # Motor control parameters
        self.motor_commands = {}
        self.movement_state = "idle"
        
        # Initialize service and motor control systems
        self._initialize_service()
        self._initialize_motor_control_systems()
        
        logger.info("MotorControlService initialized with Eva animation integration")
        
    def _initialize_service(self):
        """Initialize service representation in AtomSpace."""
        # Create service atom and triad membership
        self.service_atom = self.atomspace_manager.create_triad_atom(
            "SomaticTriad",
            self.service_name
        )
        
        # Create motor control membrane rules
        self._create_motor_control_membrane_rules()
        
    def _create_motor_control_membrane_rules(self):
        """Create membrane rules for motor control processing."""
        # Rule for motor command execution
        context = EvaluationLink(
            PredicateNode("MotorCommandReceived"),
            ConceptNode(self.service_name)
        )
        
        action = ExecutionOutputLink(
            GroundedSchemaNode("py: execute_motor_command"),
            ListLink(VariableNode("$command"), VariableNode("$parameters"))
        )
        
        goal = EvaluationLink(
            PredicateNode("MotorCommandExecuted"),
            ConceptNode(self.service_name)
        )
        
        self.motor_execution_rule = self.membrane_controller.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad="SomaticMotorMembrane"
        )
        
        # Rule for behavior coordination
        context = EvaluationLink(
            PredicateNode("BehaviorCoordinationRequired"),
            ConceptNode(self.service_name)
        )
        
        action = ExecutionOutputLink(
            GroundedSchemaNode("py: coordinate_behaviors"),
            ListLink(VariableNode("$behaviors"))
        )
        
        goal = EvaluationLink(
            PredicateNode("BehaviorsCoordinated"),
            ConceptNode(self.service_name)
        )
        
        self.behavior_coordination_rule = self.membrane_controller.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad="SomaticMotorMembrane"
        )
        
    def _initialize_motor_control_systems(self):
        """Initialize motor control and Eva integration systems."""
        # Define motor command types
        self.motor_command_types = {
            "facial_expression": {
                "parameters": ["emotion", "intensity", "duration"],
                "eva_mapping": "facial_animation",
                "execution_time": 0.5
            },
            "head_movement": {
                "parameters": ["direction", "angle", "speed"],
                "eva_mapping": "head_control",
                "execution_time": 1.0
            },
            "eye_movement": {
                "parameters": ["target", "tracking_mode"],
                "eva_mapping": "eye_control",
                "execution_time": 0.3
            },
            "gesture": {
                "parameters": ["gesture_type", "emphasis", "timing"],
                "eva_mapping": "gesture_control",
                "execution_time": 2.0
            },
            "posture": {
                "parameters": ["posture_type", "transition_speed"],
                "eva_mapping": "posture_control",
                "execution_time": 3.0
            }
        }
        
        # Define behavior coordination patterns
        self.behavior_patterns = {
            "expressive_speaking": {
                "components": ["facial_expression", "head_movement", "gesture"],
                "coordination": "synchronized",
                "priority": "high"
            },
            "attentive_listening": {
                "components": ["eye_movement", "posture", "facial_expression"],
                "coordination": "sequential",
                "priority": "medium"
            },
            "emotional_response": {
                "components": ["facial_expression", "posture", "gesture"],
                "coordination": "layered",
                "priority": "high"
            },
            "idle_behavior": {
                "components": ["eye_movement", "head_movement"],
                "coordination": "random",
                "priority": "low"
            }
        }
        
    async def execute_motor_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute motor commands through Eva animation system.
        
        Args:
            command: Dictionary containing motor command and parameters
            
        Returns:
            Dictionary containing execution results and status
        """
        try:
            command_type = command.get("type", "unknown")
            parameters = command.get("parameters", {})
            priority = command.get("priority", "medium")
            
            logger.debug(f"Executing motor command: {command_type}")
            
            # Validate command type
            if command_type not in self.motor_command_types:
                return {"error": f"Unknown command type: {command_type}", "service": self.service_name}
                
            # Get command specification
            command_spec = self.motor_command_types[command_type]
            
            # Validate parameters
            validation_result = await self._validate_command_parameters(parameters, command_spec)
            if not validation_result["valid"]:
                return {"error": f"Invalid parameters: {validation_result['errors']}", "service": self.service_name}
                
            # Execute through Eva integration
            eva_result = await self._eva_motor_execute(command_type, parameters, command_spec)
            
            # Update motor state
            await self._update_motor_state(command_type, parameters)
            
            # Log execution
            execution_log = await self._log_motor_execution(command, eva_result)
            
            response = {
                "service": self.service_name,
                "command_type": command_type,
                "parameters": parameters,
                "eva_result": eva_result,
                "execution_status": "completed",
                "execution_time": command_spec["execution_time"],
                "motor_state": self.movement_state,
                "execution_log": execution_log
            }
            
            logger.info(f"Executed motor command: {command_type}")
            return response
            
        except Exception as e:
            logger.error(f"Error in motor command execution: {e}")
            return {"error": str(e), "service": self.service_name}
            
    async def _validate_command_parameters(self, parameters: Dict[str, Any], 
                                         command_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate motor command parameters."""
        validation = {"valid": True, "errors": []}
        
        required_params = command_spec.get("parameters", [])
        
        for param in required_params:
            if param not in parameters:
                validation["valid"] = False
                validation["errors"].append(f"Missing required parameter: {param}")
                
        # Additional validation based on parameter types
        if "intensity" in parameters:
            intensity = parameters["intensity"]
            if not isinstance(intensity, (int, float)) or not 0 <= intensity <= 1:
                validation["valid"] = False
                validation["errors"].append("Intensity must be a number between 0 and 1")
                
        if "duration" in parameters:
            duration = parameters["duration"]
            if not isinstance(duration, (int, float)) or duration <= 0:
                validation["valid"] = False
                validation["errors"].append("Duration must be a positive number")
                
        return validation
        
    async def _eva_motor_execute(self, command_type: str, parameters: Dict[str, Any], 
                               command_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute motor command through Eva animation system."""
        if not self.eva_integration:
            return {"status": "eva_disabled", "simulated": True}
            
        eva_mapping = command_spec["eva_mapping"]
        
        # Simulate Eva integration - in real implementation would call actual Eva API
        eva_result = {
            "eva_command": eva_mapping,
            "eva_parameters": parameters,
            "execution_status": "completed",
            "eva_response_time": command_spec["execution_time"],
            "eva_feedback": f"Successfully executed {eva_mapping}"
        }
        
        # Add command-specific Eva simulation
        if command_type == "facial_expression":
            eva_result["facial_animation"] = await self._simulate_facial_animation(parameters)
        elif command_type == "head_movement":
            eva_result["head_position"] = await self._simulate_head_movement(parameters)
        elif command_type == "eye_movement":
            eva_result["eye_position"] = await self._simulate_eye_movement(parameters)
        elif command_type == "gesture":
            eva_result["gesture_execution"] = await self._simulate_gesture(parameters)
        elif command_type == "posture":
            eva_result["posture_state"] = await self._simulate_posture_change(parameters)
            
        return eva_result
        
    async def _simulate_facial_animation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate facial animation execution."""
        emotion = parameters.get("emotion", "neutral")
        intensity = parameters.get("intensity", 0.5)
        duration = parameters.get("duration", 1.0)
        
        return {
            "emotion_displayed": emotion,
            "intensity_level": intensity,
            "animation_duration": duration,
            "facial_muscles_activated": ["zygomatic", "corrugator", "orbicularis"]
        }
        
    async def _simulate_head_movement(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate head movement execution."""
        direction = parameters.get("direction", "center")
        angle = parameters.get("angle", 0)
        speed = parameters.get("speed", "medium")
        
        return {
            "head_direction": direction,
            "rotation_angle": angle,
            "movement_speed": speed,
            "final_position": {"yaw": angle, "pitch": 0, "roll": 0}
        }
        
    async def _simulate_eye_movement(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate eye movement execution."""
        target = parameters.get("target", "center")
        tracking_mode = parameters.get("tracking_mode", "normal")
        
        return {
            "gaze_target": target,
            "tracking_mode": tracking_mode,
            "eye_position": {"left_eye": target, "right_eye": target},
            "convergence": "normal"
        }
        
    async def _simulate_gesture(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate gesture execution."""
        gesture_type = parameters.get("gesture_type", "open_hand")
        emphasis = parameters.get("emphasis", "medium")
        timing = parameters.get("timing", "synchronized")
        
        return {
            "gesture": gesture_type,
            "emphasis_level": emphasis,
            "timing_pattern": timing,
            "gesture_completion": "successful"
        }
        
    async def _simulate_posture_change(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate posture change execution."""
        posture_type = parameters.get("posture_type", "neutral")
        transition_speed = parameters.get("transition_speed", "medium")
        
        return {
            "posture": posture_type,
            "transition_speed": transition_speed,
            "posture_stability": "stable",
            "alignment": "optimal"
        }
        
    async def _update_motor_state(self, command_type: str, parameters: Dict[str, Any]) -> None:
        """Update internal motor state tracking."""
        # Update movement state based on executed command
        if command_type in ["head_movement", "gesture", "posture"]:
            self.movement_state = "active"
        elif command_type in ["facial_expression", "eye_movement"]:
            self.movement_state = "expressive"
        else:
            self.movement_state = "responding"
            
        # Store last executed command
        self.motor_commands[command_type] = {
            "parameters": parameters,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
    async def _log_motor_execution(self, command: Dict[str, Any], 
                                 eva_result: Dict[str, Any]) -> Dict[str, Any]:
        """Log motor command execution details."""
        return {
            "command_id": command.get("id", "unknown"),
            "execution_timestamp": datetime.now().isoformat(),
            "command_type": command.get("type"),
            "parameters": command.get("parameters", {}),
            "eva_status": eva_result.get("execution_status"),
            "execution_duration": eva_result.get("eva_response_time", 0),
            "success": True
        }
        
    async def coordinate_behaviors(self, behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Coordinate multiple behaviors according to behavior patterns.
        
        Args:
            behaviors: List of behavior dictionaries to coordinate
            
        Returns:
            Dictionary containing coordination results
        """
        try:
            logger.debug(f"Coordinating {len(behaviors)} behaviors")
            
            # Group behaviors by pattern
            behavior_groups = await self._group_behaviors_by_pattern(behaviors)
            
            # Execute coordination for each group
            coordination_results = []
            for pattern_name, pattern_behaviors in behavior_groups.items():
                pattern_result = await self._execute_behavior_pattern(pattern_name, pattern_behaviors)
                coordination_results.append(pattern_result)
                
            # Manage behavior queue
            queue_status = await self._manage_behavior_queue(behaviors)
            
            response = {
                "service": self.service_name,
                "coordinated_behaviors": len(behaviors),
                "behavior_groups": len(behavior_groups),
                "coordination_results": coordination_results,
                "queue_status": queue_status,
                "coordination_efficiency": self._calculate_coordination_efficiency(coordination_results)
            }
            
            logger.info(f"Coordinated {len(behaviors)} behaviors across {len(behavior_groups)} patterns")
            return response
            
        except Exception as e:
            logger.error(f"Error in behavior coordination: {e}")
            return {"error": str(e), "service": self.service_name}
            
    async def _group_behaviors_by_pattern(self, behaviors: List[Dict[str, Any]]) -> Dict[str, List]:
        """Group behaviors by coordination pattern."""
        behavior_groups = {}
        
        for behavior in behaviors:
            behavior_type = behavior.get("type", "unknown")
            
            # Find matching pattern
            matching_pattern = None
            for pattern_name, pattern_info in self.behavior_patterns.items():
                if behavior_type in pattern_info["components"]:
                    matching_pattern = pattern_name
                    break
                    
            if matching_pattern:
                if matching_pattern not in behavior_groups:
                    behavior_groups[matching_pattern] = []
                behavior_groups[matching_pattern].append(behavior)
            else:
                # Default to idle behavior pattern
                if "idle_behavior" not in behavior_groups:
                    behavior_groups["idle_behavior"] = []
                behavior_groups["idle_behavior"].append(behavior)
                
        return behavior_groups
        
    async def _execute_behavior_pattern(self, pattern_name: str, 
                                      behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute behaviors according to coordination pattern."""
        pattern_info = self.behavior_patterns.get(pattern_name, self.behavior_patterns["idle_behavior"])
        coordination_type = pattern_info["coordination"]
        
        if coordination_type == "synchronized":
            result = await self._execute_synchronized_behaviors(behaviors)
        elif coordination_type == "sequential":
            result = await self._execute_sequential_behaviors(behaviors)
        elif coordination_type == "layered":
            result = await self._execute_layered_behaviors(behaviors)
        elif coordination_type == "random":
            result = await self._execute_random_behaviors(behaviors)
        else:
            result = await self._execute_default_behaviors(behaviors)
            
        result["pattern"] = pattern_name
        result["coordination_type"] = coordination_type
        return result
        
    async def _execute_synchronized_behaviors(self, behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute behaviors simultaneously."""
        execution_tasks = []
        for behavior in behaviors:
            task = asyncio.create_task(self.execute_motor_command(behavior))
            execution_tasks.append(task)
            
        results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        return {
            "execution_type": "synchronized",
            "behavior_count": len(behaviors),
            "results": results,
            "success_rate": sum(1 for r in results if not isinstance(r, Exception)) / len(results)
        }
        
    async def _execute_sequential_behaviors(self, behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute behaviors in sequence."""
        results = []
        for behavior in behaviors:
            result = await self.execute_motor_command(behavior)
            results.append(result)
            
        return {
            "execution_type": "sequential",
            "behavior_count": len(behaviors),
            "results": results,
            "success_rate": sum(1 for r in results if "error" not in r) / len(results)
        }
        
    async def _execute_layered_behaviors(self, behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute behaviors in overlapping layers."""
        # Execute with staggered timing
        results = []
        for i, behavior in enumerate(behaviors):
            # Add delay between behaviors for layered effect
            if i > 0:
                await asyncio.sleep(0.2)
            result = await self.execute_motor_command(behavior)
            results.append(result)
            
        return {
            "execution_type": "layered",
            "behavior_count": len(behaviors),
            "results": results,
            "layering_delay": 0.2
        }
        
    async def _execute_random_behaviors(self, behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute behaviors with random timing."""
        # Shuffle and execute with random delays
        import random
        shuffled_behaviors = behaviors.copy()
        random.shuffle(shuffled_behaviors)
        
        results = []
        for behavior in shuffled_behaviors:
            # Random delay between 0.1 and 1.0 seconds
            delay = random.uniform(0.1, 1.0)
            await asyncio.sleep(delay)
            result = await self.execute_motor_command(behavior)
            results.append(result)
            
        return {
            "execution_type": "random",
            "behavior_count": len(behaviors),
            "results": results,
            "randomization": True
        }
        
    async def _execute_default_behaviors(self, behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute behaviors with default coordination."""
        return await self._execute_sequential_behaviors(behaviors)
        
    async def _manage_behavior_queue(self, new_behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Manage the behavior queue and active behaviors."""
        # Add new behaviors to queue
        self.behavior_queue.extend(new_behaviors)
        
        # Process queue (simplified implementation)
        processed_count = min(len(self.behavior_queue), 5)  # Process up to 5 behaviors
        processed_behaviors = self.behavior_queue[:processed_count]
        self.behavior_queue = self.behavior_queue[processed_count:]
        
        return {
            "queue_length": len(self.behavior_queue),
            "processed_behaviors": processed_count,
            "active_behaviors": len(self.active_behaviors)
        }
        
    def _calculate_coordination_efficiency(self, coordination_results: List[Dict[str, Any]]) -> float:
        """Calculate coordination efficiency metric."""
        if not coordination_results:
            return 0.0
            
        success_rates = [result.get("success_rate", 0) for result in coordination_results]
        return sum(success_rates) / len(success_rates)
        
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and motor control metrics."""
        return {
            "service": self.service_name,
            "triad": self.triad,
            "coordination_type": self.coordination_type,
            "status": "active",
            "eva_integration": self.eva_integration,
            "movement_state": self.movement_state,
            "behavior_queue_length": len(self.behavior_queue),
            "active_behaviors": len(self.active_behaviors),
            "motor_command_types": len(self.motor_command_types),
            "behavior_patterns": len(self.behavior_patterns)
        }