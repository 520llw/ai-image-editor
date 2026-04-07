"""
InstructPix2Pix 图像编辑管道

基于 timbrooks/instruct-pix2pix 模型的文本指令图像编辑实现
支持显存优化，适合12GB显存运行

作者: AI Assistant
"""

import logging
from typing import Optional, Union, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

import torch
from PIL import Image

# 尝试导入diffusers，未安装时提供友好的错误提示
try:
    from diffusers import StableDiffusionInstructPix2PixPipeline
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    StableDiffusionInstructPix2PixPipeline = None

# 导入工具函数（支持相对导入和绝对导入）
try:
    from ..utils.image_utils import load_image, save_image, validate_image, resize_image
    from ..utils.memory_utils import clear_gpu_cache, get_gpu_memory_info
except ImportError:
    # 直接运行时的备用导入
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.image_utils import load_image, save_image, validate_image, resize_image
    from utils.memory_utils import clear_gpu_cache, get_gpu_memory_info

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """图像生成配置"""
    num_inference_steps: int = 10  # InstructPix2Pix推荐10-20步
    image_guidance_scale: float = 1.5  # 图像引导强度
    guidance_scale: float = 7.5  # 文本引导强度
    num_images_per_prompt: int = 1
    eta: float = 0.0
    generator: Optional[torch.Generator] = None
    output_type: str = "pil"  # "pil" 或 "latent"
    return_dict: bool = True
    callback: Optional[Any] = None
    callback_steps: int = 1


class InstructPix2PixPipeline:
    """
    InstructPix2Pix 图像编辑管道
    
    使用文本指令编辑图像，例如：
    - "make it snowy" (让它下雪)
    - "turn him into a cyborg" (把他变成赛博格)
    - "add fireworks to the sky" (在天空添加烟花)
    
    显存优化配置：
    - 使用 FP16 减少显存占用 (约6-8GB)
    - 启用 CPU offload 进一步降低显存峰值
    
    Usage:
        >>> from ai_models.model_manager import ModelConfig, ModelType
        >>> config = ModelConfig(
        ...     model_id="timbrooks/instruct-pix2pix",
        ...     model_type=ModelType.INSTRUCT_PIX2PIX,
        ...     torch_dtype=torch.float16,
        ...     enable_cpu_offload=True
        ... )
        >>> pipeline = InstructPix2PixPipeline(config)
        >>> result = pipeline.edit_image(
        ...     image_path="input.jpg",
        ...     prompt="make it sunny",
        ...     output_path="output.jpg"
        ... )
    """
    
    # 默认模型ID
    DEFAULT_MODEL_ID = "timbrooks/instruct-pix2pix"
    
    # 推荐的图像尺寸（必须是64的倍数）
    RECOMMENDED_WIDTH = 512
    RECOMMENDED_HEIGHT = 512
    MAX_DIMENSION = 1024
    
    def __init__(self, config: 'ModelConfig'):
        """
        初始化InstructPix2Pix管道
        
        Args:
            config: 模型配置对象
        """
        self.config = config
        self.model_id = config.model_id or self.DEFAULT_MODEL_ID
        self.device = config.device if torch.cuda.is_available() else "cpu"
        self.torch_dtype = config.torch_dtype
        self.enable_cpu_offload = config.enable_cpu_offload
        
        self._pipeline: Optional[StableDiffusionInstructPix2PixPipeline] = None
        self._is_loaded = False
        
        logger.info(f"InstructPix2PixPipeline初始化完成")
        logger.info(f"模型ID: {self.model_id}")
        logger.info(f"设备: {self.device}")
        logger.info(f"数据类型: {self.torch_dtype}")
        logger.info(f"CPU Offload: {self.enable_cpu_offload}")
    
    @property
    def is_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self._is_loaded and self._pipeline is not None
    
    def load(self) -> 'InstructPix2PixPipeline':
        """
        加载模型
        
        Returns:
            self，支持链式调用
            
        Raises:
            RuntimeError: 模型加载失败
        """
        if self._is_loaded:
            logger.info("模型已加载，跳过")
            return self
        
        # 检查diffusers是否可用
        if not DIFFUSERS_AVAILABLE:
            raise RuntimeError(
                "diffusers库未安装。请运行: pip install diffusers>=0.25.0"
            )
        
        try:
            logger.info(f"开始加载模型: {self.model_id}")
            
            # 记录加载前的显存状态
            if torch.cuda.is_available():
                mem_before = get_gpu_memory_info()
                logger.info(f"加载前显存: {mem_before['allocated_gb']:.2f} GB")
            
            # 加载管道
            load_kwargs = {
                "torch_dtype": self.torch_dtype,
                "safety_checker": None,  # 禁用安全检查器，节省显存
            }
            
            # 添加自定义参数
            if self.config.custom_kwargs:
                load_kwargs.update(self.config.custom_kwargs)
            
            # 添加缓存目录
            if self.config.cache_dir:
                load_kwargs["cache_dir"] = self.config.cache_dir
            
            self._pipeline = StableDiffusionInstructPix2PixPipeline.from_pretrained(
                self.model_id,
                **load_kwargs
            )
            
            # 显存优化：启用CPU offload
            if self.enable_cpu_offload and torch.cuda.is_available():
                logger.info("启用模型CPU Offload优化...")
                self._pipeline.enable_model_cpu_offload()
                logger.info("CPU Offload已启用")
            elif torch.cuda.is_available():
                # 如果不使用CPU offload，则移动到GPU
                self._pipeline = self._pipeline.to(self.device)
                logger.info(f"模型已移动到 {self.device}")
            
            # 可选：启用xformers加速（如果已安装）
            try:
                self._pipeline.enable_xformers_memory_efficient_attention()
                logger.info("xformers内存高效注意力已启用")
            except Exception:
                logger.info("xformers未安装，跳过")
            
            self._is_loaded = True
            
            # 记录加载后的显存状态
            if torch.cuda.is_available():
                mem_after = get_gpu_memory_info()
                logger.info(f"加载后显存: {mem_after['allocated_gb']:.2f} GB")
                logger.info(f"显存增加: {mem_after['allocated_gb'] - mem_before['allocated_gb']:.2f} GB")
            
            logger.info("模型加载成功")
            return self
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            self._pipeline = None
            self._is_loaded = False
            raise RuntimeError(f"模型加载失败: {str(e)}") from e
    
    def unload(self) -> None:
        """卸载模型，释放显存"""
        if not self._is_loaded:
            return
        
        logger.info("卸载模型...")
        
        # 删除管道
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
        
        # 清理显存
        clear_gpu_cache()
        
        self._is_loaded = False
        logger.info("模型已卸载")
    
    def _ensure_loaded(self) -> None:
        """确保模型已加载"""
        if not self.is_loaded:
            self.load()
    
    def _preprocess_image(self, image: Union[str, Path, Image.Image]) -> Image.Image:
        """
        预处理输入图像
        
        Args:
            image: 图像路径或PIL图像
            
        Returns:
            预处理后的PIL图像
        """
        # 加载图像
        if isinstance(image, (str, Path)):
            pil_image = load_image(str(image))
        else:
            pil_image = image
        
        # 验证图像
        validate_image(pil_image)
        
        # 调整尺寸（保持宽高比，最大尺寸限制）
        width, height = pil_image.size
        
        if width > self.MAX_DIMENSION or height > self.MAX_DIMENSION:
            logger.warning(f"图像尺寸 {width}x{height} 超过最大值，将进行缩放")
            pil_image = resize_image(
                pil_image,
                max_size=self.MAX_DIMENSION,
                keep_aspect_ratio=True
            )
        
        # 确保尺寸是64的倍数
        width, height = pil_image.size
        new_width = (width // 64) * 64
        new_height = (height // 64) * 64
        
        if new_width != width or new_height != height:
            logger.info(f"调整图像尺寸: {width}x{height} -> {new_width}x{new_height}")
            pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
        
        return pil_image
    
    def edit_image(
        self,
        image: Union[str, Path, Image.Image],
        prompt: str,
        negative_prompt: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None,
        num_inference_steps: int = 10,
        image_guidance_scale: float = 1.5,
        guidance_scale: float = 7.5,
        num_images_per_prompt: int = 1,
        seed: Optional[int] = None,
        **kwargs
    ) -> Union[Image.Image, List[Image.Image]]:
        """
        编辑图像
        
        Args:
            image: 输入图像（路径或PIL图像）
            prompt: 编辑指令（如 "make it sunny"）
            negative_prompt: 负面提示词
            output_path: 输出路径（可选）
            num_inference_steps: 推理步数（推荐10-20）
            image_guidance_scale: 图像引导强度（1.0-2.0）
            guidance_scale: 文本引导强度（7.5-10.0）
            num_images_per_prompt: 每个提示词生成图像数量
            seed: 随机种子
            **kwargs: 额外参数
            
        Returns:
            编辑后的图像（PIL Image或列表）
            
        Raises:
            RuntimeError: 生成失败
            ValueError: 参数无效
        """
        self._ensure_loaded()
        
        if not prompt or not prompt.strip():
            raise ValueError("提示词不能为空")
        
        try:
            # 预处理图像
            logger.info("预处理输入图像...")
            input_image = self._preprocess_image(image)
            
            # 设置随机种子
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
                logger.info(f"使用随机种子: {seed}")
            
            # 记录生成前的显存状态
            if torch.cuda.is_available():
                mem_before = get_gpu_memory_info()
                logger.info(f"生成前显存: {mem_before['allocated_gb']:.2f} GB")
            
            logger.info(f"开始生成，提示词: '{prompt}'")
            logger.info(f"推理步数: {num_inference_steps}")
            logger.info(f"图像引导强度: {image_guidance_scale}")
            logger.info(f"文本引导强度: {guidance_scale}")
            
            # 生成图像
            with torch.inference_mode():
                result = self._pipeline(
                    prompt=prompt,
                    image=input_image,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    image_guidance_scale=image_guidance_scale,
                    guidance_scale=guidance_scale,
                    num_images_per_prompt=num_images_per_prompt,
                    generator=generator,
                    **kwargs
                )
            
            # 记录生成后的显存状态
            if torch.cuda.is_available():
                mem_after = get_gpu_memory_info()
                logger.info(f"生成后显存: {mem_after['allocated_gb']:.2f} GB")
            
            # 获取生成的图像
            output_images = result.images
            
            # 保存输出（如果指定了路径）
            if output_path is not None:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                if len(output_images) == 1:
                    save_image(output_images[0], str(output_path))
                    logger.info(f"图像已保存: {output_path}")
                else:
                    for i, img in enumerate(output_images):
                        save_path = output_path.parent / f"{output_path.stem}_{i}{output_path.suffix}"
                        save_image(img, str(save_path))
                        logger.info(f"图像已保存: {save_path}")
            
            # 返回结果
            if len(output_images) == 1:
                return output_images[0]
            return output_images
            
        except Exception as e:
            logger.error(f"图像生成失败: {str(e)}")
            raise RuntimeError(f"图像生成失败: {str(e)}") from e
    
    def batch_edit(
        self,
        images: List[Union[str, Path, Image.Image]],
        prompt: str,
        **kwargs
    ) -> List[Image.Image]:
        """
        批量编辑图像
        
        Args:
            images: 输入图像列表
            prompt: 编辑指令
            **kwargs: 其他参数传递给 edit_image
            
        Returns:
            编辑后的图像列表
        """
        results = []
        
        for i, image in enumerate(images):
            logger.info(f"处理图像 {i+1}/{len(images)}")
            
            try:
                result = self.edit_image(image, prompt, **kwargs)
                
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"处理图像 {i+1} 失败: {str(e)}")
                raise
        
        return results
    
    def generate(
        self,
        **kwargs
    ) -> Union[Image.Image, List[Image.Image]]:
        """
        通用生成接口（兼容ModelManager）
        
        参数同 edit_image
        
        Returns:
            生成的图像
        """
        return self.edit_image(**kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        info = {
            "model_id": self.model_id,
            "model_type": "InstructPix2Pix",
            "device": self.device,
            "torch_dtype": str(self.torch_dtype),
            "enable_cpu_offload": self.enable_cpu_offload,
            "is_loaded": self.is_loaded,
            "recommended_settings": {
                "num_inference_steps": "10-20",
                "image_guidance_scale": "1.0-2.0",
                "guidance_scale": "7.5-10.0",
            }
        }
        
        if torch.cuda.is_available():
            mem_info = get_gpu_memory_info()
            info["gpu_memory"] = mem_info
        
        return info


# 便捷函数
def create_instruct_pix2pix_pipeline(
    model_id: str = "timbrooks/instruct-pix2pix",
    device: str = "cuda",
    enable_cpu_offload: bool = True,
    cache_dir: Optional[str] = None
) -> InstructPix2PixPipeline:
    """
    创建InstructPix2Pix管道的便捷函数
    
    Args:
        model_id: 模型ID
        device: 设备
        enable_cpu_offload: 是否启用CPU offload
        cache_dir: 缓存目录
        
    Returns:
        InstructPix2PixPipeline实例
    """
    from ..model_manager import ModelConfig, ModelType
    
    config = ModelConfig(
        model_id=model_id,
        model_type=ModelType.INSTRUCT_PIX2PIX,
        torch_dtype=torch.float16,
        device=device,
        enable_cpu_offload=enable_cpu_offload,
        cache_dir=cache_dir
    )
    
    pipeline = InstructPix2PixPipeline(config)
    pipeline.load()
    
    return pipeline
