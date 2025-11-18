"""Model data models for language model registration and management."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelType(str, Enum):
    """Type of language model."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    VLLM = "vllm"
    OPENAI_COMPATIBLE = "openai-compatible"
    CUSTOM = "custom"


class ModelStatus(str, Enum):
    """Status of a registered model."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"


class ModelCapabilities(BaseModel):
    """Model capabilities and limitations."""

    model_config = ConfigDict(extra="allow")

    max_tokens: int | None = Field(
        None, description="Maximum tokens supported by the model"
    )
    supports_streaming: bool = Field(
        default=False, description="Whether the model supports streaming responses"
    )
    supports_function_calling: bool = Field(
        default=False, description="Whether the model supports function calling"
    )
    supports_vision: bool = Field(
        default=False, description="Whether the model supports vision/image inputs"
    )
    context_window: int | None = Field(None, description="Model's context window size")


class ModelConfig(BaseModel):
    """Model configuration parameters."""

    model_config = ConfigDict(extra="allow")

    temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Default temperature setting"
    )
    max_tokens: int | None = Field(
        None, gt=0, description="Default max tokens for responses"
    )
    top_p: float | None = Field(
        None, ge=0.0, le=1.0, description="Default top_p setting"
    )
    frequency_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="Default frequency penalty"
    )
    presence_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="Default presence penalty"
    )
    timeout: int | None = Field(30, gt=0, description="Request timeout in seconds")
    retry_attempts: int | None = Field(3, ge=0, description="Number of retry attempts")


class Model(BaseModel):
    """Language model specification."""

    model_config = ConfigDict(extra="allow")

    model_id: str = Field(..., description="Unique model identifier")
    model_name: str = Field(..., description="Human-readable model name")
    description: str = Field(..., description="Model description")
    model_type: ModelType = Field(..., description="Type of model")
    base_url: str = Field(..., description="Base URL for the model API")
    api_key_required: bool = Field(
        default=True, description="Whether an API key is required"
    )
    model_path: str | None = Field(
        None, description="Model path or identifier within the service"
    )
    capabilities: ModelCapabilities = Field(
        default_factory=lambda: ModelCapabilities(max_tokens=None, context_window=None),
        description="Model capabilities",
    )
    config: ModelConfig = Field(
        default_factory=lambda: ModelConfig(
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            timeout=30,
            retry_attempts=3,
        ),
        description="Default model configuration",
    )
    status: ModelStatus = Field(default=ModelStatus.ACTIVE, description="Model status")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="When the model was registered"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="When the model was last updated"
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate that base_url is a valid URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must be a valid HTTP or HTTPS URL")
        return v

    @field_validator("model_id")
    @classmethod
    def validate_model_id(cls, v: str) -> str:
        """Validate model_id format."""
        if not v.strip():
            raise ValueError("model_id cannot be empty")
        # Allow alphanumeric, hyphens, underscores, and dots
        import re

        if not re.match(r"^[a-zA-Z0-9._-]+$", v):
            raise ValueError(
                "model_id can only contain letters, numbers, dots, hyphens, and underscores"
            )
        return v.strip()


class ModelSummary(BaseModel):
    """Simplified model information without detailed configuration."""

    model_config = ConfigDict(extra="allow")

    model_id: str = Field(..., description="Unique model identifier")
    model_name: str = Field(..., description="Human-readable model name")
    description: str = Field(..., description="Model description")
    model_type: ModelType = Field(..., description="Type of model")
    base_url: str = Field(..., description="Base URL for the model API")
    status: ModelStatus = Field(..., description="Model status")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(..., description="When the model was registered")


class ModelRegistrationRequest(BaseModel):
    """Request model for registering a new model."""

    model_config = ConfigDict(extra="allow")

    model_id: str = Field(..., description="Unique model identifier")
    model_name: str = Field(..., description="Human-readable model name")
    description: str = Field(..., description="Model description")
    model_type: ModelType = Field(..., description="Type of model")
    base_url: str = Field(..., description="Base URL for the model API")
    api_key_required: bool = Field(
        default=True, description="Whether an API key is required"
    )
    model_path: str | None = Field(
        None, description="Model path or identifier within the service"
    )
    capabilities: ModelCapabilities | None = Field(
        None, description="Model capabilities"
    )
    config: ModelConfig | None = Field(None, description="Default model configuration")
    status: ModelStatus = Field(default=ModelStatus.ACTIVE, description="Model status")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")


class ModelUpdateRequest(BaseModel):
    """Request model for updating an existing model."""

    model_config = ConfigDict(extra="allow")

    model_name: str | None = Field(None, description="Human-readable model name")
    description: str | None = Field(None, description="Model description")
    model_type: ModelType | None = Field(None, description="Type of model")
    base_url: str | None = Field(None, description="Base URL for the model API")
    api_key_required: bool | None = Field(
        None, description="Whether an API key is required"
    )
    model_path: str | None = Field(
        None, description="Model path or identifier within the service"
    )
    capabilities: ModelCapabilities | None = Field(
        None, description="Model capabilities"
    )
    config: ModelConfig | None = Field(None, description="Default model configuration")
    status: ModelStatus | None = Field(None, description="Model status")
    tags: list[str] | None = Field(None, description="Tags for categorization")


class ListModelsResponse(BaseModel):
    """Response for listing all models."""

    model_config = ConfigDict(extra="allow")

    models: list[ModelSummary] = Field(..., description="List of available models")
    total_models: int = Field(..., description="Total number of models")
    runtime_models: list[ModelSummary] = Field(
        default_factory=list, description="Models specified via environment variables"
    )


class RuntimeModelConfig(BaseModel):
    """Configuration for runtime-specified models via environment variables."""

    model_config = ConfigDict(extra="allow")

    model_id: str = Field(..., description="Runtime model identifier")
    model_name: str = Field(..., description="Runtime model name")
    description: str = Field(
        default="Runtime-specified model", description="Model description"
    )
    model_type: ModelType = Field(
        default=ModelType.OPENAI_COMPATIBLE, description="Type of model"
    )
    base_url: str = Field(..., description="Base URL from environment variable")
    api_key_required: bool = Field(
        default=True, description="Whether an API key is required"
    )
    model_path: str | None = Field(
        None, description="Model path or identifier within the service"
    )


class ModelsData(BaseModel):
    """Complete models configuration data."""

    model_config = ConfigDict(extra="allow")

    models: list[Model] = Field(
        default_factory=list, description="List of registered models"
    )


# Model Server structures


class ServerModel(BaseModel):
    """A model available on a model server."""

    model_config = ConfigDict(extra="allow")

    model_name: str = Field(..., description="Name of the model on the server")
    description: str | None = Field(None, description="Model description")
    capabilities: ModelCapabilities | None = Field(
        None, description="Model capabilities"
    )
    config: ModelConfig | None = Field(None, description="Default model configuration")
    status: ModelStatus = Field(default=ModelStatus.ACTIVE, description="Model status")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")


class ModelServer(BaseModel):
    """Model server that can host multiple models."""

    model_config = ConfigDict(extra="allow")

    server_id: str = Field(..., description="Unique server identifier")
    server_type: ModelType = Field(..., description="Type of model server")
    base_url: str = Field(..., description="Base URL for the server API")
    api_key_required: bool = Field(
        default=True, description="Whether an API key is required"
    )
    models: list[ServerModel] = Field(
        default_factory=list, description="List of models available on this server"
    )
    server_config: ModelConfig | None = Field(
        None, description="Default server-level configuration"
    )
    status: ModelStatus = Field(default=ModelStatus.ACTIVE, description="Server status")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="When the server was registered"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="When the server was last updated"
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate that base_url is a valid URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must be a valid HTTP or HTTPS URL")
        return v

    @field_validator("server_id")
    @classmethod
    def validate_server_id(cls, v: str) -> str:
        """Validate server_id format."""
        if not v.strip():
            raise ValueError("server_id cannot be empty")
        import re

        if not re.match(r"^[a-zA-Z0-9._-]+$", v):
            raise ValueError(
                "server_id can only contain letters, numbers, dots, hyphens, and underscores"
            )
        return v.strip()


class ModelServerSummary(BaseModel):
    """Simplified model server information."""

    model_config = ConfigDict(extra="allow")

    server_id: str = Field(..., description="Unique server identifier")
    server_type: ModelType = Field(..., description="Type of model server")
    base_url: str = Field(..., description="Base URL for the server API")
    model_count: int = Field(..., description="Number of models on this server")
    status: ModelStatus = Field(..., description="Server status")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(..., description="When the server was registered")


class ModelServerRegistrationRequest(BaseModel):
    """Request model for registering a new model server."""

    model_config = ConfigDict(extra="allow")

    server_id: str = Field(..., description="Unique server identifier")
    server_type: ModelType = Field(..., description="Type of model server")
    base_url: str = Field(..., description="Base URL for the server API")
    api_key_required: bool = Field(
        default=True, description="Whether an API key is required"
    )
    models: list[ServerModel] = Field(
        default_factory=list, description="List of models available on this server"
    )
    server_config: ModelConfig | None = Field(
        None, description="Default server-level configuration"
    )
    status: ModelStatus = Field(default=ModelStatus.ACTIVE, description="Server status")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")


class ModelServerUpdateRequest(BaseModel):
    """Request model for updating an existing model server."""

    model_config = ConfigDict(extra="allow")
    base_url: str | None = Field(None, description="Base URL for the server API")
    api_key_required: bool | None = Field(
        None, description="Whether an API key is required"
    )
    models: list[ServerModel] | None = Field(
        None, description="List of models available on this server"
    )
    server_config: ModelConfig | None = Field(
        None, description="Default server-level configuration"
    )
    status: ModelStatus | None = Field(None, description="Server status")
    tags: list[str] | None = Field(None, description="Tags for categorization")


class ListModelServersResponse(BaseModel):
    """Response for listing all model servers."""

    model_config = ConfigDict(extra="allow")

    servers: list[ModelServerSummary] = Field(
        ..., description="List of available model servers"
    )
    total_servers: int = Field(..., description="Total number of servers")
    runtime_servers: list[ModelServerSummary] = Field(
        default_factory=list, description="Servers specified via environment variables"
    )
