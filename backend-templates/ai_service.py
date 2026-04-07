# backend/app/services/ai_service.py
import torch
from PIL import Image
from pathlib import Path
from typing import Optional, Callable
from diffusers import StableDiffusionImg2ImgPipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    """AI图片生成服务"""
    
    _instance = None
    _pipeline = None
    _model_loaded = False
    
    def __new__(cls, settings):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, settings):
        self.settings = settings
        self.device = settings.DEVICE if torch.cuda.is_available() else "cpu"
        self.model_id = settings.DEFAULT_MODEL
        self.model_cache_dir = settings.MODEL_CACHE_DIR
        
    def load_model(self):
        """加载AI模型（懒加载）"""
        if self._model_loaded:
            logger.info("模型已加载，跳过")
            return
        
        logger.info(f"正在加载模型: {self.model_id}")
        logger.info(f"使用设备: {self.device}")
        
        try:
            # 加载pipeline
            self._pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                cache_dir=self.model_cache_dir,
                use_safetensors=True,
            )
            
            # 移动到GPU
            self._pipeline = self._pipeline.to(self.device)
            
            # 启用内存优化
            if self.device == "cuda":
                # 启用xformers加速
                try:
                    self._pipeline.enable_xformers_memory_efficient_attention()
                    logger.info("已启用xformers加速")
                except Exception as e:
                    logger.warning(f"xformers启用失败: {e}")
                
                # 启用注意力切片
                self._pipeline.enable_attention_slicing(1)
                logger.info("已启用注意力切片")
                
                # 启用VAE切片
                if hasattr(self._pipeline, 'vae'):
                    self._pipeline.enable_vae_slicing()
                    logger.info("已启用VAE切片")
            
            self._model_loaded = True
            logger.info("模型加载完成")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def unload_model(self):
        """卸载模型释放显存"""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self._model_loaded = False
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("模型已卸载")
    
    async def generate(
        self,
        source_path: str,
        output_path: str,
        prompt: str,
        negative_prompt: str = "",
        strength: float = 0.75,
        steps: int = 30,
        guidance_scale: float = 7.5,
        progress_callback: Optional[Callable[[float], None]] = None
    ):
        """生成图片"""
        if not self._model_loaded:
            raise RuntimeError("模型未加载")
        
        logger.info(f"开始生成图片: prompt='{prompt}', strength={strength}")
        
        # 加载源图片
        source_image = Image.open(source_path).convert("RGB")
        
        # 调整图片尺寸（最大1024）
        max_size = 1024
        width, height = source_image.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            source_image = source_image.resize((new_width, new_height), Image.LANCZOS)
            logger.info(f"图片已调整尺寸: {width}x{height} -> {new_width}x{new_height}")
        
        # 创建进度回调
        def callback_on_step_end(pipe, step_index, timestep, callback_kwargs):
            progress = (step_index + 1) / steps
            if progress_callback:
                progress_callback(progress)
            return callback_kwargs
        
        # 执行生成
        try:
            result = self._pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=source_image,
                strength=strength,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                callback_on_step_end=callback_on_step_end,
                callback_on_step_end_tensor_inputs=["latents"],
            )
            
            # 保存结果
            output_image = result.images[0]
            output_image.save(output_path, "PNG")
            
            logger.info(f"图片生成完成: {output_path}")
            
        except Exception as e:
            logger.error(f"图片生成失败: {e}")
            raise
    
    def get_memory_info(self) -> dict:
        """获取显存使用信息"""
        if torch.cuda.is_available():
            return {
                "allocated_gb": torch.cuda.memory_allocated() / 1e9,
                "reserved_gb": torch.cuda.memory_reserved() / 1e9,
                "max_allocated_gb": torch.cuda.max_memory_allocated() / 1e9,
            }
        return {"device": "cpu"}
