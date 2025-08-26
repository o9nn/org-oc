"""
P-System Membrane Controller

This module implements membrane-based process control using OpenPsi.
It creates and manages membrane rules that control interaction between
cognitive triads in the Cognitive Cities Architecture.
"""

from opencog.openpsi import *
from opencog.atomspace import types
from opencog.type_constructors import *
import logging

logger = logging.getLogger(__name__)


class MembraneController:
    """
    Manages P-System membrane rules using OpenPsi framework.
    
    Implements membrane-based control mechanisms that regulate
    communication and processing between cognitive triads.
    """
    
    def __init__(self, atomspace):
        """
        Initialize the membrane controller with an AtomSpace.
        
        Args:
            atomspace: OpenCog AtomSpace instance
        """
        self.atomspace = atomspace
        
        # Initialize triad categories for membrane rules
        self._initialize_membrane_categories()
        
        logger.info("MembraneController initialized with OpenPsi integration")
        
    def _initialize_membrane_categories(self):
        """Initialize membrane categories for each triad."""
        # Create membrane categories for triads
        self.cerebral_membrane = psi_add_category(ConceptNode("CerebralMembrane"))
        self.somatic_membrane = psi_add_category(ConceptNode("SomaticMembrane"))
        self.autonomic_membrane = psi_add_category(ConceptNode("AutonomicMembrane"))
        
        # Create inter-triad membrane categories
        self.cerebral_to_somatic = psi_add_category(ConceptNode("CerebralToSomaticMembrane"))
        self.cerebral_to_autonomic = psi_add_category(ConceptNode("CerebralToAutonomicMembrane"))
        self.somatic_to_autonomic = psi_add_category(ConceptNode("SomaticToAutonomicMembrane"))
        
    def create_membrane_rule(self, context, action, goal, triad, strength=0.8, confidence=0.9):
        """
        Create P-System membrane rules as OpenPsi ImplicationLinks.
        
        Args:
            context: Context conditions for rule activation
            action: Action to execute when rule fires
            goal: Goal state the rule aims to achieve
            triad: Triad category for the rule
            strength (float): Truth value strength (default 0.8)
            confidence (float): Truth value confidence (default 0.9)
            
        Returns:
            Rule atom representing the membrane rule
        """
        try:
            # Create truth value for the rule
            tv = TruthValue(strength, confidence)
            
            # Create the psi rule using OpenPsi framework
            rule = psi_rule(
                context=context,
                action=action,
                goal=goal,
                stv=tv
            )
            
            # Add rule to triad-specific category
            if isinstance(triad, str):
                triad_category = ConceptNode(triad)
            else:
                triad_category = triad
                
            psi_add_category(triad_category, rule)
            
            logger.debug(f"Created membrane rule for {triad_category.name}")
            return rule
            
        except Exception as e:
            logger.error(f"Failed to create membrane rule: {e}")
            raise
            
    def create_attention_membrane_rule(self, source_triad, attention_threshold=0.7):
        """
        Create membrane rule for attention-based processing control.
        
        Args:
            source_triad (str): Name of the source triad
            attention_threshold (float): Minimum attention level required
            
        Returns:
            Rule atom for attention-based membrane control
        """
        # Define context: attention level above threshold
        context = GreaterThanLink(
            EvaluationLink(
                PredicateNode("AttentionLevel"),
                ConceptNode(source_triad)
            ),
            NumberNode(attention_threshold)
        )
        
        # Define action: allow processing
        action = ExecutionOutputLink(
            GroundedSchemaNode("scm: enable-triad-processing"),
            ListLink(ConceptNode(source_triad))
        )
        
        # Define goal: maintain optimal attention allocation
        goal = EvaluationLink(
            PredicateNode("OptimalAttentionAllocation"),
            ConceptNode(source_triad)
        )
        
        return self.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad=f"{source_triad}AttentionMembrane"
        )
        
    def create_communication_membrane_rule(self, source_triad, target_triad, event_type):
        """
        Create membrane rule for inter-triad communication control.
        
        Args:
            source_triad (str): Source triad name
            target_triad (str): Target triad name
            event_type (str): Type of communication event
            
        Returns:
            Rule atom for communication membrane control
        """
        # Define context: communication event pending
        context = EvaluationLink(
            PredicateNode("CommunicationPending"),
            ListLink(
                ConceptNode(source_triad),
                ConceptNode(target_triad),
                ConceptNode(event_type)
            )
        )
        
        # Define action: route communication
        action = ExecutionOutputLink(
            GroundedSchemaNode("scm: route-triad-communication"),
            ListLink(
                ConceptNode(source_triad),
                ConceptNode(target_triad),
                ConceptNode(event_type)
            )
        )
        
        # Define goal: successful communication delivery
        goal = EvaluationLink(
            PredicateNode("CommunicationDelivered"),
            ListLink(
                ConceptNode(source_triad),
                ConceptNode(target_triad),
                ConceptNode(event_type)
            )
        )
        
        membrane_category = f"{source_triad}To{target_triad}Membrane"
        
        return self.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad=membrane_category
        )
        
    def create_load_balancing_membrane_rule(self, triad_name, max_load=0.8):
        """
        Create membrane rule for load balancing within a triad.
        
        Args:
            triad_name (str): Name of the triad
            max_load (float): Maximum allowed load threshold
            
        Returns:
            Rule atom for load balancing membrane control
        """
        # Define context: load exceeds threshold
        context = GreaterThanLink(
            EvaluationLink(
                PredicateNode("ProcessingLoad"),
                ConceptNode(triad_name)
            ),
            NumberNode(max_load)
        )
        
        # Define action: redistribute load
        action = ExecutionOutputLink(
            GroundedSchemaNode("scm: redistribute-triad-load"),
            ListLink(ConceptNode(triad_name))
        )
        
        # Define goal: balanced processing load
        goal = EvaluationLink(
            PredicateNode("BalancedLoad"),
            ConceptNode(triad_name)
        )
        
        return self.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad=f"{triad_name}LoadBalancingMembrane"
        )
        
    def create_emotional_regulation_membrane_rule(self, emotion_type, regulation_strength=0.6):
        """
        Create membrane rule for emotional regulation in autonomic triad.
        
        Args:
            emotion_type (str): Type of emotion to regulate
            regulation_strength (float): Strength of regulation response
            
        Returns:
            Rule atom for emotional regulation membrane control
        """
        # Define context: strong emotional activation
        context = GreaterThanLink(
            EvaluationLink(
                PredicateNode("EmotionalActivation"),
                ConceptNode(emotion_type)
            ),
            NumberNode(0.7)
        )
        
        # Define action: apply emotional regulation
        action = ExecutionOutputLink(
            GroundedSchemaNode("scm: regulate-emotion"),
            ListLink(
                ConceptNode(emotion_type),
                NumberNode(regulation_strength)
            )
        )
        
        # Define goal: emotional homeostasis
        goal = EvaluationLink(
            PredicateNode("EmotionalHomeostasis"),
            ConceptNode(emotion_type)
        )
        
        return self.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad="AutonomicEmotionalMembrane"
        )
        
    def get_membrane_rules(self, triad_category):
        """
        Retrieve all membrane rules for a specific triad category.
        
        Args:
            triad_category: Triad category concept node or string
            
        Returns:
            list: List of membrane rules in the category
        """
        if isinstance(triad_category, str):
            category_node = ConceptNode(triad_category)
        else:
            category_node = triad_category
            
        try:
            rules = psi_get_rules(category_node)
            logger.debug(f"Found {len(rules)} membrane rules for {category_node.name}")
            return rules
        except Exception as e:
            logger.error(f"Failed to get membrane rules: {e}")
            return []
            
    def activate_membrane_processing(self, triad_category):
        """
        Activate membrane processing for a specific triad.
        
        Args:
            triad_category: Triad category to activate
            
        Returns:
            bool: True if activation successful
        """
        try:
            if isinstance(triad_category, str):
                category_node = ConceptNode(triad_category)
            else:
                category_node = triad_category
                
            # Use OpenPsi to run one step of processing for the category
            psi_step(category_node)
            
            logger.debug(f"Activated membrane processing for {category_node.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate membrane processing: {e}")
            return False