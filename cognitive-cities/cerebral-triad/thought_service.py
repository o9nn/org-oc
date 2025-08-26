"""
Thought Service - Cerebral Triad

Right Hemisphere service focused on intuitive idea generation and creative processing.
Implements intuitive, creative cognitive patterns using Ghost DSL integration.
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

logger = logging.getLogger(__name__)


class ThoughtService:
    """
    Thought Service implementing right hemisphere intuitive processing.
    
    Generates creative, intuitive responses and explores possibilities
    using Ghost DSL patterns and right-brain cognitive processing.
    """
    
    def __init__(self):
        """Initialize the Thought Service with AtomSpace and membrane control."""
        self.atomspace_manager = CognitiveAtomSpaceManager()
        self.membrane_controller = MembraneController(self.atomspace_manager.get_atomspace())
        
        self.hemisphere = "right"  # Intuitive Idea Potential
        self.triad = "cerebral"
        self.service_name = "thought-service"
        
        # Initialize service in AtomSpace
        self._initialize_service()
        
        # Initialize Ghost-like rule patterns for intuitive processing
        self._initialize_intuitive_patterns()
        
        logger.info(f"ThoughtService initialized - {self.hemisphere} hemisphere processing")
        
    def _initialize_service(self):
        """Initialize service representation in AtomSpace."""
        # Create service atom and triad membership
        self.service_atom = self.atomspace_manager.create_triad_atom(
            "CerebralTriad", 
            self.service_name
        )
        
        # Create hemisphere assignment
        self.hemisphere_atom = self.atomspace_manager.create_hemisphere_atom(
            self.service_name,
            self.hemisphere
        )
        
        # Create membrane rules for thought service
        self._create_membrane_rules()
        
    def _create_membrane_rules(self):
        """Create membrane rules for thought service processing."""
        # Rule for creative idea generation
        context = EvaluationLink(
            PredicateNode("CreativeInputReceived"),
            ConceptNode(self.service_name)
        )
        
        action = ExecutionOutputLink(
            GroundedSchemaNode("py: generate_intuitive_ideas"),
            ListLink(VariableNode("$input"))
        )
        
        goal = EvaluationLink(
            PredicateNode("IntuitiveIdeasGenerated"),
            ConceptNode(self.service_name)
        )
        
        self.creative_rule = self.membrane_controller.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad="CerebralThoughtMembrane"
        )
        
    def _initialize_intuitive_patterns(self):
        """Initialize Ghost-like patterns for intuitive processing."""
        self.intuitive_patterns = {
            "possibility_exploration": {
                "pattern": "explore possibilities about *",
                "response_type": "divergent_thinking",
                "creativity_weight": 0.9
            },
            "creative_synthesis": {
                "pattern": "combine concepts * and *",
                "response_type": "conceptual_blending",
                "creativity_weight": 0.8
            },
            "metaphorical_thinking": {
                "pattern": "find metaphor for *",
                "response_type": "metaphor_generation",
                "creativity_weight": 0.85
            },
            "emotional_insight": {
                "pattern": "understand feeling of *",
                "response_type": "emotional_processing",
                "creativity_weight": 0.7
            }
        }
        
    async def generate_intuitive_ideas(self, sensory_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate creative, intuitive responses from sensory input.
        
        Args:
            sensory_input: Dictionary containing sensory data and context
            
        Returns:
            Dictionary containing generated intuitive ideas and insights
        """
        try:
            input_text = sensory_input.get('text', '')
            input_context = sensory_input.get('context', {})
            
            logger.debug(f"Generating intuitive ideas for: {input_text}")
            
            # Apply intuitive processing patterns
            ideas = await self._apply_intuitive_patterns(input_text, input_context)
            
            # Generate creative associations
            associations = await self._generate_creative_associations(input_text)
            
            # Explore possibilities
            possibilities = await self._explore_possibilities(input_text, input_context)
            
            response = {
                "service": self.service_name,
                "hemisphere": self.hemisphere,
                "processing_type": "intuitive",
                "ideas": ideas,
                "associations": associations,
                "possibilities": possibilities,
                "confidence": 0.7,  # Intuitive processing has moderate confidence
                "creativity_score": self._calculate_creativity_score(ideas, associations)
            }
            
            logger.info(f"Generated {len(ideas)} intuitive ideas")
            return response
            
        except Exception as e:
            logger.error(f"Error in intuitive idea generation: {e}")
            return {"error": str(e), "service": self.service_name}
            
    async def _apply_intuitive_patterns(self, input_text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply intuitive processing patterns to generate ideas."""
        ideas = []
        
        for pattern_name, pattern_info in self.intuitive_patterns.items():
            if self._pattern_matches(input_text, pattern_info["pattern"]):
                idea = {
                    "pattern": pattern_name,
                    "type": pattern_info["response_type"],
                    "content": await self._generate_pattern_response(input_text, pattern_info),
                    "weight": pattern_info["creativity_weight"]
                }
                ideas.append(idea)
                
        return ideas
        
    async def _generate_creative_associations(self, input_text: str) -> List[str]:
        """Generate creative associations using right-brain processing."""
        # Simulate creative association generation
        associations = []
        
        # Extract key concepts from input
        concepts = self._extract_concepts(input_text)
        
        for concept in concepts:
            # Generate associations through AtomSpace links
            related_concepts = self._find_related_concepts(concept)
            associations.extend(related_concepts[:3])  # Take top 3 associations
            
        return list(set(associations))  # Remove duplicates
        
    async def _explore_possibilities(self, input_text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Explore possibilities and alternative perspectives."""
        possibilities = []
        
        # Generate "what if" scenarios
        what_if_scenarios = [
            f"What if {input_text} were approached differently?",
            f"What if we considered the opposite of {input_text}?",
            f"What if {input_text} were combined with something unexpected?"
        ]
        
        for scenario in what_if_scenarios:
            possibility = {
                "scenario": scenario,
                "type": "hypothetical",
                "exploration_depth": "conceptual"
            }
            possibilities.append(possibility)
            
        return possibilities
        
    def _pattern_matches(self, text: str, pattern: str) -> bool:
        """Check if text matches intuitive pattern."""
        # Simplified pattern matching - in real implementation would use more sophisticated NLP
        pattern_keywords = pattern.replace("*", "").split()
        text_lower = text.lower()
        
        return any(keyword.lower() in text_lower for keyword in pattern_keywords)
        
    async def _generate_pattern_response(self, input_text: str, pattern_info: Dict[str, Any]) -> str:
        """Generate response based on pattern type."""
        response_type = pattern_info["response_type"]
        
        if response_type == "divergent_thinking":
            return f"Multiple perspectives on '{input_text}' could include..."
        elif response_type == "conceptual_blending":
            return f"Blending concepts from '{input_text}' with novel elements..."
        elif response_type == "metaphor_generation":
            return f"'{input_text}' is like..."
        elif response_type == "emotional_processing":
            return f"The emotional dimension of '{input_text}' suggests..."
        else:
            return f"Intuitive insight about '{input_text}'..."
            
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text for association generation."""
        # Simplified concept extraction - in real implementation would use NLP
        words = text.split()
        concepts = [word.strip('.,!?') for word in words if len(word) > 3]
        return concepts[:5]  # Return top 5 concepts
        
    def _find_related_concepts(self, concept: str) -> List[str]:
        """Find related concepts in AtomSpace."""
        # Simplified concept finding - in real implementation would query AtomSpace
        concept_associations = {
            "creative": ["innovative", "artistic", "original"],
            "thinking": ["reasoning", "cognition", "awareness"],
            "emotion": ["feeling", "sentiment", "mood"],
            "learning": ["education", "knowledge", "understanding"]
        }
        
        return concept_associations.get(concept.lower(), [])
        
    def _calculate_creativity_score(self, ideas: List[Dict], associations: List[str]) -> float:
        """Calculate creativity score based on generated content."""
        idea_score = sum(idea.get("weight", 0.5) for idea in ideas) / max(len(ideas), 1)
        association_score = min(len(associations) * 0.1, 1.0)
        
        return (idea_score + association_score) / 2
        
    async def process_cerebral_communication(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process communication from other cerebral triad services.
        
        Args:
            message: Communication message from another cerebral service
            
        Returns:
            Response message with intuitive insights
        """
        source = message.get("source", "unknown")
        content = message.get("content", {})
        
        logger.debug(f"Processing cerebral communication from {source}")
        
        # Apply intuitive processing to the communication content
        intuitive_response = await self.generate_intuitive_ideas(content)
        
        response = {
            "source": self.service_name,
            "target": source,
            "type": "intuitive_insights",
            "content": intuitive_response,
            "hemisphere": self.hemisphere
        }
        
        return response
        
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and metrics."""
        return {
            "service": self.service_name,
            "triad": self.triad,
            "hemisphere": self.hemisphere,
            "status": "active",
            "atomspace_atoms": self.atomspace_manager.get_atom_count(),
            "patterns_loaded": len(self.intuitive_patterns),
            "processing_type": "right_hemisphere_intuitive"
        }