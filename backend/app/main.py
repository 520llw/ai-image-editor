"""
AI Image Editor - FastAPI Backend
Main application entry point
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.models.schemas import HealthCheckResponse, ErrorResponse
from app.api.routes import image
from app.services.image_service import image_service
from app.services.ai_service import ai_service

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


logger = setup_logging()


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events"""
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info("=" * 50)
    
    # Ensure directories exist
    image_service._ensure_directories()
    
    # Log configuration
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"Output directory: {settings.OUTPUT_DIR}")
    logger.info(f"Max file size: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB")
    logger.info(f"Device: {settings.get_device()}")
    logger.info(f"Default model: {settings.DEFAULT_MODEL}")
    
    # Check CUDA availability
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        logger.info(f"CUDA available: {cuda_available}")
        if cuda_available:
            logger.info(f"CUDA device: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    except ImportError:
        logger.warning("PyTorch not installed")
    
    logger.info("Application started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Unload AI model
    try:
        ai_service.model_manager.unload_model()
        logger.info("AI model unloaded")
    except Exception as e:
        logger.error(f"Error unloading model: {e}")
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered image editing API using Stable Diffusion",
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            success=False,
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": exc.errors()}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error_code="INTERNAL_ERROR",
            message="An internal server error occurred",
            details={"error": str(exc)} if settings.DEBUG else None
        ).model_dump()
    )


# Include API routes
app.include_router(image.router, prefix="/api/v1")

# Mount static file directories
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["health"],
    summary="Health check",
    description="Check if the service is running and get system information"
)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint"""
    import torch
    
    cuda_available = torch.cuda.is_available()
    device = "cuda" if cuda_available else "cpu"
    
    # Get memory info if CUDA available
    memory_info = {}
    if cuda_available:
        memory_info = {
            "allocated_gb": torch.cuda.memory_allocated() / 1e9,
            "reserved_gb": torch.cuda.memory_reserved() / 1e9
        }
    
    models_loaded = 1 if ai_service.model_manager.pipeline is not None else 0
    
    return HealthCheckResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.now(),
        device=device,
        cuda_available=cuda_available,
        models_loaded=models_loaded
    )


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="API info",
    description="Get API information"
)
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "AI-powered image editing API",
        "docs": "/docs" if settings.DEBUG else None,
        "health": "/health",
        "endpoints": {
            "upload": "POST /api/v1/images/upload",
            "generate": "POST /api/v1/images/generate",
            "status": "GET /api/v1/images/status/{task_id}",
            "download": "GET /api/v1/images/download/{image_id}",
            "models": "GET /api/v1/images/models/available"
        }
    }


# Cleanup endpoint (for admin use)
@app.post(
    "/admin/cleanup",
    tags=["admin"],
    summary="Cleanup old files",
    description="Clean up old uploaded and generated files (admin only)"
)
async def cleanup_old_files(max_age_hours: int = 24):
    """Clean up old files"""
    deleted_uploads = image_service.cleanup_old_files(max_age_hours)
    deleted_tasks = ai_service.cleanup_old_tasks(max_age_hours)
    
    return {
        "success": True,
        "deleted_files": deleted_uploads,
        "deleted_tasks": deleted_tasks,
        "max_age_hours": max_age_hours
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
