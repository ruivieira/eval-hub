## **Proposal 2: Thin API Router/Orchestration Layer**

### High-Level Summary

The Thin API Router proposal creates a custom-built microservice focused solely on evaluation orchestration with minimal dependencies and maximum flexibility. This approach prioritizes lightweight operation and complete control over the orchestration logic. It offers optimal performance and customization at the cost of increased development effort.  
The Router/Orch layer **will not** provide any evaluation/benchmark runtime capabilities, its sole purpose is to translate requests into backend executions and storage.

**Key Benefits**: Minimal footprint, maximum flexibility, full API/design control  
**Key Challenges**: Higher development effort, manual ecosystem integration, feature scope responsibility

### Architecture Overview

This solution implements a dedicated Kubernetes-native control plane for evaluation that orchestrates underlying frameworks directly, providing lifecycle management and extensibility. The platform focuses on plug-in extensibility and provides out-of-the-box support for the currently and future available evaluation backends.

#### Core Components

##### 1\. Core API Service

- **Lightweight Router**: FastAPI-based service with minimal dependencies  
- **Request Processor**: Schema validation and backend capability matching  
- **Communication Layer**: Protocol adapters for different backend types (HTTP, gRPC, message queue)

##### 2\. Kubernetes-Native Control Plane

- **Operator-Based Management**: Dedicated controller, deployed as Kubernetes Operator managed by TrustyAI team  
- **Unified Orchestration Layer**: Custom-built platform for managing multiple evaluation frameworks  
- **Framework Discovery Service**: Lists all available evaluation capabilities

##### 3\. Framework Management & Extensibility

- **Built-in Framework Support**: Out-of-the-box support for LMEval, RAGAS, Garak and GuideLLM  
- **Bring Your Own Framework (BYOF)**: Container images with standardized interfaces  
- **Framework Registry**: Centralized catalog of available evaluation frameworks

##### 4\. Enterprise MLOps Integration

- **MLOps Traceability**: Full evaluation traces persisted in OCI-backed storage  
- **Model Governance**: Automatic surfacing of evaluation metrics in Model Registry UI  
- **Industry-Specific Collections**: Curated evaluation collections for healthcare, legal, finance domains

### Comprehensive API Analysis

The eval-hub implements a comprehensive REST API with versioned endpoints (`/api/v1/`) providing orchestration capabilities across multiple evaluation backends. The API follows OpenAPI 3.0 specification and supports both synchronous and asynchronous execution patterns.

#### API Base Configuration
- **Base URL**: `http://localhost:8000/api/v1/`
- **API Version**: v1
- **Content-Type**: `application/json`
- **Authentication**: Bearer token (configurable)
- **OpenAPI Spec**: Available at `/docs` (Swagger UI) and `/openapi.json`

---

## Core API Endpoints

### 🏥 Health & Status Endpoints

#### **GET** `/health` - Health Check
**Purpose**: Service health monitoring and dependency status
**Response Model**: `HealthResponse`

```bash
curl -X GET "{{baseUrl}}/health"
```

**Response Example**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "components": {
    "mlflow": {
      "status": "healthy",
      "tracking_uri": "http://mlflow:5000"
    }
  },
  "uptime_seconds": 3600.5,
  "active_evaluations": 3
}
```

**Commentary**: Provides comprehensive health status including external dependencies (MLFlow), current system load (active evaluations), and service uptime. Essential for monitoring and observability.

---

### 🔄 Evaluation Management Endpoints

#### **POST** `/evaluations` - Create Evaluation Request
**Purpose**: Submit evaluation jobs for execution across multiple backends
**Response Model**: `EvaluationResponse`
**Status Code**: `202 ACCEPTED` (async) | `200 OK` (sync)

```bash
curl -X POST "{{baseUrl}}/evaluations?async_mode=true" \
-H "Content-Type: application/json" \
-d '{
  "evaluations": [
    {
      "benchmark": {
        "benchmark_id": "arc_easy",
        "provider_id": "lm_evaluation_harness"
      },
      "backend": {
        "backend_type": "llama_stack",
        "model_id": "meta-llama/llama-3.1-8b"
      }
    }
  ],
  "experiment_name": "prod-model-validation",
  "tags": {
    "environment": "production",
    "model_version": "v2.1"
  }
}'
```

**Response Example**:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "evaluations": [
    {
      "evaluation_id": "eval_001",
      "benchmark": {
        "benchmark_id": "arc_easy",
        "provider_id": "lm_evaluation_harness"
      },
      "status": "pending",
      "backend": {
        "backend_type": "llama_stack",
        "model_id": "meta-llama/llama-3.1-8b"
      },
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "experiment_id": "exp_12345",
  "experiment_url": "http://mlflow:5000/experiments/12345",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Commentary**: Supports both single and batch evaluation requests. Async mode (default) returns immediately with tracking IDs, while sync mode blocks until completion. MLFlow integration provides experiment tracking and result persistence.

#### **POST** `/evaluations/single` - Single Benchmark Evaluation
**Purpose**: Simplified endpoint for single benchmark evaluations
**Response Model**: `EvaluationResponse`

```bash
curl -X POST "{{baseUrl}}/evaluations/single" \
-H "Content-Type: application/json" \
-d '{
  "benchmark_id": "arc_easy",
  "provider_id": "lm_evaluation_harness",
  "model_id": "meta-llama/llama-3.1-8b",
  "backend_type": "llama_stack"
}'
```

#### **GET** `/evaluations/{evaluation_id}/status` - Check Evaluation Status
**Purpose**: Monitor evaluation progress and retrieve current status

```bash
curl -X GET "{{baseUrl}}/evaluations/550e8400-e29b-41d4-a716-446655440000/status"
```

**Response Example**:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 0.65,
  "evaluations": [
    {
      "evaluation_id": "eval_001",
      "status": "running",
      "progress": 0.65,
      "started_at": "2025-01-15T10:31:00Z",
      "estimated_completion": "2025-01-15T10:45:00Z"
    }
  ],
  "updated_at": "2025-01-15T10:40:00Z"
}
```

#### **GET** `/evaluations` - List Active Evaluations
**Purpose**: Retrieve all active evaluations with filtering capabilities

```bash
curl -X GET "{{baseUrl}}/evaluations?status=running&limit=10"
```

#### **DELETE** `/evaluations/{evaluation_id}` - Cancel Evaluation
**Purpose**: Cancel running evaluations and cleanup resources

```bash
curl -X DELETE "{{baseUrl}}/evaluations/550e8400-e29b-41d4-a716-446655440000"
```

#### **GET** `/evaluations/{evaluation_id}/summary` - Get Evaluation Results
**Purpose**: Retrieve comprehensive evaluation results and metrics

---

### 🏢 Provider Management Endpoints

#### **GET** `/providers` - List All Providers
**Purpose**: Discover available evaluation providers and their capabilities
**Response Model**: `ListProvidersResponse`

```bash
curl -X GET "{{baseUrl}}/providers"
```

**Response Example**:
```json
{
  "providers": [
    {
      "provider_id": "lm_evaluation_harness",
      "provider_name": "LM Evaluation Harness",
      "description": "Comprehensive evaluation framework for language models with 167 benchmarks",
      "provider_type": "builtin",
      "benchmark_count": 167,
      "categories": ["reasoning", "math", "science", "knowledge", "language_modeling"]
    },
    {
      "provider_id": "ragas",
      "provider_name": "RAGAS",
      "description": "Retrieval Augmented Generation Assessment framework",
      "provider_type": "builtin",
      "benchmark_count": 8,
      "categories": ["retrieval", "generation", "rag"]
    },
    {
      "provider_id": "garak",
      "provider_name": "Garak",
      "description": "LLM vulnerability scanner for security assessment",
      "provider_type": "builtin",
      "benchmark_count": 15,
      "categories": ["safety", "security", "robustness"]
    }
  ],
  "total_count": 3
}
```

**Commentary**: Provides provider discovery with capability summary. Each provider exposes different benchmark categories - LM Eval Harness for comprehensive model evaluation, RAGAS for RAG-specific assessment, and Garak for security scanning.

#### **GET** `/providers/{provider_id}` - Get Provider Details
**Purpose**: Retrieve detailed provider information including all benchmarks

```bash
curl -X GET "{{baseUrl}}/providers/lm_evaluation_harness"
```

#### **POST** `/providers/reload` - Reload Provider Configuration
**Purpose**: Hot-reload provider configuration without service restart

---

### 📊 Benchmark Management Endpoints

#### **GET** `/benchmarks` - List All Benchmarks
**Purpose**: Discover available benchmarks across all providers with filtering
**Response Model**: `ListBenchmarksResponse`

```bash
# List all benchmarks
curl -X GET "{{baseUrl}}/benchmarks"

# Filter by provider
curl -X GET "{{baseUrl}}/benchmarks?provider_id=lm_evaluation_harness"

# Filter by category
curl -X GET "{{baseUrl}}/benchmarks?category=reasoning"

# Filter by tags
curl -X GET "{{baseUrl}}/benchmarks?tags=math,science"
```

**Response Example**:
```json
{
  "benchmarks": [
    {
      "benchmark_id": "lm_evaluation_harness::arc_easy",
      "provider_id": "lm_evaluation_harness",
      "name": "ARC Easy",
      "description": "AI2 Reasoning Challenge (Easy) - Grade school science questions",
      "category": "reasoning",
      "metrics": ["accuracy", "acc_norm"],
      "num_few_shot": 0,
      "dataset_size": 2376,
      "tags": ["reasoning", "science", "lm_eval"]
    },
    {
      "benchmark_id": "ragas::faithfulness",
      "provider_id": "ragas",
      "name": "Faithfulness",
      "description": "Measures factual consistency of generated answer against given context",
      "category": "retrieval",
      "metrics": ["faithfulness_score"],
      "num_few_shot": null,
      "dataset_size": null,
      "tags": ["rag", "faithfulness", "retrieval"]
    }
  ],
  "total_count": 190,
  "providers_included": ["lm_evaluation_harness", "ragas", "garak"]
}
```

**Commentary**: Unified benchmark catalog across providers. Benchmark IDs follow `provider::benchmark` format for global uniqueness. Supports powerful filtering by provider, category, and tags for targeted discovery.

#### **GET** `/providers/{provider_id}/benchmarks` - Provider-Specific Benchmarks
**Purpose**: Get benchmarks for a specific provider

```bash
curl -X GET "{{baseUrl}}/providers/lm_evaluation_harness/benchmarks"
```

#### **GET** `/benchmarks/{benchmark_id}` - Get Benchmark Details
**Purpose**: Detailed benchmark specification including metrics and requirements

```bash
curl -X GET "{{baseUrl}}/benchmarks/lm_evaluation_harness::arc_easy"
```

---

### 📚 Collection Management Endpoints

#### **GET** `/collections` - List Benchmark Collections
**Purpose**: Discover curated benchmark collections for specific domains
**Response Model**: `ListCollectionsResponse`

```bash
curl -X GET "{{baseUrl}}/collections"
```

**Response Example**:
```json
{
  "collections": [
    {
      "collection_id": "healthcare_safety_v1",
      "name": "Healthcare Safety Assessment v1",
      "description": "Comprehensive safety evaluation for healthcare LLM applications",
      "benchmark_count": 12,
      "providers": ["lm_evaluation_harness", "garak"],
      "categories": ["safety", "medical", "reasoning"],
      "created_at": "2024-12-01T00:00:00Z"
    },
    {
      "collection_id": "general_llm_eval_v1",
      "name": "General LLM Evaluation v1",
      "description": "Standard evaluation suite for general-purpose language models",
      "benchmark_count": 25,
      "providers": ["lm_evaluation_harness"],
      "categories": ["reasoning", "knowledge", "math", "language_modeling"],
      "created_at": "2024-12-01T00:00:00Z"
    }
  ],
  "total_count": 4
}
```

**Commentary**: Pre-curated benchmark collections for domain-specific evaluation. Healthcare, automotive, finance, and general collections provide standardized evaluation suites for compliance and model validation.

#### **GET** `/collections/{collection_id}` - Get Collection Details
**Purpose**: Detailed collection specification with benchmark list

```bash
curl -X GET "{{baseUrl}}/collections/healthcare_safety_v1"
```

#### **POST** `/collections` - Create Custom Collection
**Purpose**: Create custom benchmark collections for organizational needs

```bash
curl -X POST "{{baseUrl}}/collections" \
-H "Content-Type: application/json" \
-d '{
  "collection_id": "custom_eval_v1",
  "name": "Custom Evaluation Suite",
  "description": "Organization-specific benchmark collection",
  "benchmarks": [
    {
      "provider_id": "lm_evaluation_harness",
      "benchmark_id": "arc_easy"
    }
  ]
}'
```

#### **PUT** `/collections/{collection_id}` - Update Collection
#### **DELETE** `/collections/{collection_id}` - Delete Collection

---

### 🖥️ Model Management Endpoints

#### **GET** `/models` - List Registered Models
**Purpose**: Discover available models for evaluation
**Response Model**: `ListModelsResponse`

```bash
curl -X GET "{{baseUrl}}/models?status=active"
```

**Response Example**:
```json
{
  "models": [
    {
      "model_id": "meta-llama-3.1-8b",
      "model_name": "Meta Llama 3.1 8B",
      "description": "Meta's Llama 3.1 8B parameter model",
      "model_type": "language_model",
      "status": "active",
      "capabilities": {
        "text_generation": true,
        "reasoning": true,
        "code_generation": false
      },
      "created_at": "2025-01-10T00:00:00Z"
    }
  ],
  "total_count": 15
}
```

#### **GET** `/models/{model_id}` - Get Model Details
#### **POST** `/models` - Register New Model
#### **PUT** `/models/{model_id}` - Update Model Configuration
#### **DELETE** `/models/{model_id}` - Unregister Model
#### **POST** `/models/reload` - Reload Runtime Models

---

### 🌐 Server Management Endpoints

#### **GET** `/servers` - List Model Servers
**Purpose**: Manage inference server endpoints

```bash
curl -X GET "{{baseUrl}}/servers"
```

#### **GET** `/servers/{server_id}` - Get Server Details
#### **POST** `/servers` - Register Model Server
#### **PUT** `/servers/{server_id}` - Update Server Configuration
#### **DELETE** `/servers/{server_id}` - Unregister Server
#### **POST** `/servers/reload` - Reload Runtime Servers

---

### 📈 Monitoring & Metrics Endpoints

#### **GET** `/metrics/system` - Get System Metrics
**Purpose**: Prometheus-compatible metrics for monitoring

```bash
curl -X GET "{{baseUrl}}/metrics/system"
```

**Response Example**:
```json
{
  "active_evaluations": 3,
  "completed_evaluations_24h": 45,
  "failed_evaluations_24h": 2,
  "average_evaluation_time_seconds": 245.5,
  "system": {
    "cpu_usage_percent": 65.2,
    "memory_usage_percent": 72.1,
    "disk_usage_percent": 45.8
  },
  "providers": {
    "lm_evaluation_harness": {
      "status": "healthy",
      "evaluations_24h": 35
    },
    "ragas": {
      "status": "healthy",
      "evaluations_24h": 8
    }
  }
}
```

---

## Advanced Features

### Asynchronous Execution Pattern
The API supports both synchronous and asynchronous execution:
- **Async Mode** (default): Returns immediately with tracking ID, enables parallel processing
- **Sync Mode**: Blocks until completion, suitable for simple workflows
- **Status Polling**: Regular status checks for async evaluations
- **Callback URLs**: Optional webhook notifications on completion

### Batch Processing Capabilities
```bash
# Submit multiple evaluations in single request
curl -X POST "{{baseUrl}}/evaluations" \
-d '{
  "evaluations": [
    {
      "benchmark": {"benchmark_id": "arc_easy", "provider_id": "lm_evaluation_harness"},
      "backend": {"backend_type": "llama_stack", "model_id": "model-a"}
    },
    {
      "benchmark": {"benchmark_id": "faithfulness", "provider_id": "ragas"},
      "backend": {"backend_type": "llama_stack", "model_id": "model-b"}
    }
  ]
}'
```

### MLFlow Integration
- **Experiment Tracking**: Automatic MLFlow experiment creation
- **Result Persistence**: Metrics and artifacts stored in MLFlow
- **Lineage Tracking**: Full evaluation provenance
- **Model Registry**: Integration with model governance workflows

### Error Handling & Validation
- **Request Validation**: Comprehensive Pydantic-based validation
- **Provider Validation**: Backend capability verification
- **Graceful Degradation**: Partial execution on provider failures
- **Detailed Error Messages**: Structured error responses with context

---

## Integration Patterns

### Enterprise MLOps Workflow
1. **Model Registration**: Register models via `/models` endpoint
2. **Collection Selection**: Choose domain-specific collections
3. **Evaluation Submission**: Submit batch evaluations
4. **Progress Monitoring**: Poll status endpoints
5. **Result Retrieval**: Access results via MLFlow integration
6. **Governance Integration**: Surface metrics in model registry

### Development & Testing Workflow
1. **Health Check**: Verify service status
2. **Provider Discovery**: List available providers and benchmarks
3. **Single Evaluation**: Test with `/evaluations/single`
4. **Batch Evaluation**: Scale to multiple benchmarks
5. **Custom Collections**: Create organization-specific suites

### Continuous Integration Pattern
```bash
# CI/CD Pipeline Integration
./evaluate-model.sh model-v2.1 healthcare_safety_v1
# 1. Register model endpoint
# 2. Submit collection evaluation
# 3. Wait for completion
# 4. Parse results for gate decisions
```

---

## API Examples and Use Cases