"""
Cognitive API Gateway - Integration Hub

RESTful API gateway for the Cognitive Cities Architecture that provides
unified access to all triads and integrates with AtomSpace.
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import asyncio
import logging
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the cognitive-cities directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from cognitive_core.shared_libraries.atomspace_manager import CognitiveAtomSpaceManager
from integration_hub.event_bus.event_bus import CognitiveEventBus, EventPriority

logger = logging.getLogger(__name__)


class CognitiveAPIGateway:
    """
    API Gateway for Cognitive Cities Architecture.
    
    Provides RESTful API access to all triads with AtomSpace integration
    and event-driven communication coordination.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        """Initialize the API Gateway."""
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web client access
        
        self.host = host
        self.port = port
        
        # Initialize core components
        self.atomspace_manager = CognitiveAtomSpaceManager()
        self.event_bus = CognitiveEventBus()
        
        # Service registry for dynamic service discovery
        self.service_registry = {
            "cerebral_triad": {
                "thought-service": None,
                "processing-director": None,
                "processing-service": None,
                "output-service": None
            },
            "somatic_triad": {
                "motor-control-service": None,
                "sensory-service": None,
                "processing-service": None,
                "output-service": None
            },
            "autonomic_triad": {
                "monitoring-service": None,
                "state-management": None,
                "process-director": None,
                "processing-service": None,
                "trigger-service": None
            }
        }
        
        # API metrics
        self.api_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "triad_requests": {
                "cerebral": 0,
                "somatic": 0,
                "autonomic": 0
            }
        }
        
        # Setup routes
        self._setup_routes()
        self._setup_error_handlers()
        
        logger.info(f"CognitiveAPIGateway initialized on {host}:{port}")
        
    def _setup_routes(self):
        """Setup API routes for all triads and services."""
        
        # Health check and status endpoints
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """API health check endpoint."""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "atomspace_atoms": self.atomspace_manager.get_atom_count(),
                "event_bus_stats": self.event_bus.get_statistics()
            })
            
        @self.app.route('/api/v1/status', methods=['GET'])
        def get_system_status():
            """Get overall system status."""
            return jsonify({
                "system": "cognitive_cities",
                "version": "1.0.0",
                "status": "active",
                "triads": self._get_triad_status(),
                "atomspace": {
                    "total_atoms": self.atomspace_manager.get_atom_count(),
                    "status": "active"
                },
                "event_bus": self.event_bus.get_statistics(),
                "api_metrics": self.api_metrics
            })
            
        # AtomSpace endpoints
        @self.app.route('/api/v1/atomspace/atoms', methods=['GET'])
        def get_atomspace_info():
            """Get AtomSpace information."""
            return jsonify({
                "total_atoms": self.atomspace_manager.get_atom_count(),
                "triads": {
                    "cerebral": len(self.atomspace_manager.get_triad_components("CerebralTriad")),
                    "somatic": len(self.atomspace_manager.get_triad_components("SomaticTriad")),
                    "autonomic": len(self.atomspace_manager.get_triad_components("AutonomicTriad"))
                }
            })
            
        @self.app.route('/api/v1/atomspace/triads/<triad_name>/components', methods=['GET'])
        def get_triad_components(triad_name):
            """Get components of a specific triad."""
            try:
                triad_name_formatted = f"{triad_name.title()}Triad"
                components = self.atomspace_manager.get_triad_components(triad_name_formatted)
                
                return jsonify({
                    "triad": triad_name,
                    "components": [str(comp) for comp in components],
                    "count": len(components)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 400
                
        # Cerebral Triad endpoints
        @self.app.route('/api/v1/triad/cerebral/thought', methods=['POST'])
        def cerebral_thought_processing():
            """Process intuitive thought requests."""
            return self._handle_triad_request("cerebral", "thought-service", request.json)
            
        @self.app.route('/api/v1/triad/cerebral/processing', methods=['POST'])
        def cerebral_analytical_processing():
            """Process analytical reasoning requests."""
            return self._handle_triad_request("cerebral", "processing-service", request.json)
            
        @self.app.route('/api/v1/triad/cerebral/output', methods=['POST'])
        def cerebral_output_generation():
            """Generate structured output."""
            return self._handle_triad_request("cerebral", "output-service", request.json)
            
        @self.app.route('/api/v1/triad/cerebral/coordinate', methods=['POST'])
        def cerebral_coordination():
            """Coordinate cerebral triad processing."""
            return self._handle_triad_request("cerebral", "processing-director", request.json)
            
        # Somatic Triad endpoints
        @self.app.route('/api/v1/triad/somatic/motor', methods=['POST'])
        def somatic_motor_control():
            """Execute motor control commands."""
            return self._handle_triad_request("somatic", "motor-control-service", request.json)
            
        @self.app.route('/api/v1/triad/somatic/sensory', methods=['POST'])
        def somatic_sensory_processing():
            """Process sensory input."""
            return self._handle_triad_request("somatic", "sensory-service", request.json)
            
        # Autonomic Triad endpoints
        @self.app.route('/api/v1/triad/autonomic/monitoring', methods=['POST'])
        def autonomic_monitoring():
            """Handle autonomic monitoring requests."""
            return self._handle_triad_request("autonomic", "monitoring-service", request.json)
            
        @self.app.route('/api/v1/triad/autonomic/state', methods=['POST'])
        def autonomic_state_management():
            """Handle state management requests."""
            return self._handle_triad_request("autonomic", "state-management", request.json)
            
        # Inter-triad communication endpoints
        @self.app.route('/api/v1/communication/publish', methods=['POST'])
        def publish_triad_event():
            """Publish event between triads."""
            try:
                data = request.json
                source_triad = data.get("source_triad")
                target_triad = data.get("target_triad")
                event_type = data.get("event_type")
                event_data = data.get("data", {})
                priority = data.get("priority", "medium")
                
                # Convert priority string to enum
                priority_enum = getattr(EventPriority, priority.upper(), EventPriority.MEDIUM)
                
                # Publish event
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(
                    self.event_bus.publish_triad_event(
                        source_triad, target_triad, event_type, event_data, priority_enum
                    )
                )
                loop.close()
                
                if success:
                    return jsonify({
                        "status": "published",
                        "source_triad": source_triad,
                        "target_triad": target_triad,
                        "event_type": event_type
                    })
                else:
                    return jsonify({"error": "Failed to publish event"}), 400
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
                
        @self.app.route('/api/v1/communication/pathways', methods=['GET'])
        def get_communication_pathways():
            """Get available communication pathways."""
            pathways = {}
            for pathway_name, pathway_info in self.event_bus.triad_connections.items():
                pathways[pathway_name] = {
                    "allowed_events": pathway_info["allowed_events"],
                    "pathway_type": pathway_info["pathway_type"],
                    "priority_weight": pathway_info["priority_weight"]
                }
                
            return jsonify({"pathways": pathways})
            
        @self.app.route('/api/v1/communication/history', methods=['GET'])
        def get_communication_history():
            """Get recent communication history."""
            limit = request.args.get('limit', 50, type=int)
            history = self.event_bus.get_event_history(limit)
            
            return jsonify({
                "history": history,
                "total_events": len(history)
            })
            
        # Service management endpoints
        @self.app.route('/api/v1/services/register', methods=['POST'])
        def register_service():
            """Register a service instance."""
            try:
                data = request.json
                triad = data.get("triad")
                service_name = data.get("service_name")
                service_instance = data.get("service_instance")
                
                if triad in self.service_registry and service_name in self.service_registry[triad]:
                    self.service_registry[triad][service_name] = service_instance
                    return jsonify({"status": "registered", "triad": triad, "service": service_name})
                else:
                    return jsonify({"error": "Invalid triad or service name"}), 400
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
                
        @self.app.route('/api/v1/services/status', methods=['GET'])
        def get_services_status():
            """Get status of all registered services."""
            services_status = {}
            
            for triad_name, services in self.service_registry.items():
                services_status[triad_name] = {}
                for service_name, service_instance in services.items():
                    if service_instance and hasattr(service_instance, 'get_service_status'):
                        try:
                            status = service_instance.get_service_status()
                            services_status[triad_name][service_name] = status
                        except Exception as e:
                            services_status[triad_name][service_name] = {"error": str(e)}
                    else:
                        services_status[triad_name][service_name] = {"status": "not_registered"}
                        
            return jsonify({"services": services_status})
            
    def _setup_error_handlers(self):
        """Setup error handlers for the API."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Endpoint not found"}), 404
            
        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({"error": "Bad request"}), 400
            
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({"error": "Internal server error"}), 500
            
        @self.app.before_request
        def before_request():
            """Execute before each request."""
            self.api_metrics["total_requests"] += 1
            g.start_time = datetime.now()
            
        @self.app.after_request
        def after_request(response):
            """Execute after each request."""
            if response.status_code < 400:
                self.api_metrics["successful_requests"] += 1
            else:
                self.api_metrics["failed_requests"] += 1
                
            # Track triad-specific requests
            if request.endpoint:
                if "cerebral" in request.endpoint:
                    self.api_metrics["triad_requests"]["cerebral"] += 1
                elif "somatic" in request.endpoint:
                    self.api_metrics["triad_requests"]["somatic"] += 1
                elif "autonomic" in request.endpoint:
                    self.api_metrics["triad_requests"]["autonomic"] += 1
                    
            return response
            
    def _handle_triad_request(self, triad: str, service_name: str, request_data: Dict[str, Any]) -> tuple:
        """Handle requests to triad services."""
        try:
            # Check if service is registered
            service_key = f"{triad}_triad"
            if service_key not in self.service_registry or service_name not in self.service_registry[service_key]:
                return jsonify({"error": f"Service {service_name} not found in {triad} triad"}), 404
                
            service_instance = self.service_registry[service_key][service_name]
            if not service_instance:
                return jsonify({"error": f"Service {service_name} not registered"}), 503
                
            # For now, return a placeholder response since services aren't fully connected
            response = {
                "triad": triad,
                "service": service_name,
                "status": "request_received",
                "request_data": request_data,
                "timestamp": datetime.now().isoformat(),
                "note": "Service integration in progress"
            }
            
            # Publish event about the request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self.event_bus.publish(
                    f"{triad}_triad_request",
                    {
                        "service": service_name,
                        "request_data": request_data
                    },
                    EventPriority.MEDIUM
                )
            )
            loop.close()
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error handling {triad} triad request: {e}")
            return jsonify({"error": str(e)}), 500
            
    def _get_triad_status(self) -> Dict[str, Any]:
        """Get status of all triads."""
        triad_status = {}
        
        for triad_name, services in self.service_registry.items():
            active_services = sum(1 for service in services.values() if service is not None)
            total_services = len(services)
            
            triad_status[triad_name] = {
                "active_services": active_services,
                "total_services": total_services,
                "status": "active" if active_services > 0 else "inactive"
            }
            
        return triad_status
        
    def register_service_instance(self, triad: str, service_name: str, service_instance: Any) -> bool:
        """Register a service instance programmatically."""
        try:
            service_key = f"{triad}_triad"
            if service_key in self.service_registry and service_name in self.service_registry[service_key]:
                self.service_registry[service_key][service_name] = service_instance
                logger.info(f"Registered {service_name} in {triad} triad")
                return True
            else:
                logger.error(f"Invalid triad ({triad}) or service name ({service_name})")
                return False
        except Exception as e:
            logger.error(f"Error registering service: {e}")
            return False
            
    def get_event_bus(self) -> CognitiveEventBus:
        """Get the event bus instance."""
        return self.event_bus
        
    def get_atomspace_manager(self) -> CognitiveAtomSpaceManager:
        """Get the AtomSpace manager instance."""
        return self.atomspace_manager
        
    def run(self, debug: bool = False) -> None:
        """Run the API Gateway server."""
        logger.info(f"Starting CognitiveAPIGateway on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)
        
    async def shutdown(self) -> None:
        """Shutdown the API Gateway gracefully."""
        logger.info("Shutting down CognitiveAPIGateway...")
        await self.event_bus.shutdown()
        logger.info("CognitiveAPIGateway shutdown complete")


def create_api_gateway(host: str = "0.0.0.0", port: int = 5000) -> CognitiveAPIGateway:
    """Factory function to create API Gateway instance."""
    return CognitiveAPIGateway(host, port)


if __name__ == "__main__":
    # Run the API Gateway if executed directly
    gateway = create_api_gateway()
    gateway.run(debug=True)