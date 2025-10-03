"""
Cognitive Cities Architecture

A neurological-inspired cognitive architecture based on System-5 CNS organization
that integrates with OpenCog frameworks (AtomSpace, OpenPsi, Ghost, ECAN, PLN, MOSES).

## Architecture Overview

The Cognitive Cities Architecture implements a triad-based structure mirroring
the central nervous system:

### Cerebral Triad (Neocortex)
Higher-order cognitive processing with hemisphere specialization:
- Thought Service (Right Hemisphere - Intuitive)
- Processing Director (Central Coordination with ECAN)  
- Processing Service (Analytical with PLN)
- Output Service (Left Hemisphere - Applied Technique)

### Somatic Triad (Basal System)
Voluntary motor functions and behavioral responses:
- Motor Control Service (Eva Integration)
- Sensory Service (Input Processing)
- Processing Service (Behavioral Techniques)
- Output Service (Behavioral Responses)

### Autonomic Triad (Limbic System) 
Background processes with polarity distinctions:
- Monitoring Service (Sympathetic - Active)
- State Management (Persistence)
- Process Director (Background Processes)
- Processing Service (Emotive with OpenPsi)
- Trigger Service (Parasympathetic - Automatic)

### Integration Hub
Event-driven communication infrastructure:
- Event Bus (Inter-triad Communication)
- API Gateway (RESTful Access)

## Key Features

- **System-5 CNS Mapping**: Precise neurological component mapping
- **Hemisphere Distinctions**: Right (intuitive) vs Left (applied technique)
- **Polarity Distinctions**: Sympathetic (active) vs Parasympathetic (calming)
- **OpenCog Integration**: AtomSpace, OpenPsi, Ghost, ECAN, PLN, MOSES
- **Event-Driven Architecture**: Following CNS communication pathways
- **Microservices Design**: Scalable, distributed deployment
- **Kubernetes Ready**: Complete deployment configurations

## Usage

```python
from cognitive_cities.cerebral_triad import ThoughtService, ProcessingDirector
from cognitive_cities.integration_hub.event_bus import CognitiveEventBus
from cognitive_cities.integration_hub.api_gateway import CognitiveAPIGateway

# Initialize services
thought_service = ThoughtService()
event_bus = CognitiveEventBus()
api_gateway = CognitiveAPIGateway()

# Process intuitive ideas
ideas = await thought_service.generate_intuitive_ideas({
    "text": "creative problem solving",
    "context": {"creativity_required": True}
})

# Publish inter-triad events
await event_bus.publish_triad_event(
    "cerebral", "somatic", "action_commands", 
    {"command": "express_emotion", "emotion": "joy"}
)
```

## Installation

See deployment/kubernetes/ for Kubernetes deployment instructions.

## Testing

```bash
cd cognitive-cities
python tests/test_basic_structure.py
python tests/test_triad_integration.py
```
"""

from . import cognitive_core
from . import cerebral_triad
from . import somatic_triad
from . import autonomic_triad
from . import integration_hub

__version__ = "1.0.0"
__author__ = "OpenCog Cognitive Cities Team"
__email__ = "info@opencog.org"

__all__ = [
    'cognitive_core',
    'cerebral_triad', 
    'somatic_triad',
    'autonomic_triad',
    'integration_hub'
]