# System-5 CNS Organization Mapping

## Neurological Component Mapping

This document defines the precise mapping between the neurological System-5 CNS diagram components and the Cognitive Cities microservices architecture. The implementation follows a triad-based structure that mirrors the central nervous system organization.

### Cerebral Triad (Yellow - Neocortex)
The cerebral triad handles higher-order cognitive processing with hemisphere specialization:

- **T (7): thought-service** (Right Hemisphere - Intuitive Idea Potential)
  - Generates creative, intuitive responses using Ghost DSL
  - Focuses on possibility exploration and creative ideation
  - Implements right-brain processing patterns

- **PD (2): processing-director** (Central coordination) 
  - Coordinates processing across cerebral triad using ECAN attention allocation
  - Routes tasks to appropriate hemisphere services
  - Manages cognitive workload distribution

- **P (5): processing-service** (Analytical processing)
  - Performs logical, analytical processing using PLN
  - Handles reasoning and problem-solving tasks
  - Implements systematic cognitive processes

- **O (4): output-service** (Left Hemisphere - Applied Technique Commitment)
  - Delivers structured, applied responses
  - Focuses on practical implementation and technique application
  - Implements left-brain processing patterns

### Somatic Triad (Light Blue - Basal System)
The somatic triad manages voluntary motor functions and behavioral responses:

- **M (1): motor-control-service** (Movement coordination)
  - Executes motor commands through Eva animation system integration
  - Coordinates physical and behavioral actions
  - Manages movement planning and execution

- **S (8): sensory-service** (Input processing)
  - Processes sensory input following Eva's 5-step pipeline
  - Handles vision, audio, and other sensory modalities
  - Performs initial sensory data classification

- **Processing Service**: Behavioral technique implementation
  - Transforms cognitive intentions into behavioral patterns
  - Implements learned behavioral responses
  - Coordinates sensory-motor integration

- **Output Service**: Behavioral response delivery
  - Delivers physical actions and behavioral responses
  - Manages output timing and coordination
  - Handles response execution and feedback

### Autonomic Triad (Turquoise - Limbic System)
The autonomic triad handles background processes with polarity distinctions:

- **M (1): monitoring-service** (Sympathetic - Active monitoring)
  - Performs active system health monitoring with emotive responses
  - Implements sympathetic nervous system activation patterns
  - Handles stress detection and active alerting

- **S (8): state-management** (State persistence)
  - Manages system state persistence using AtomSpace storage
  - Handles memory consolidation and retrieval
  - Maintains emotional and cognitive state continuity

- **PD (2): process-director** (Background processes)
  - Coordinates background cognitive processes
  - Manages housekeeping and maintenance tasks
  - Handles process priority and resource allocation

- **P (5): processing-service** (Emotive processing)
  - Processes emotional and affective information using OpenPsi
  - Handles emotional state transitions and regulation
  - Implements limbic system response patterns

- **T (7): trigger-service** (Parasympathetic - Intuitive responses)
  - Handles automatic responses with intuitive, calming processing
  - Implements parasympathetic nervous system patterns
  - Manages rest, digest, and recovery responses

## Communication Pathways

The inter-triad communication follows the specific arrows shown in the System-5 CNS diagram:

### Cerebral → Somatic
- **action_commands**: High-level motor intentions from cerebral processing
- **behavioral_requests**: Coordinated behavioral pattern requests

### Cerebral → Autonomic  
- **emotional_states**: Cognitive emotional assessments
- **attention_allocation**: ECAN attention distribution signals

### Somatic → Autonomic
- **stress_indicators**: Physical stress and load measurements
- **sensory_overload**: Sensory processing capacity warnings

### Bidirectional Feedback Loops
- All pathways include feedback mechanisms for adaptive control
- State information flows back to inform higher-level processing
- Error signals and completion confirmations maintain system coherence

## Hemisphere and Polarity Distinctions

### Hemisphere Distinctions (Cerebral Triad)
- **Right Hemisphere Services**: Focus on intuitive, creative, holistic processing
  - Pattern recognition and creative synthesis
  - Emotional and contextual understanding
  - Possibility exploration and divergent thinking

- **Left Hemisphere Services**: Focus on analytical, logical, sequential processing
  - Systematic problem solving and logical reasoning  
  - Language processing and symbolic manipulation
  - Convergent thinking and practical application

### Polarity Distinctions (Autonomic Triad)
- **Sympathetic Services**: Active, arousal-oriented processing
  - Fight-or-flight response patterns
  - Active monitoring and alerting
  - Energy mobilization and activation

- **Parasympathetic Services**: Calming, restorative processing
  - Rest-and-digest response patterns
  - Intuitive and reflective processing
  - Energy conservation and restoration

## Implementation Notes

- Each service integrates with existing OpenCog components (AtomSpace, OpenPsi, Ghost, ECAN)
- Services communicate via event-driven architecture using the CognitiveEventBus
- Deployment follows microservices patterns with Kubernetes orchestration
- Testing validates both individual service functionality and inter-triad communication patterns