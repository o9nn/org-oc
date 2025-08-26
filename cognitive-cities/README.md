# Cognitive Cities Architecture

A neurological-inspired cognitive architecture implementing System-5 CNS organization with OpenCog integration.

## Overview

The Cognitive Cities Architecture is a comprehensive implementation of a neurological-inspired cognitive system based on the System-5 Central Nervous System (CNS) organization. It leverages existing OpenCog components including AtomSpace, OpenPsi, Ghost, ECAN, PLN, and MOSES to create a distributed microservices architecture that mirrors brain function.

## Architecture

### System-5 CNS Mapping

The implementation follows precise neurological mappings:

#### Cerebral Triad (Neocortex - Yellow)
Higher-order cognitive processing with hemisphere specialization:
- **Thought Service** (Right Hemisphere): Intuitive idea generation, creative processing
- **Processing Director**: Central coordination using ECAN attention allocation
- **Processing Service**: Analytical reasoning using PLN (Probabilistic Logic Networks)
- **Output Service** (Left Hemisphere): Applied technique commitment, structured output

#### Somatic Triad (Basal System - Light Blue)
Voluntary motor functions and behavioral coordination:
- **Motor Control Service**: Eva animation system integration for movement
- **Sensory Service**: Multi-modal input processing (vision, audio, etc.)
- **Processing Service**: Behavioral technique implementation
- **Output Service**: Behavioral response delivery

#### Autonomic Triad (Limbic System - Turquoise)
Background processes with sympathetic/parasympathetic polarity:
- **Monitoring Service** (Sympathetic): Active system monitoring with emotive responses
- **State Management**: AtomSpace persistence and memory consolidation
- **Process Director**: Background process coordination
- **Processing Service**: Emotive processing using OpenPsi
- **Trigger Service** (Parasympathetic): Automatic, calming responses

#### Integration Hub
Event-driven communication infrastructure:
- **Event Bus**: Inter-triad communication following CNS pathways
- **API Gateway**: RESTful access to all triads with Flask

## Key Features

### Neurological Fidelity
- **Hemisphere Distinctions**: Right hemisphere (intuitive, creative) vs Left hemisphere (analytical, applied)
- **Polarity Distinctions**: Sympathetic (active, arousal) vs Parasympathetic (calming, restorative)
- **Communication Pathways**: Event routing follows System-5 CNS diagram arrows

### OpenCog Integration
- **AtomSpace**: Knowledge representation and graph storage
- **OpenPsi**: Rule-based behavior control and membrane systems
- **Ghost**: Behavior scripting and natural language processing
- **ECAN**: Attention allocation and importance spreading
- **PLN**: Probabilistic reasoning and inference
- **MOSES**: Machine learning and evolution (ready for integration)

### Technical Architecture
- **Microservices**: Distributed, scalable service architecture
- **Event-Driven**: Asynchronous communication via event bus
- **Kubernetes Ready**: Complete deployment configurations
- **RESTful API**: Unified access through API gateway
- **Comprehensive Testing**: Integration and unit tests

## Installation and Deployment

### Prerequisites
- Python 3.8+
- OpenCog (optional, architecture works without it)
- Kubernetes cluster (for production deployment)
- Docker (for containerized deployment)

### Quick Start
```bash
# Clone repository
git clone https://github.com/OpenCoq/opencog-org.git
cd opencog-org/cognitive-cities

# Run basic tests
python tests/test_basic_structure.py

# Start API Gateway (development)
cd integration-hub/api_gateway
python api_gateway.py
```

### Kubernetes Deployment
```bash
# Deploy all triads
cd deployment/kubernetes
kubectl apply -f cerebral-triad-deployment.yaml
kubectl apply -f somatic-triad-deployment.yaml  
kubectl apply -f autonomic-triad-deployment.yaml
kubectl apply -f integration-hub-deployment.yaml

# Verify deployment
kubectl get deployments -l app=cognitive-cities
```

## Usage Examples

### Cerebral Triad Processing
```python
from cognitive_cities.cerebral_triad import ThoughtService, ProcessingService, OutputService

# Intuitive processing (Right Hemisphere)
thought_service = ThoughtService()
ideas = await thought_service.generate_intuitive_ideas({
    "text": "solve climate change creatively",
    "context": {"urgency": "high", "creativity_required": True}
})

# Analytical processing 
processing_service = ProcessingService()
analysis = await processing_service.process_analytical_task({
    "type": "complex_problem",
    "data": {"problem": "resource optimization"},
    "reasoning_type": "deductive"
})

# Structured output (Left Hemisphere)
output_service = OutputService()
plan = await output_service.generate_structured_output({
    "type": "planning",
    "data": analysis,
    "format": "actionable_plan"
})
```

### Inter-Triad Communication
```python
from cognitive_cities.integration_hub.event_bus import CognitiveEventBus, EventPriority

event_bus = CognitiveEventBus()

# Cerebral to Somatic communication
await event_bus.publish_triad_event(
    "cerebral", "somatic", "action_commands",
    {"action": "express_emotion", "emotion": "excitement", "intensity": 0.8},
    EventPriority.HIGH
)

# Somatic to Autonomic feedback
await event_bus.publish_triad_event(
    "somatic", "autonomic", "stress_indicators", 
    {"stress_level": 0.3, "physical_load": 0.5},
    EventPriority.MEDIUM
)
```

### API Gateway Access
```python
import requests

# Get system status
response = requests.get("http://localhost:5000/api/v1/status")
print(response.json())

# Submit cerebral processing request
cerebral_request = {
    "text": "analyze market trends",
    "context": {"domain": "finance", "timeframe": "quarterly"}
}
response = requests.post(
    "http://localhost:5000/api/v1/triad/cerebral/processing",
    json=cerebral_request
)
print(response.json())
```

## Testing

### Unit Tests
```bash
# Basic structure tests (no OpenCog required)
python tests/test_basic_structure.py

# Integration tests (requires OpenCog)
python tests/test_triad_integration.py
```

### Manual Testing
```bash
# Test API Gateway
curl http://localhost:5000/health

# Test triad communication
curl -X POST http://localhost:5000/api/v1/communication/publish \
  -H "Content-Type: application/json" \
  -d '{"source_triad": "cerebral", "target_triad": "somatic", "event_type": "action_commands", "data": {"test": true}}'
```

## Development

### Project Structure
```
cognitive-cities/
├── cognitive-core/           # Shared libraries
│   └── shared_libraries/
│       ├── atomspace_manager.py
│       └── membrane_controller.py
├── cerebral-triad/          # Cerebral services
│   ├── thought_service.py
│   ├── processing_director.py
│   ├── processing_service.py
│   └── output_service.py
├── somatic-triad/           # Somatic services
│   └── motor_control_service.py
├── autonomic-triad/         # Autonomic services (to be completed)
├── integration-hub/         # Communication infrastructure
│   ├── event_bus/
│   └── api_gateway/
├── deployment/              # Kubernetes configs
│   └── kubernetes/
└── tests/                   # Test suites
```

### Contributing
1. Follow the neurological System-5 CNS mapping precisely
2. Maintain hemisphere and polarity distinctions
3. Integrate with existing OpenCog components
4. Add comprehensive tests for new services
5. Update documentation and deployment configs

## Documentation

- **SYSTEM5_CNS_MAPPING.md**: Detailed neurological component mapping
- **deployment/kubernetes/README.md**: Kubernetes deployment guide
- **tests/**: Integration and unit test documentation

## License

This project is part of the OpenCog framework and follows the same licensing terms.

## Contributors

- OpenCog Cognitive Cities Development Team
- Based on System-5 CNS neurological research

## Status

**Current Implementation Status:**
- ✅ System-5 CNS Mapping Documentation
- ✅ Cognitive Core Shared Libraries (AtomSpace, OpenPsi)
- ✅ Complete Cerebral Triad (4 services)
- ✅ Motor Control Service (Somatic Triad)
- ✅ Integration Hub (Event Bus + API Gateway)
- ✅ Kubernetes Deployment Configurations
- ✅ Comprehensive Test Suite
- 🔄 Remaining Somatic and Autonomic services (in progress)

The architecture provides a solid foundation for neurological-inspired AI systems with OpenCog integration and is ready for deployment and extension.