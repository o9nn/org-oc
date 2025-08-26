"""
Cognitive AtomSpace Manager

This module provides AtomSpace integration for the Cognitive Cities Architecture.
It manages atoms representing triad components and implements the knowledge
representation layer using OpenCog's AtomSpace framework.
"""

from opencog.atomspace import AtomSpace, types
from opencog.type_constructors import *
from opencog.utilities import initialize_opencog
import logging

logger = logging.getLogger(__name__)


class CognitiveAtomSpaceManager:
    """
    Manages AtomSpace integration for Cognitive Cities Architecture.
    
    Provides methods for creating and managing atoms that represent
    triad components, their relationships, and the cognitive state
    of the system.
    """
    
    def __init__(self):
        """Initialize the AtomSpace and OpenCog utilities."""
        self.atomspace = AtomSpace()
        initialize_opencog(self.atomspace)
        
        # Initialize triad categories
        self._initialize_triad_categories()
        
        logger.info("CognitiveAtomSpaceManager initialized with AtomSpace")
        
    def _initialize_triad_categories(self):
        """Create base concept nodes for the three triads."""
        self.cerebral_triad = ConceptNode("CerebralTriad")
        self.somatic_triad = ConceptNode("SomaticTriad")  
        self.autonomic_triad = ConceptNode("AutonomicTriad")
        
        # Create hemisphere distinctions for cerebral triad
        self.right_hemisphere = ConceptNode("RightHemisphere")
        self.left_hemisphere = ConceptNode("LeftHemisphere")
        
        # Create polarity distinctions for autonomic triad
        self.sympathetic = ConceptNode("Sympathetic")
        self.parasympathetic = ConceptNode("Parasympathetic")
        
        # Link hemispheres to cerebral triad
        InheritanceLink(self.right_hemisphere, self.cerebral_triad)
        InheritanceLink(self.left_hemisphere, self.cerebral_triad)
        
        # Link polarities to autonomic triad
        InheritanceLink(self.sympathetic, self.autonomic_triad)
        InheritanceLink(self.parasympathetic, self.autonomic_triad)
        
    def create_triad_atom(self, triad_name, component_name):
        """
        Create atoms representing triad components.
        
        Args:
            triad_name (str): Name of the triad (cerebral, somatic, autonomic)
            component_name (str): Name of the component service
            
        Returns:
            InheritanceLink: Link representing component membership in triad
        """
        triad_node = ConceptNode(triad_name)
        component_node = ConceptNode(component_name)
        
        inheritance_link = InheritanceLink(component_node, triad_node)
        
        logger.debug(f"Created triad atom: {component_name} -> {triad_name}")
        return inheritance_link
        
    def create_hemisphere_atom(self, component_name, hemisphere):
        """
        Create atoms with hemisphere distinctions for cerebral triad.
        
        Args:
            component_name (str): Name of the component service
            hemisphere (str): 'right' or 'left'
            
        Returns:
            InheritanceLink: Link representing hemisphere assignment
        """
        component_node = ConceptNode(component_name)
        
        if hemisphere.lower() == 'right':
            hemisphere_node = self.right_hemisphere
        elif hemisphere.lower() == 'left':
            hemisphere_node = self.left_hemisphere
        else:
            raise ValueError(f"Invalid hemisphere: {hemisphere}")
            
        inheritance_link = InheritanceLink(component_node, hemisphere_node)
        
        logger.debug(f"Created hemisphere atom: {component_name} -> {hemisphere}")
        return inheritance_link
        
    def create_polarity_atom(self, component_name, polarity):
        """
        Create atoms with polarity distinctions for autonomic triad.
        
        Args:
            component_name (str): Name of the component service
            polarity (str): 'sympathetic' or 'parasympathetic'
            
        Returns:
            InheritanceLink: Link representing polarity assignment
        """
        component_node = ConceptNode(component_name)
        
        if polarity.lower() == 'sympathetic':
            polarity_node = self.sympathetic
        elif polarity.lower() == 'parasympathetic':
            polarity_node = self.parasympathetic
        else:
            raise ValueError(f"Invalid polarity: {polarity}")
            
        inheritance_link = InheritanceLink(component_node, polarity_node)
        
        logger.debug(f"Created polarity atom: {component_name} -> {polarity}")
        return inheritance_link
        
    def create_communication_pathway(self, source_triad, target_triad, event_type):
        """
        Create atoms representing communication pathways between triads.
        
        Args:
            source_triad (str): Source triad name
            target_triad (str): Target triad name  
            event_type (str): Type of communication event
            
        Returns:
            EvaluationLink: Link representing the communication pathway
        """
        source_node = ConceptNode(source_triad)
        target_node = ConceptNode(target_triad)
        event_node = ConceptNode(event_type)
        
        pathway_predicate = PredicateNode("CommunicationPathway")
        
        evaluation_link = EvaluationLink(
            pathway_predicate,
            ListLink(source_node, target_node, event_node)
        )
        
        logger.debug(f"Created communication pathway: {source_triad} -> {target_triad} ({event_type})")
        return evaluation_link
        
    def get_triad_components(self, triad_name):
        """
        Retrieve all components belonging to a specific triad.
        
        Args:
            triad_name (str): Name of the triad
            
        Returns:
            list: List of component atoms in the triad
        """
        triad_node = ConceptNode(triad_name)
        
        # Find all nodes that inherit from this triad
        query = GetLink(
            VariableNode("$component"),
            InheritanceLink(
                VariableNode("$component"),
                triad_node
            )
        )
        
        result = query.execute(self.atomspace)
        components = [atom for atom in result.out]
        
        logger.debug(f"Found {len(components)} components in {triad_name}")
        return components
        
    def get_atomspace(self):
        """
        Get the underlying AtomSpace instance.
        
        Returns:
            AtomSpace: The managed AtomSpace instance
        """
        return self.atomspace
        
    def get_atom_count(self):
        """
        Get the current number of atoms in the AtomSpace.
        
        Returns:
            int: Number of atoms in the AtomSpace
        """
        return len(self.atomspace)