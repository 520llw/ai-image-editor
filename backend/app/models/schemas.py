"""
Pydantic models for request/response validation
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ImageFormat(str, Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"


class GenerationStyle(str, Enum):
    """Generation style options"""
    NONE = "none"
    PHOTOREALISTIC = "photorealistic"
    ANIME = "anime"
    DIGITAL_ART = "digital_art"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    SKETCH = "sketch"
    CINEMATIC = "cinematic"


# ============== Request Models ==============

class ImageUploadResponse(BaseModel):
    """Response model for image upload"""
    success: bool = Field(..., description="Upload success status")
    image_id: str = Field(..., description="Unique image identifier")
    filename: str = Field(..., description="Original filename")
    url: str = Field(..., description="URL to access the uploaded image")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    format: str = Field(..., description="Image format")
    size_bytes: int = Field(..., description="File size in bytes")
    message: Optional[str] = Field(None, description="Status message")


class ImageGenerateRequest(BaseModel):
    """Request model for image generation"""
    image_id: str = Field(..., description="ID of the uploaded source image")
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text prompt describing desired changes"
    )
    negative_prompt: Optional[str] = Field(
        default="",
        max_length=1000,
        description="Things to avoid in the generated image"
    )
    style: GenerationStyle = Field(
        default=GenerationStyle.NONE,
        description="Generation style preset"
    )
    strength: float = Field(
        default=0.75,
        ge=0.1,
        le=1.0,
        description="How much to change the original image (0.1-1.0)"
    )
    steps: int = Field(
        default=30,
        ge=1,
        le=50,
        description="Number of inference steps (1-50)"
    )
    guidance_scale: float = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="Guidance scale for generation"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility"
    )
    
    @validator("prompt")
    def validate_prompt(cls, v: str) -> str:
        """Validate prompt is not empty after stripping"""
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class ImageGenerateResponse(BaseModel):
    """Response model for image generation request"""
    success: bool = Field(..., description="Request success status")
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Status message")
    estimated_time_seconds: Optional[int] = Field(
        None,
        description="Estimated processing time in seconds"
    )


class TaskStatusResponse(BaseModel):
    """Response model for task status query"""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Progress percentage (0-100)"
    )
    message: Optional[str] = Field(None, description="Status message")
    result_url: Optional[str] = Field(None, description="URL to download result")
    result_image_id: Optional[str] = Field(None, description="Result image ID")
    created_at: Optional[datetime] = Field(None, description="Task creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class ImageInfoResponse(BaseModel):
    """Response model for image information"""
    image_id: str = Field(..., description="Unique image identifier")
    filename: str = Field(..., description="Filename")
    url: str = Field(..., description="URL to access the image")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    format: str = Field(..., description="Image format")
    size_bytes: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="Creation time")
    is_output: bool = Field(default=False, description="Whether this is an output image")


class ModelInfo(BaseModel):
    """Model information"""
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Model display name")
    description: str = Field(..., description="Model description")
    type: str = Field(..., description="Model type (img2img, inpainting, etc.)")
    is_loaded: bool = Field(default=False, description="Whether model is loaded")
    is_available: bool = Field(default=True, description="Whether model is available")


class ModelsListResponse(BaseModel):
    """Response model for available models list"""
    models: List[ModelInfo] = Field(..., description="List of available models")
    default_model: str = Field(..., description="Default model ID")
    current_model: Optional[str] = Field(None, description="Currently loaded model")


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current timestamp")
    device: str = Field(..., description="AI inference device")
    cuda_available: bool = Field(..., description="Whether CUDA is available")
    models_loaded: int = Field(..., description="Number of loaded models")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Success status")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class DeleteImageResponse(BaseModel):
    """Response model for image deletion"""
    success: bool = Field(..., description="Deletion success status")
    image_id: str = Field(..., description="Deleted image ID")
    message: str = Field(..., description="Status message")


# ============== Internal Models ==============

class GenerationTask(BaseModel):
    """Internal model for tracking generation tasks"""
    task_id: str
    status: TaskStatus
    progress: int
    image_id: str
    prompt: str
    negative_prompt: str
    style: str
    strength: float
    steps: int
    guidance_scale: float
    seed: Optional[int]
    result_path: Optional[str] = None
    result_image_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
