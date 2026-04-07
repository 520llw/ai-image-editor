"""
Image API routes for upload, generation, and download
"""
import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse

from app.models.schemas import (
    ImageUploadResponse,
    ImageGenerateRequest,
    ImageGenerateResponse,
    TaskStatusResponse,
    ImageInfoResponse,
    ModelsListResponse,
    ModelInfo,
    TaskStatus,
    GenerationStyle,
    DeleteImageResponse,
    ErrorResponse
)
from app.services.image_service import image_service
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/images", tags=["images"])


@router.post(
    "/upload",
    response_model=ImageUploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Upload an image",
    description="Upload an image file for editing. Supported formats: jpg, jpeg, png, webp. Max size: 10MB"
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload")
) -> ImageUploadResponse:
    """
    Upload an image file for editing.
    
    - **file**: Image file (jpg, jpeg, png, webp)
    - Max file size: 10MB
    """
    try:
        # Read file content
        content = await file.read()
        
        # Validate and save
        result = await image_service.save_upload(
            file_data=content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        return ImageUploadResponse(
            success=True,
            image_id=result["image_id"],
            filename=result["filename"],
            url=result["url"],
            width=result["width"],
            height=result["height"],
            format=result["format"],
            size_bytes=result["size_bytes"],
            message="Image uploaded successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Upload validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.post(
    "/generate",
    response_model=ImageGenerateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        404: {"model": ErrorResponse, "description": "Image not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Generate edited image",
    description="Generate an edited version of the uploaded image using AI"
)
async def generate_image(
    background_tasks: BackgroundTasks,
    request: ImageGenerateRequest
) -> ImageGenerateResponse:
    """
    Generate an edited image based on the uploaded image and prompt.
    
    - **image_id**: ID of the uploaded source image
    - **prompt**: Text description of desired changes
    - **negative_prompt**: (optional) Things to avoid
    - **style**: (optional) Generation style preset
    - **strength**: (optional) How much to change (0.1-1.0, default: 0.75)
    - **steps**: (optional) Inference steps (1-50, default: 30)
    - **guidance_scale**: (optional) Guidance scale (1.0-20.0, default: 7.5)
    - **seed**: (optional) Random seed for reproducibility
    """
    try:
        # Check if source image exists
        source_image = image_service.get_image(request.image_id)
        if source_image is None:
            raise HTTPException(
                status_code=404,
                detail=f"Source image not found: {request.image_id}"
            )
        
        # Create generation task
        task_id = await ai_service.create_task(
            image_id=request.image_id,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt or "",
            style=request.style,
            strength=request.strength,
            steps=request.steps,
            guidance_scale=request.guidance_scale,
            seed=request.seed
        )
        
        # Start background generation task
        background_tasks.add_task(
            process_generation_task,
            task_id=task_id,
            source_image=source_image,
            request=request
        )
        
        return ImageGenerateResponse(
            success=True,
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="Image generation started",
            estimated_time_seconds=request.steps * 2  # Rough estimate
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")


async def process_generation_task(
    task_id: str,
    source_image,
    request: ImageGenerateRequest
) -> None:
    """Background task for image generation"""
    try:
        # Generate image
        result_image = await ai_service.generate_image(
            task_id=task_id,
            source_image=source_image,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt or "",
            style=request.style,
            strength=request.strength,
            steps=request.steps,
            guidance_scale=request.guidance_scale,
            seed=request.seed
        )
        
        # Save result
        ai_service.update_task_progress(task_id, 95, "Saving result...")
        save_result = await image_service.save_output(
            image=result_image,
            original_id=request.image_id,
            format="png"
        )
        
        # Complete task
        ai_service.complete_task(task_id, save_result["image_id"])
        
        # Update task with result URL
        task = ai_service.get_task(task_id)
        if task:
            task.result_url = save_result["url"]
        
        logger.info(f"Generation task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Generation task {task_id} failed: {e}")
        ai_service.fail_task(task_id, str(e))


@router.get(
    "/status/{task_id}",
    response_model=TaskStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"}
    },
    summary="Get task status",
    description="Get the current status of an image generation task"
)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Get the status of a generation task.
    
    - **task_id**: The task ID returned by the generate endpoint
    """
    task = ai_service.get_task(task_id)
    
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        progress=task.progress,
        message=get_status_message(task.status, task.progress),
        result_url=task.result_url,
        result_image_id=task.result_image_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        error_message=task.error_message
    )


def get_status_message(status: TaskStatus, progress: int) -> str:
    """Get human-readable status message"""
    messages = {
        TaskStatus.PENDING: "Waiting to start...",
        TaskStatus.PROCESSING: f"Processing... {progress}%",
        TaskStatus.COMPLETED: "Generation completed",
        TaskStatus.FAILED: "Generation failed",
        TaskStatus.CANCELLED: "Generation cancelled"
    }
    return messages.get(status, "Unknown status")


@router.get(
    "/download/{image_id}",
    responses={
        404: {"model": ErrorResponse, "description": "Image not found"}
    },
    summary="Download image",
    description="Download an uploaded or generated image by ID"
)
async def download_image(
    image_id: str,
    is_output: bool = Query(default=False, description="Whether to look in output directory")
):
    """
    Download an image file.
    
    - **image_id**: The image ID
    - **is_output**: Set to true for generated images
    """
    file_path = image_service.get_image_path(image_id, is_output)
    
    if file_path is None or not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Image not found: {image_id}")
    
    # Determine media type
    ext = file_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }
    media_type = media_types.get(ext, "application/octet-stream")
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_path.name
    )


@router.get(
    "/info/{image_id}",
    response_model=ImageInfoResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Image not found"}
    },
    summary="Get image info",
    description="Get information about an uploaded or generated image"
)
async def get_image_info(
    image_id: str,
    is_output: bool = Query(default=False, description="Whether to look in output directory")
) -> ImageInfoResponse:
    """
    Get information about an image.
    
    - **image_id**: The image ID
    - **is_output**: Set to true for generated images
    """
    file_path = image_service.get_image_path(image_id, is_output)
    
    if file_path is None or not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Image not found: {image_id}")
    
    # Get image info
    img_info = image_service.get_image_info(file_path)
    stat = file_path.stat()
    
    return ImageInfoResponse(
        image_id=image_id,
        filename=file_path.name,
        url=f"/{'outputs' if is_output else 'uploads'}/{file_path.name}",
        width=img_info["width"],
        height=img_info["height"],
        format=img_info["format"],
        size_bytes=stat.st_size,
        created_at=datetime.fromtimestamp(stat.st_ctime),
        is_output=is_output
    )


@router.delete(
    "/{image_id}",
    response_model=DeleteImageResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Image not found"}
    },
    summary="Delete image",
    description="Delete an uploaded or generated image"
)
async def delete_image(
    image_id: str,
    is_output: bool = Query(default=False, description="Whether to look in output directory")
) -> DeleteImageResponse:
    """
    Delete an image file.
    
    - **image_id**: The image ID
    - **is_output**: Set to true for generated images
    """
    deleted = image_service.delete_image(image_id, is_output)
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Image not found: {image_id}")
    
    return DeleteImageResponse(
        success=True,
        image_id=image_id,
        message="Image deleted successfully"
    )


@router.get(
    "/models/available",
    response_model=ModelsListResponse,
    summary="Get available models",
    description="Get list of available AI models"
)
async def get_available_models() -> ModelsListResponse:
    """Get list of available AI models"""
    models = ai_service.get_available_models()
    
    model_infos = [
        ModelInfo(
            id=m["id"],
            name=m["name"],
            description=m["description"],
            type=m["type"],
            is_loaded=m["is_loaded"],
            is_available=m["is_available"]
        )
        for m in models
    ]
    
    return ModelsListResponse(
        models=model_infos,
        default_model="runwayml/stable-diffusion-v1-5",
        current_model=ai_service.model_manager.current_model_id
    )


@router.post(
    "/generate-simple",
    response_model=ImageGenerateResponse,
    summary="Generate image (simple form)",
    description="Simple form-based image generation endpoint"
)
async def generate_image_simple(
    background_tasks: BackgroundTasks,
    image_id: str = Form(..., description="Source image ID"),
    prompt: str = Form(..., description="Generation prompt"),
    negative_prompt: Optional[str] = Form(default="", description="Negative prompt"),
    style: GenerationStyle = Form(default=GenerationStyle.NONE, description="Generation style"),
    strength: float = Form(default=0.75, ge=0.1, le=1.0, description="Generation strength"),
    steps: int = Form(default=30, ge=1, le=50, description="Inference steps"),
    guidance_scale: float = Form(default=7.5, ge=1.0, le=20.0, description="Guidance scale"),
    seed: Optional[int] = Form(default=None, description="Random seed")
) -> ImageGenerateResponse:
    """
    Generate image using form data (for simple HTML forms).
    Same functionality as /generate but accepts form data.
    """
    request = ImageGenerateRequest(
        image_id=image_id,
        prompt=prompt,
        negative_prompt=negative_prompt,
        style=style,
        strength=strength,
        steps=steps,
        guidance_scale=guidance_scale,
        seed=seed
    )
    return await generate_image(background_tasks, request)
