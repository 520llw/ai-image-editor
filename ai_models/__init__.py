"""
AI Models Package - AI图像编辑模型集成

提供基于Diffusers的图像编辑模型支持：
- InstructPix2Pix: 文本指令驱动的图像编辑

作者: AI Assistant
版本: 1.0.0
"""

from .model_manager import ModelManager, get_model_manager
from .pipelines.instruct_pix2pix_pipeline import InstructPix2PixPipeline

__version__ = "1.0.0"
__all__ = [
    "ModelManager",
    "get_model_manager",
    "InstructPix2PixPipeline",
]
