# Cognitive Cities Architecture - Kubernetes Deployment Guide

This directory contains Kubernetes deployment configurations for the complete Cognitive Cities Architecture following the System-5 CNS mapping.

## Architecture Overview

The deployment consists of three main triads plus an integration hub:

### 1. Cerebral Triad (cognitive-processing)
- **Thought Service** (Right Hemisphere - Intuitive)
- **Processing Director** (Central Coordination with ECAN)
- **Processing Service** (Analytical Processing with PLN)
- **Output Service** (Left Hemisphere - Applied Technique)

### 2. Somatic Triad (behavioral-control)
- **Motor Control Service** (Eva Integration)
- **Sensory Service** (Input Processing)
- **Processing Service** (Behavioral Techniques)
- **Output Service** (Behavioral Responses)

### 3. Autonomic Triad (background-regulation)
- **Monitoring Service** (Sympathetic - Active)
- **State Management** (Persistence)
- **Process Director** (Background Processes)
- **Processing Service** (Emotive Processing)
- **Trigger Service** (Parasympathetic - Automatic)

### 4. Integration Hub (communication-infrastructure)
- **API Gateway** (RESTful Access)
- **Event Bus** (Inter-triad Communication)

## Deployment Instructions

### Prerequisites

1. Kubernetes cluster (1.20+)
2. kubectl configured
3. Container registry access
4. Persistent storage (for state management)

### Quick Deployment

```bash
# Deploy all triads and integration hub
kubectl apply -f cerebral-triad-deployment.yaml
kubectl apply -f somatic-triad-deployment.yaml
kubectl apply -f autonomic-triad-deployment.yaml
kubectl apply -f integration-hub-deployment.yaml

# Verify deployments
kubectl get deployments -l app=cognitive-cities
kubectl get services -l app=cognitive-cities
```

### Individual Triad Deployment

```bash
# Deploy cerebral triad only
kubectl apply -f cerebral-triad-deployment.yaml

# Deploy somatic triad only
kubectl apply -f somatic-triad-deployment.yaml

# Deploy autonomic triad only
kubectl apply -f autonomic-triad-deployment.yaml

# Deploy integration hub
kubectl apply -f integration-hub-deployment.yaml
```

## Service Endpoints

### External Access
- **API Gateway**: `http://[LoadBalancer-IP]/api/v1/`
- **Health Check**: `http://[LoadBalancer-IP]/health`
- **System Status**: `http://[LoadBalancer-IP]/api/v1/status`

### Internal Services
- **Cerebral Triad**: `cerebral-triad-service:8001-8004`
- **Somatic Triad**: `somatic-triad-service:8011-8014`
- **Autonomic Triad**: `autonomic-triad-service:8021-8025`
- **Event Bus**: `integration-hub-service:6000`

## API Endpoints

### Cerebral Triad
- `POST /api/v1/triad/cerebral/thought` - Intuitive processing
- `POST /api/v1/triad/cerebral/processing` - Analytical reasoning
- `POST /api/v1/triad/cerebral/output` - Structured output
- `POST /api/v1/triad/cerebral/coordinate` - Coordination

### Somatic Triad
- `POST /api/v1/triad/somatic/motor` - Motor control
- `POST /api/v1/triad/somatic/sensory` - Sensory processing

### Autonomic Triad
- `POST /api/v1/triad/autonomic/monitoring` - System monitoring
- `POST /api/v1/triad/autonomic/state` - State management

### Communication
- `POST /api/v1/communication/publish` - Publish inter-triad events
- `GET /api/v1/communication/pathways` - Get CNS pathways
- `GET /api/v1/communication/history` - Communication history

## Configuration

### Environment Variables

Each service supports configuration through environment variables:

#### Cerebral Triad
- `HEMISPHERE`: right, left, or neutral
- `PROCESSING_TYPE`: intuitive, analytical, applied
- `ECAN_ENABLED`: true/false (Processing Director)
- `ATTENTION_BUDGET`: 1000 (Processing Director)

#### Somatic Triad
- `EVA_INTEGRATION`: true/false (Motor Control)
- `VISION_ENABLED`: true/false (Sensory)
- `AUDIO_ENABLED`: true/false (Sensory)

#### Autonomic Triad
- `POLARITY`: sympathetic or parasympathetic
- `MONITORING_ACTIVE`: true/false
- `STATE_PERSISTENCE`: true/false

#### Integration Hub
- `API_HOST`: 0.0.0.0
- `API_PORT`: 5000
- `EVENT_BUS_PORT`: 6000

### Resource Requirements

#### Minimum Resources
- **Cerebral Triad**: 1.5 CPU, 1.5Gi RAM
- **Somatic Triad**: 1.5 CPU, 1.5Gi RAM
- **Autonomic Triad**: 2 CPU, 2Gi RAM
- **Integration Hub**: 0.75 CPU, 768Mi RAM

#### Recommended Resources
- **Total**: 6 CPU, 6Gi RAM for full deployment
- **Storage**: 10Gi persistent volume for state management

## Monitoring and Health Checks

### Health Endpoints
Each service provides:
- `/health` - Liveness probe
- `/ready` - Readiness probe
- `/metrics` - Prometheus metrics (if enabled)

### Monitoring
```bash
# Check pod status
kubectl get pods -l app=cognitive-cities

# View logs
kubectl logs -l triad=cerebral
kubectl logs -l component=integration-hub

# Port forward for local access
kubectl port-forward service/cognitive-cities-api 8080:80
```

## Scaling

### Horizontal Scaling
```bash
# Scale cerebral triad
kubectl scale deployment cerebral-triad --replicas=5

# Scale integration hub
kubectl scale deployment integration-hub --replicas=3
```

### Vertical Scaling
Update resource limits in deployment files and apply:
```bash
kubectl apply -f cerebral-triad-deployment.yaml
```

## Troubleshooting

### Common Issues

1. **Service Discovery**: Ensure all services are running and registered
2. **Event Bus Connection**: Check event bus service is accessible
3. **AtomSpace Integration**: Verify OpenCog dependencies
4. **Resource Limits**: Monitor CPU and memory usage

### Debug Commands
```bash
# Check service endpoints
kubectl get endpoints

# Test internal connectivity
kubectl exec -it [pod-name] -- curl http://cerebral-triad-service:8001/health

# View detailed service info
kubectl describe service cognitive-cities-api
```

## Security Considerations

1. **Network Policies**: Implement network segmentation
2. **RBAC**: Configure role-based access control
3. **TLS**: Enable TLS for external endpoints
4. **Secrets**: Use Kubernetes secrets for sensitive data

## Backup and Recovery

1. **State Management**: Backup persistent volumes
2. **Configuration**: Version control deployment files
3. **AtomSpace**: Implement AtomSpace persistence backup
4. **Event History**: Configure event bus data retention