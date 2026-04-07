"""
显存管理工具模块

提供GPU显存监控、清理和优化功能
适合12GB显存环境使用

作者: AI Assistant
"""

import logging
import gc
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

import torch

logger = logging.getLogger(__name__)


@dataclass
class GPUMemoryInfo:
    """GPU显存信息数据类"""
    allocated_bytes: int
    reserved_bytes: int
    max_allocated_bytes: int
    total_bytes: int
    
    @property
    def allocated_gb(self) -> float:
        """已分配显存（GB）"""
        return self.allocated_bytes / (1024 ** 3)
    
    @property
    def reserved_gb(self) -> float:
        """预留显存（GB）"""
        return self.reserved_bytes / (1024 ** 3)
    
    @property
    def max_allocated_gb(self) -> float:
        """最大已分配显存（GB）"""
        return self.max_allocated_bytes / (1024 ** 3)
    
    @property
    def total_gb(self) -> float:
        """总显存（GB）"""
        return self.total_bytes / (1024 ** 3)
    
    @property
    def free_gb(self) -> float:
        """可用显存（GB）"""
        return self.total_gb - self.allocated_gb
    
    @property
    def usage_percent(self) -> float:
        """显存使用率（%）"""
        if self.total_bytes == 0:
            return 0.0
        return (self.allocated_bytes / self.total_bytes) * 100


def is_cuda_available() -> bool:
    """
    检查CUDA是否可用
    
    Returns:
        CUDA是否可用
    """
    return torch.cuda.is_available()


def get_gpu_memory_info(device: Optional[int] = None) -> GPUMemoryInfo:
    """
    获取GPU显存信息
    
    Args:
        device: GPU设备索引，None表示当前设备
        
    Returns:
        GPU显存信息
    """
    if not is_cuda_available():
        return GPUMemoryInfo(0, 0, 0, 0)
    
    if device is None:
        device = torch.cuda.current_device()
    
    # 获取显存信息
    allocated = torch.cuda.memory_allocated(device)
    reserved = torch.cuda.memory_reserved(device)
    max_allocated = torch.cuda.max_memory_allocated(device)
    total = torch.cuda.get_device_properties(device).total_memory
    
    return GPUMemoryInfo(allocated, reserved, max_allocated, total)


def get_gpu_memory_summary(device: Optional[int] = None) -> Dict[str, Any]:
    """
    获取GPU显存摘要信息
    
    Args:
        device: GPU设备索引
        
    Returns:
        显存摘要字典
    """
    if not is_cuda_available():
        return {"cuda_available": False}
    
    info = get_gpu_memory_info(device)
    
    return {
        "cuda_available": True,
        "device_name": torch.cuda.get_device_name(device),
        "device_index": device or torch.cuda.current_device(),
        "allocated_gb": round(info.allocated_gb, 2),
        "reserved_gb": round(info.reserved_gb, 2),
        "max_allocated_gb": round(info.max_allocated_gb, 2),
        "total_gb": round(info.total_gb, 2),
        "free_gb": round(info.free_gb, 2),
        "usage_percent": round(info.usage_percent, 2),
    }


def clear_gpu_cache(device: Optional[int] = None) -> None:
    """
    清理GPU缓存
    
    Args:
        device: GPU设备索引
    """
    if not is_cuda_available():
        return
    
    # 记录清理前的显存
    info_before = get_gpu_memory_info(device)
    
    # 强制垃圾回收
    gc.collect()
    
    # 清空CUDA缓存
    torch.cuda.empty_cache()
    
    # 同步（确保所有操作完成）
    torch.cuda.synchronize(device)
    
    # 记录清理后的显存
    info_after = get_gpu_memory_info(device)
    
    freed_gb = info_before.allocated_gb - info_after.allocated_gb
    
    if freed_gb > 0.01:  # 只记录有意义的清理
        logger.info(f"GPU缓存已清理，释放显存: {freed_gb:.2f} GB")


def reset_peak_memory_stats(device: Optional[int] = None) -> None:
    """
    重置峰值显存统计
    
    Args:
        device: GPU设备索引
    """
    if is_cuda_available():
        torch.cuda.reset_peak_memory_stats(device)
        logger.info("峰值显存统计已重置")


def print_memory_stats(device: Optional[int] = None, prefix: str = "") -> None:
    """
    打印显存使用统计
    
    Args:
        device: GPU设备索引
        prefix: 打印前缀
    """
    if not is_cuda_available():
        print(f"{prefix}CUDA不可用")
        return
    
    info = get_gpu_memory_info(device)
    device_name = torch.cuda.get_device_name(device)
    
    print(f"{prefix}=" * 50)
    print(f"{prefix}GPU显存统计 - {device_name}")
    print(f"{prefix}=" * 50)
    print(f"{prefix}已分配: {info.allocated_gb:.2f} GB")
    print(f"{prefix}预留:   {info.reserved_gb:.2f} GB")
    print(f"{prefix}峰值:   {info.max_allocated_gb:.2f} GB")
    print(f"{prefix}总计:   {info.total_gb:.2f} GB")
    print(f"{prefix}可用:   {info.free_gb:.2f} GB")
    print(f"{prefix}使用率: {info.usage_percent:.1f}%")
    print(f"{prefix}=" * 50)


def ensure_gpu_memory(
    required_gb: float,
    device: Optional[int] = None,
    clear_cache: bool = True
) -> bool:
    """
    确保有足够的GPU显存
    
    Args:
        required_gb: 需要的显存（GB）
        device: GPU设备索引
        clear_cache: 是否清理缓存
        
    Returns:
        是否有足够的显存
    """
    if not is_cuda_available():
        return False
    
    info = get_gpu_memory_info(device)
    
    # 检查当前可用显存
    if info.free_gb >= required_gb:
        return True
    
    # 尝试清理缓存
    if clear_cache:
        logger.warning(f"显存不足，尝试清理缓存...")
        clear_gpu_cache(device)
        
        # 重新检查
        info = get_gpu_memory_info(device)
        if info.free_gb >= required_gb:
            logger.info("缓存清理后显存充足")
            return True
    
    logger.error(
        f"显存不足！需要: {required_gb:.2f} GB, "
        f"可用: {info.free_gb:.2f} GB"
    )
    return False


def get_optimal_batch_size(
    sample_memory_gb: float,
    safety_margin_gb: float = 2.0,
    device: Optional[int] = None
) -> int:
    """
    根据显存计算最优批处理大小
    
    Args:
        sample_memory_gb: 单个样本所需显存（GB）
        safety_margin_gb: 安全边距（GB）
        device: GPU设备索引
        
    Returns:
        最优批处理大小
    """
    if not is_cuda_available():
        return 1
    
    info = get_gpu_memory_info(device)
    available_gb = info.free_gb - safety_margin_gb
    
    if available_gb <= 0:
        return 1
    
    batch_size = int(available_gb / sample_memory_gb)
    return max(1, batch_size)


def monitor_memory(
    threshold_gb: float = 10.0,
    callback: Optional[callable] = None
) -> None:
    """
    监控显存使用，超过阈值时触发回调
    
    Args:
        threshold_gb: 显存使用阈值（GB）
        callback: 超过阈值时的回调函数
    """
    if not is_cuda_available():
        return
    
    info = get_gpu_memory_info()
    
    if info.allocated_gb > threshold_gb:
        logger.warning(f"显存使用超过阈值: {info.allocated_gb:.2f} GB > {threshold_gb} GB")
        
        if callback:
            callback(info)


class MemoryMonitor:
    """
    显存监控上下文管理器
    
    Usage:
        >>> with MemoryMonitor("模型加载"):
        ...     model.load()
    """
    
    def __init__(self, operation_name: str = "操作", device: Optional[int] = None):
        self.operation_name = operation_name
        self.device = device
        self.start_info: Optional[GPUMemoryInfo] = None
    
    def __enter__(self):
        if is_cuda_available():
            self.start_info = get_gpu_memory_info(self.device)
            logger.info(
                f"开始 {self.operation_name}, "
                f"当前显存: {self.start_info.allocated_gb:.2f} GB"
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if is_cuda_available() and self.start_info:
            end_info = get_gpu_memory_info(self.device)
            delta = end_info.allocated_gb - self.start_info.allocated_gb
            
            if exc_type is None:
                logger.info(
                    f"完成 {self.operation_name}, "
                    f"显存变化: {delta:+.2f} GB, "
                    f"当前: {end_info.allocated_gb:.2f} GB"
                )
            else:
                logger.error(
                    f"{self.operation_name} 失败, "
                    f"显存变化: {delta:+.2f} GB"
                )


class GPUMemoryOptimizer:
    """
    GPU显存优化器
    
    提供显存优化策略
    """
    
    @staticmethod
    def enable_memory_efficient_attention(pipeline) -> None:
        """
        启用内存高效注意力
        
        Args:
            pipeline: Diffusers管道
        """
        try:
            pipeline.enable_xformers_memory_efficient_attention()
            logger.info("内存高效注意力已启用")
        except Exception as e:
            logger.warning(f"无法启用内存高效注意力: {e}")
    
    @staticmethod
    def enable_vae_slicing(pipeline) -> None:
        """
        启用VAE切片
        
        Args:
            pipeline: Diffusers管道
        """
        if hasattr(pipeline, 'enable_vae_slicing'):
            pipeline.enable_vae_slicing()
            logger.info("VAE切片已启用")
    
    @staticmethod
    def enable_vae_tiling(pipeline) -> None:
        """
        启用VAE分块
        
        Args:
            pipeline: Diffusers管道
        """
        if hasattr(pipeline, 'enable_vae_tiling'):
            pipeline.enable_vae_tiling()
            logger.info("VAE分块已启用")
    
    @staticmethod
    def enable_model_cpu_offload(pipeline, device: str = "cuda") -> None:
        """
        启用模型CPU offload
        
        Args:
            pipeline: Diffusers管道
            device: 目标设备
        """
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload(device)
            logger.info(f"模型CPU offload已启用，设备: {device}")
    
    @staticmethod
    def enable_sequential_cpu_offload(pipeline, device: str = "cuda") -> None:
        """
        启用顺序CPU offload（更激进的显存优化）
        
        Args:
            pipeline: Diffusers管道
            device: 目标设备
        """
        if hasattr(pipeline, 'enable_sequential_cpu_offload'):
            pipeline.enable_sequential_cpu_offload(device)
            logger.info(f"顺序CPU offload已启用，设备: {device}")
    
    @classmethod
    def apply_all_optimizations(
        cls,
        pipeline,
        device: str = "cuda",
        aggressive: bool = False
    ) -> None:
        """
        应用所有显存优化
        
        Args:
            pipeline: Diffusers管道
            device: 目标设备
            aggressive: 是否使用激进的优化（顺序CPU offload）
        """
        logger.info("应用显存优化...")
        
        # 内存高效注意力
        cls.enable_memory_efficient_attention(pipeline)
        
        # VAE优化
        cls.enable_vae_slicing(pipeline)
        cls.enable_vae_tiling(pipeline)
        
        # CPU offload
        if aggressive:
            cls.enable_sequential_cpu_offload(pipeline, device)
        else:
            cls.enable_model_cpu_offload(pipeline, device)
        
        logger.info("显存优化应用完成")


# 便捷函数
def log_memory_usage(prefix: str = "") -> None:
    """记录当前显存使用"""
    if is_cuda_available():
        info = get_gpu_memory_info()
        logger.info(
            f"{prefix}显存使用: {info.allocated_gb:.2f} GB / "
            f"{info.total_gb:.2f} GB ({info.usage_percent:.1f}%)"
        )


def get_memory_footprint() -> Dict[str, float]:
    """
    获取内存占用快照
    
    Returns:
        内存占用信息
    """
    result = {"cuda_available": is_cuda_available()}
    
    if is_cuda_available():
        info = get_gpu_memory_info()
        result.update({
            "allocated_gb": info.allocated_gb,
            "reserved_gb": info.reserved_gb,
            "total_gb": info.total_gb,
            "free_gb": info.free_gb,
        })
    
    return result
