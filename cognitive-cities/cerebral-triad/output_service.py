"""
Output Service - Cerebral Triad

Left Hemisphere service focused on applied technique commitment and structured output delivery.
Implements practical application and systematic output formatting.
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


class OutputService:
    """
    Output Service implementing left hemisphere applied technique processing.
    
    Delivers structured, practical responses with focus on applied techniques
    and systematic output formatting for practical implementation.
    """
    
    def __init__(self):
        """Initialize the Output Service with applied technique capabilities."""
        self.atomspace_manager = CognitiveAtomSpaceManager()
        self.membrane_controller = MembraneController(self.atomspace_manager.get_atomspace())
        
        self.hemisphere = "left"  # Applied Technique Commitment
        self.triad = "cerebral"
        self.service_name = "output-service"
        self.processing_focus = "applied_technique"
        
        # Initialize service and output formatting systems
        self._initialize_service()
        self._initialize_output_formats()
        
        logger.info(f"OutputService initialized - {self.hemisphere} hemisphere applied processing")
        
    def _initialize_service(self):
        """Initialize service representation in AtomSpace."""
        # Create service atom and triad membership
        self.service_atom = self.atomspace_manager.create_triad_atom(
            "CerebralTriad",
            self.service_name
        )
        
        # Create hemisphere assignment for left hemisphere
        self.hemisphere_atom = self.atomspace_manager.create_hemisphere_atom(
            self.service_name,
            self.hemisphere
        )
        
        # Create output membrane rules
        self._create_output_membrane_rules()
        
    def _create_output_membrane_rules(self):
        """Create membrane rules for output processing."""
        # Rule for structured output generation
        context = EvaluationLink(
            PredicateNode("OutputGenerationRequired"),
            ConceptNode(self.service_name)
        )
        
        action = ExecutionOutputLink(
            GroundedSchemaNode("py: generate_structured_output"),
            ListLink(VariableNode("$content"), VariableNode("$format"))
        )
        
        goal = EvaluationLink(
            PredicateNode("StructuredOutputDelivered"),
            ConceptNode(self.service_name)
        )
        
        self.output_rule = self.membrane_controller.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad="CerebralOutputMembrane"
        )
        
        # Rule for practical application formatting
        context = EvaluationLink(
            PredicateNode("PracticalApplicationRequired"),
            ConceptNode(self.service_name)
        )
        
        action = ExecutionOutputLink(
            GroundedSchemaNode("py: format_practical_application"),
            ListLink(VariableNode("$abstract_content"))
        )
        
        goal = EvaluationLink(
            PredicateNode("PracticalFormatDelivered"),
            ConceptNode(self.service_name)
        )
        
        self.application_rule = self.membrane_controller.create_membrane_rule(
            context=context,
            action=action,
            goal=goal,
            triad="CerebralOutputMembrane"
        )
        
    def _initialize_output_formats(self):
        """Initialize output formats for different types of content."""
        self.output_formats = {
            "structured_report": {
                "template": {
                    "executive_summary": "",
                    "detailed_analysis": "",
                    "recommendations": [],
                    "implementation_steps": [],
                    "conclusion": ""
                },
                "style": "formal",
                "target_audience": "professional"
            },
            "actionable_plan": {
                "template": {
                    "objective": "",
                    "prerequisites": [],
                    "step_by_step_process": [],
                    "resources_required": [],
                    "success_metrics": [],
                    "timeline": ""
                },
                "style": "procedural",
                "target_audience": "implementer"
            },
            "technical_specification": {
                "template": {
                    "requirements": [],
                    "technical_details": {},
                    "implementation_guidelines": [],
                    "testing_criteria": [],
                    "documentation": ""
                },
                "style": "technical",
                "target_audience": "developer"
            },
            "decision_framework": {
                "template": {
                    "decision_criteria": [],
                    "options_analysis": [],
                    "risk_assessment": {},
                    "recommended_decision": "",
                    "rationale": ""
                },
                "style": "analytical",
                "target_audience": "decision_maker"
            }
        }
        
        # Initialize practical application patterns
        self.application_patterns = {
            "step_by_step": {
                "description": "Sequential procedural format",
                "structure": "numbered_steps",
                "clarity_score": 0.9
            },
            "hierarchical": {
                "description": "Hierarchical breakdown format",
                "structure": "nested_categories",
                "clarity_score": 0.8
            },
            "checklist": {
                "description": "Actionable checklist format",
                "structure": "checkbox_items",
                "clarity_score": 0.85
            },
            "flowchart": {
                "description": "Process flow format",
                "structure": "decision_tree",
                "clarity_score": 0.9
            }
        }
        
    async def generate_structured_output(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured, practical output from content.
        
        Args:
            content: Dictionary containing content to be formatted
            
        Returns:
            Dictionary containing structured output with applied formatting
        """
        try:
            content_type = content.get("type", "general")
            raw_content = content.get("data", {})
            target_format = content.get("format", "structured_report")
            
            logger.debug(f"Generating structured output for {content_type}")
            
            # Select appropriate output format
            output_format = self._select_output_format(content_type, target_format)
            
            # Apply left hemisphere processing (structured, applied)
            structured_content = await self._apply_left_hemisphere_processing(raw_content)
            
            # Format content using selected template
            formatted_output = await self._format_content(structured_content, output_format)
            
            # Apply practical application patterns
            practical_application = await self._apply_practical_patterns(formatted_output)
            
            # Validate and refine output
            validation_result = await self._validate_output_quality(formatted_output)
            
            response = {
                "service": self.service_name,
                "hemisphere": self.hemisphere,
                "processing_focus": self.processing_focus,
                "output_format": output_format,
                "structured_content": structured_content,
                "formatted_output": formatted_output,
                "practical_application": practical_application,
                "validation": validation_result,
                "clarity_score": self._calculate_clarity_score(formatted_output),
                "applicability_score": self._calculate_applicability_score(practical_application)
            }
            
            logger.info(f"Generated structured output with format: {target_format}")
            return response
            
        except Exception as e:
            logger.error(f"Error in structured output generation: {e}")
            return {"error": str(e), "service": self.service_name}
            
    def _select_output_format(self, content_type: str, target_format: str) -> Dict[str, Any]:
        """Select appropriate output format based on content type."""
        if target_format in self.output_formats:
            return self.output_formats[target_format]
        
        # Auto-select based on content type
        format_mapping = {
            "analysis": "structured_report",
            "planning": "actionable_plan", 
            "technical": "technical_specification",
            "decision": "decision_framework"
        }
        
        auto_format = format_mapping.get(content_type, "structured_report")
        return self.output_formats[auto_format]
        
    async def _apply_left_hemisphere_processing(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply left hemisphere processing patterns (analytical, structured, applied)."""
        processed_content = {
            "logical_structure": await self._create_logical_structure(content),
            "sequential_order": await self._establish_sequential_order(content),
            "categorical_organization": await self._organize_categorically(content),
            "practical_elements": await self._extract_practical_elements(content)
        }
        
        return processed_content
        
    async def _create_logical_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create logical structure following left-brain patterns."""
        structure = {
            "main_points": [],
            "supporting_details": {},
            "logical_flow": [],
            "hierarchical_organization": {}
        }
        
        # Extract main concepts and organize hierarchically
        if "ideas" in content:
            structure["main_points"] = content["ideas"][:5]  # Top 5 main points
            
        if "analysis" in content:
            structure["supporting_details"] = content["analysis"]
            
        return structure
        
    async def _establish_sequential_order(self, content: Dict[str, Any]) -> List[str]:
        """Establish sequential order for procedural content."""
        sequence = []
        
        # Look for temporal or procedural elements
        if "steps" in content:
            sequence = content["steps"]
        elif "process" in content:
            sequence = content["process"]
        else:
            # Create logical sequence from available content
            sequence = [
                "1. Analyze current situation",
                "2. Define objectives and requirements",
                "3. Develop implementation strategy",
                "4. Execute planned actions",
                "5. Monitor and evaluate results"
            ]
            
        return sequence
        
    async def _organize_categorically(self, content: Dict[str, Any]) -> Dict[str, List]:
        """Organize content into clear categories."""
        categories = {
            "concepts": [],
            "procedures": [],
            "requirements": [],
            "outcomes": [],
            "resources": []
        }
        
        # Categorize content elements
        for key, value in content.items():
            if key in ["ideas", "concepts", "theories"]:
                categories["concepts"].extend(value if isinstance(value, list) else [value])
            elif key in ["steps", "procedures", "process"]:
                categories["procedures"].extend(value if isinstance(value, list) else [value])
            elif key in ["requirements", "needs", "constraints"]:
                categories["requirements"].extend(value if isinstance(value, list) else [value])
                
        return categories
        
    async def _extract_practical_elements(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract elements that can be practically applied."""
        practical_elements = {
            "actionable_items": [],
            "implementation_details": {},
            "resource_requirements": [],
            "success_criteria": []
        }
        
        # Look for actionable content
        for key, value in content.items():
            if "action" in key.lower() or "implement" in key.lower():
                if isinstance(value, list):
                    practical_elements["actionable_items"].extend(value)
                else:
                    practical_elements["actionable_items"].append(str(value))
                    
        return practical_elements
        
    async def _format_content(self, content: Dict[str, Any], output_format: Dict[str, Any]) -> Dict[str, Any]:
        """Format content using the selected output template."""
        template = output_format["template"]
        style = output_format["style"]
        
        formatted_content = {}
        
        # Fill template with structured content
        for section, default_value in template.items():
            if section == "executive_summary":
                formatted_content[section] = self._generate_executive_summary(content)
            elif section == "detailed_analysis":
                formatted_content[section] = self._generate_detailed_analysis(content)
            elif section == "recommendations":
                formatted_content[section] = self._generate_recommendations(content)
            elif section == "implementation_steps":
                formatted_content[section] = self._generate_implementation_steps(content)
            elif section == "objective":
                formatted_content[section] = self._extract_objective(content)
            elif section == "step_by_step_process":
                formatted_content[section] = content.get("sequential_order", [])
            else:
                formatted_content[section] = default_value
                
        # Apply style-specific formatting
        formatted_content["style_applied"] = style
        formatted_content["formatting_timestamp"] = datetime.now().isoformat()
        
        return formatted_content
        
    def _generate_executive_summary(self, content: Dict[str, Any]) -> str:
        """Generate executive summary from structured content."""
        summary_parts = []
        
        if "logical_structure" in content:
            main_points = content["logical_structure"].get("main_points", [])
            if main_points:
                summary_parts.append(f"Key findings include: {', '.join(main_points[:3])}")
                
        if "practical_elements" in content:
            actionable_items = content["practical_elements"].get("actionable_items", [])
            if actionable_items:
                summary_parts.append(f"Recommended actions: {', '.join(actionable_items[:2])}")
                
        return ". ".join(summary_parts) if summary_parts else "Summary of analysis and recommendations."
        
    def _generate_detailed_analysis(self, content: Dict[str, Any]) -> str:
        """Generate detailed analysis section."""
        analysis_parts = []
        
        if "categorical_organization" in content:
            categories = content["categorical_organization"]
            for category, items in categories.items():
                if items:
                    analysis_parts.append(f"{category.title()}: {', '.join(items[:3])}")
                    
        return ". ".join(analysis_parts) if analysis_parts else "Detailed analysis of the situation."
        
    def _generate_recommendations(self, content: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if "practical_elements" in content:
            actionable_items = content["practical_elements"].get("actionable_items", [])
            recommendations.extend(actionable_items[:5])
            
        if not recommendations:
            recommendations = [
                "Implement systematic approach to problem-solving",
                "Establish clear success metrics and monitoring",
                "Ensure adequate resource allocation"
            ]
            
        return recommendations
        
    def _generate_implementation_steps(self, content: Dict[str, Any]) -> List[str]:
        """Generate implementation steps."""
        if "sequential_order" in content:
            return content["sequential_order"]
        else:
            return [
                "Define implementation scope and objectives",
                "Allocate necessary resources and personnel",
                "Execute implementation plan systematically",
                "Monitor progress and adjust as needed",
                "Evaluate results and document lessons learned"
            ]
            
    def _extract_objective(self, content: Dict[str, Any]) -> str:
        """Extract or infer objective from content."""
        if "practical_elements" in content:
            success_criteria = content["practical_elements"].get("success_criteria", [])
            if success_criteria:
                return f"Achieve {success_criteria[0]}"
                
        return "Execute planned activities to achieve desired outcomes"
        
    async def _apply_practical_patterns(self, formatted_content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply practical application patterns for enhanced usability."""
        practical_output = {}
        
        for pattern_name, pattern_info in self.application_patterns.items():
            if pattern_name == "step_by_step":
                practical_output[pattern_name] = await self._apply_step_by_step_pattern(formatted_content)
            elif pattern_name == "checklist":
                practical_output[pattern_name] = await self._apply_checklist_pattern(formatted_content)
            elif pattern_name == "hierarchical":
                practical_output[pattern_name] = await self._apply_hierarchical_pattern(formatted_content)
                
        return practical_output
        
    async def _apply_step_by_step_pattern(self, content: Dict[str, Any]) -> List[str]:
        """Apply step-by-step procedural pattern."""
        steps = []
        
        if "implementation_steps" in content:
            for i, step in enumerate(content["implementation_steps"], 1):
                steps.append(f"Step {i}: {step}")
        elif "step_by_step_process" in content:
            steps = content["step_by_step_process"]
            
        return steps
        
    async def _apply_checklist_pattern(self, content: Dict[str, Any]) -> List[str]:
        """Apply checklist pattern for actionable items."""
        checklist = []
        
        if "recommendations" in content:
            for rec in content["recommendations"]:
                checklist.append(f"☐ {rec}")
                
        return checklist
        
    async def _apply_hierarchical_pattern(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply hierarchical organization pattern."""
        hierarchy = {
            "level_1": [],
            "level_2": {},
            "level_3": {}
        }
        
        # Organize content hierarchically
        for key, value in content.items():
            if isinstance(value, list) and value:
                hierarchy["level_1"].append(key)
                hierarchy["level_2"][key] = value[:3]  # Top 3 items per category
                
        return hierarchy
        
    async def _validate_output_quality(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output quality and completeness."""
        validation = {
            "completeness": self._check_completeness(output),
            "clarity": self._check_clarity(output),
            "practicality": self._check_practicality(output),
            "structure": self._check_structure(output)
        }
        
        validation["overall_quality"] = sum(validation.values()) / len(validation)
        return validation
        
    def _check_completeness(self, output: Dict[str, Any]) -> float:
        """Check if output contains all required sections."""
        required_sections = ["executive_summary", "recommendations", "implementation_steps"]
        present_sections = sum(1 for section in required_sections if section in output and output[section])
        return present_sections / len(required_sections)
        
    def _check_clarity(self, output: Dict[str, Any]) -> float:
        """Check clarity of output content."""
        # Simple heuristic based on content length and structure
        clarity_score = 0.7  # Base score
        
        if "executive_summary" in output and len(output["executive_summary"]) > 20:
            clarity_score += 0.1
            
        if "recommendations" in output and len(output["recommendations"]) > 0:
            clarity_score += 0.1
            
        return min(1.0, clarity_score)
        
    def _check_practicality(self, output: Dict[str, Any]) -> float:
        """Check practicality and actionability of output."""
        practicality_score = 0.6  # Base score
        
        if "implementation_steps" in output and len(output["implementation_steps"]) > 0:
            practicality_score += 0.2
            
        if "recommendations" in output:
            actionable_recommendations = [r for r in output["recommendations"] if any(action_word in r.lower() for action_word in ["implement", "establish", "create", "develop"])]
            if actionable_recommendations:
                practicality_score += 0.2
                
        return min(1.0, practicality_score)
        
    def _check_structure(self, output: Dict[str, Any]) -> float:
        """Check structural organization of output."""
        structure_score = 0.5  # Base score
        
        # Check for logical flow
        if "style_applied" in output:
            structure_score += 0.2
            
        # Check for hierarchical organization
        if len(output.keys()) >= 3:
            structure_score += 0.3
            
        return min(1.0, structure_score)
        
    def _calculate_clarity_score(self, output: Dict[str, Any]) -> float:
        """Calculate clarity score for the output."""
        return self._check_clarity(output)
        
    def _calculate_applicability_score(self, practical_application: Dict[str, Any]) -> float:
        """Calculate applicability score for practical elements."""
        if not practical_application:
            return 0.5
            
        pattern_scores = []
        for pattern_name, pattern_content in practical_application.items():
            if pattern_name in self.application_patterns:
                pattern_score = self.application_patterns[pattern_name]["clarity_score"]
                if pattern_content:  # Non-empty content
                    pattern_scores.append(pattern_score)
                    
        return sum(pattern_scores) / len(pattern_scores) if pattern_scores else 0.5
        
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and output metrics."""
        return {
            "service": self.service_name,
            "triad": self.triad,
            "hemisphere": self.hemisphere,
            "processing_focus": self.processing_focus,
            "status": "active",
            "output_formats": len(self.output_formats),
            "application_patterns": len(self.application_patterns),
            "atomspace_atoms": self.atomspace_manager.get_atom_count()
        }