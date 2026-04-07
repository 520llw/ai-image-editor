"""
AI service for image generation using Stable Diffusion
"""
import os
import gc
import uuid
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from PIL import Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler

from app.config import settings
from app.models.schemas import TaskStatus, GenerationTask, GenerationStyle

logger = logging.getLogger(__name__)


# Style presets with prompt enhancements
STYLE_PROMPTS = {
    GenerationStyle.NONE: "",
    GenerationStyle.PHOTOREALISTIC: ", photorealistic, highly detailed, 8k uhd, professional photography",
    GenerationStyle.ANIME: ", anime style, manga art, vibrant colors, detailed illustration",
    GenerationStyle.DIGITAL_ART: ", digital art, concept art, trending on artstation, highly detailed",
    GenerationStyle.OIL_PAINTING: ", oil painting, classical art style, textured brushstrokes, museum quality",
    GenerationStyle.WATERCOLOR: ", watercolor painting, soft colors, artistic, flowing style",
    GenerationStyle.SKETCH: ", pencil sketch, hand drawn, artistic sketch, detailed linework",
    GenerationStyle.CINEMATIC: ", cinematic lighting, dramatic composition, movie still, film grain"
}

NEGATIVE_PROMPT_BASE = "low quality, blurry, distorted, deformed, ugly, bad anatomy, watermark, signature, text, cropped, out of frame"


class ModelManager:
    """Singleton manager for AI models"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if ModelManager._initialized:
            return
        
        self.device = settings.get_device()
        self.model_cache_dir = settings.MODEL_CACHE_DIR
        self.current_model_id = None
        self.pipeline = None
        self.is_loading = False
        
        # Ensure cache directory exists
        os.makedirs(self.model_cache_dir, exist_ok=True)
        
        ModelManager._initialized = True
        logger.info(f"ModelManager initialized with device: {self.device}")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get GPU memory usage in GB"""
        if self.device == "cuda" and torch.cuda.is_available():
            return {
                "allocated": torch.cuda.memory_allocated() / 1e9,
                "reserved": torch.cuda.memory_reserved() / 1e9,
                "max_allocated": torch.cuda.max_memory_allocated() / 1e9
            }
        return {"allocated": 0, "reserved": 0, "max_allocated": 0}
    
    def clear_cache(self) -> None:
        """Clear GPU cache"""
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
    
    async def load_model(self, model_id: Optional[str] = None) -> bool:
        """
        Load AI model asynchronously
        
        Args:
            model_id: Model identifier (uses default if None)
            
        Returns:
            True if model loaded successfully
        """
        model_id = model_id or settings.DEFAULT_MODEL
        
        # Check if already loaded
        if self.current_model_id == model_id and self.pipeline is not None:
            logger.info(f"Model {model_id} already loaded")
            return True
        
        if self.is_loading:
            logger.warning("Model is already being loaded")
            return False
        
        self.is_loading = True
        
        try:
            # Run model loading in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_model_sync, model_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            self.pipeline = None
            self.current_model_id = None
            return False
            
        finally:
            self.is_loading = False
    
    def _load_model_sync(self, model_id: str) -> None:
        """Synchronous model loading"""
        logger.info(f"Loading model: {model_id}")
        
        # Unload existing model first
        if self.pipeline is not None:
            self.unload_model()
        
        # Determine dtype based on device
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        # Load pipeline
        self.pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            cache_dir=self.model_cache_dir,
            safety_checker=None,  # Disable safety checker for speed
            requires_safety_checker=False
        )
        
        # Use faster scheduler
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipeline.scheduler.config,
            algorithm_type="dpmsolver++"
        )
        
        # Move to device
        self.pipeline = self.pipeline.to(self.device)
        
        # Enable memory optimizations for CUDA
        if self.device == "cuda":
            # Enable attention slicing
            self.pipeline.enable_attention_slicing(1)
            
            # Try to enable xformers if available
            try:
                self.pipeline.enable_xformers_memory_efficient_attention()
                logger.info("XFormers memory efficient attention enabled")
            except Exception as e:
                logger.warning(f"Could not enable xformers: {e}")
            
            # Enable VAE slicing for larger images
            if hasattr(self.pipeline, "enable_vae_slicing"):
                self.pipeline.enable_vae_slicing()
        
        self.current_model_id = model_id
        logger.info(f"Model {model_id} loaded successfully")
        
        # Log memory usage
        memory = self.get_memory_usage()
        logger.info(f"GPU Memory: {memory['allocated']:.2f}GB allocated")
    
    def unload_model(self) -> None:
        """Unload current model and free memory"""
        if self.pipeline is not None:
            logger.info(f"Unloading model: {self.current_model_id}")
            del self.pipeline
            self.pipeline = None
            self.current_model_id = None
            self.clear_cache()
            logger.info("Model unloaded")


class AIService:
    """Service for AI image generation"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.tasks: Dict[str, GenerationTask] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
        
        # Generation settings
        self.max_image_size = settings.MAX_IMAGE_SIZE
        self.default_steps = settings.DEFAULT_STEPS
        self.default_strength = settings.DEFAULT_STRENGTH
    
    def _resize_image_if_needed(self, image: Image.Image) -> Image.Image:
        """Resize image if it exceeds maximum dimensions"""
        max_size = self.max_image_size
        
        if image.width > max_size or image.height > max_size:
            # Calculate new size maintaining aspect ratio
            ratio = min(max_size / image.width, max_size / image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            logger.info(f"Resizing image from {image.width}x{image.height} to {new_width}x{new_height}")
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def _enhance_prompt(self, prompt: str, style: GenerationStyle) -> str:
        """Enhance prompt with style preset"""
        style_suffix = STYLE_PROMPTS.get(style, "")
        if style_suffix:
            return prompt + style_suffix
        return prompt
    
    def _get_negative_prompt(self, user_negative: str) -> str:
        """Combine base negative prompt with user negative prompt"""
        if user_negative and user_negative.strip():
            return f"{NEGATIVE_PROMPT_BASE}, {user_negative.strip()}"
        return NEGATIVE_PROMPT_BASE
    
    async def create_task(
        self,
        image_id: str,
        prompt: str,
        negative_prompt: str = "",
        style: GenerationStyle = GenerationStyle.NONE,
        strength: float = 0.75,
        steps: int = 30,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> str:
        """
        Create a new generation task
        
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = GenerationTask(
            task_id=task_id,
            status=TaskStatus.PENDING,
            progress=0,
            image_id=image_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            style=style.value,
            strength=strength,
            steps=steps,
            guidance_scale=guidance_scale,
            seed=seed,
            created_at=now,
            updated_at=now
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id} for image {image_id}")
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[GenerationTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def update_task_progress(self, task_id: str, progress: int, message: str = "") -> None:
        """Update task progress"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.progress = progress
            task.updated_at = datetime.now()
            if message:
                logger.info(f"Task {task_id}: {message} ({progress}%)")
            
            # Call progress callback if registered
            if task_id in self.progress_callbacks:
                try:
                    self.progress_callbacks[task_id](task_id, progress, message)
                except Exception as e:
                    logger.error(f"Progress callback error: {e}")
    
    def register_progress_callback(self, task_id: str, callback: Callable) -> None:
        """Register a callback for progress updates"""
        self.progress_callbacks[task_id] = callback
    
    def unregister_progress_callback(self, task_id: str) -> None:
        """Unregister progress callback"""
        if task_id in self.progress_callbacks:
            del self.progress_callbacks[task_id]
    
    async def generate_image(
        self,
        task_id: str,
        source_image: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        style: GenerationStyle = GenerationStyle.NONE,
        strength: float = 0.75,
        steps: int = 30,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Image.Image:
        """
        Generate image using AI model
        
        Args:
            task_id: Task ID for progress tracking
            source_image: Source PIL Image
            prompt: Text prompt
            negative_prompt: Negative prompt
            style: Generation style
            strength: How much to change the image (0.1-1.0)
            steps: Number of inference steps
            guidance_scale: Guidance scale
            seed: Random seed
            
        Returns:
            Generated PIL Image
        """
        # Ensure model is loaded
        if not await self.model_manager.load_model():
            raise RuntimeError("Failed to load AI model")
        
        # Update task status
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.PROCESSING
            task.updated_at = datetime.now()
        
        self.update_task_progress(task_id, 10, "Preparing image...")
        
        # Resize image if needed
        source_image = self._resize_image_if_needed(source_image)
        
        # Convert to RGB if needed
        if source_image.mode != "RGB":
            source_image = source_image.convert("RGB")
        
        # Enhance prompt with style
        enhanced_prompt = self._enhance_prompt(prompt, style)
        full_negative_prompt = self._get_negative_prompt(negative_prompt)
        
        self.update_task_progress(task_id, 20, "Generating image...")
        
        # Set seed if provided
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.model_manager.device).manual_seed(seed)
        
        # Create progress callback
        def progress_callback(pipe, step_index, timestep, callback_kwargs):
            progress = 20 + int((step_index / steps) * 70)
            self.update_task_progress(task_id, progress, f"Generating... step {step_index}/{steps}")
            return callback_kwargs
        
        try:
            # Run generation in thread pool
            loop = asyncio.get_event_loop()
            
            def generate():
                return self.model_manager.pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=full_negative_prompt,
                    image=source_image,
                    strength=strength,
                    num_inference_steps=steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    callback_on_step_end=progress_callback,
                    callback_on_step_end_tensor_inputs=["latents"]
                )
            
            result = await loop.run_in_executor(None, generate)
            
            self.update_task_progress(task_id, 95, "Finalizing...")
            
            return result.images[0]
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def complete_task(self, task_id: str, result_image_id: Optional[str] = None) -> None:
        """Mark task as completed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.result_image_id = result_image_id
            task.completed_at = datetime.now()
            task.updated_at = datetime.now()
            self.unregister_progress_callback(task_id)
            logger.info(f"Task {task_id} completed")
    
    def fail_task(self, task_id: str, error_message: str) -> None:
        """Mark task as failed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error_message = error_message
            task.updated_at = datetime.now()
            self.unregister_progress_callback(task_id)
            logger.error(f"Task {task_id} failed: {error_message}")
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        return [
            {
                "id": "runwayml/stable-diffusion-v1-5",
                "name": "Stable Diffusion v1.5",
                "description": "General purpose image-to-image generation",
                "type": "img2img",
                "is_loaded": self.model_manager.current_model_id == "runwayml/stable-diffusion-v1-5",
                "is_available": True
            }
        ]
    
    def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up old completed/failed tasks"""
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.updated_at < cutoff_time:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
            self.unregister_progress_callback(task_id)
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old tasks")
        
        return len(to_remove)


# Global AI service instance
ai_service = AIService()
