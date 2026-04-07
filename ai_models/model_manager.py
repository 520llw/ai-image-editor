"""
模型管理器模块

提供单例模式的模型管理，支持：
- 懒加载模型
- 显存管理
- 模型缓存
- 多模型切换

作者: AI Assistant
"""

import threading
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

import torch

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """支持的模型类型"""
    INSTRUCT_PIX2PIX = "instruct_pix2pix"
    # 未来可扩展更多模型
    # STABLE_DIFFUSION = "stable_diffusion"
    # CONTROLNET = "controlnet"


@dataclass
class ModelConfig:
    """模型配置数据类"""
    model_id: str
    model_type: ModelType
    torch_dtype: torch.dtype = torch.float16
    device: str = "cuda"
    enable_cpu_offload: bool = True
    safety_checker: Optional[Any] = None
    cache_dir: Optional[str] = None
    custom_kwargs: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_kwargs is None:
            self.custom_kwargs = {}


class ModelManager:
    """
    模型管理器（单例模式）
    
    管理所有AI模型的加载、缓存和显存优化
    
    Usage:
        >>> manager = ModelManager()
        >>> manager.load_model(ModelConfig(...))
        >>> result = manager.generate(...)
    """
    
    _instance: Optional['ModelManager'] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls) -> 'ModelManager':
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化模型管理器"""
        if self._initialized:
            return
            
        self._initialized = True
        self._models: Dict[ModelType, Any] = {}
        self._configs: Dict[ModelType, ModelConfig] = {}
        self._model_locks: Dict[ModelType, threading.Lock] = {}
        self._global_lock = threading.Lock()
        
        # 检查CUDA可用性
        self._cuda_available = torch.cuda.is_available()
        self._device = "cuda" if self._cuda_available else "cpu"
        
        if self._cuda_available:
            logger.info(f"CUDA可用，使用设备: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA版本: {torch.version.cuda}")
        else:
            logger.warning("CUDA不可用，将使用CPU运行（性能会显著降低）")
        
        logger.info("ModelManager初始化完成")
    
    @property
    def device(self) -> str:
        """获取当前设备"""
        return self._device
    
    @property
    def cuda_available(self) -> bool:
        """检查CUDA是否可用"""
        return self._cuda_available
    
    def _get_model_lock(self, model_type: ModelType) -> threading.Lock:
        """获取模型专用的锁"""
        if model_type not in self._model_locks:
            with self._global_lock:
                if model_type not in self._model_locks:
                    self._model_locks[model_type] = threading.Lock()
        return self._model_locks[model_type]
    
    def load_model(self, config: ModelConfig) -> Any:
        """
        加载模型
        
        Args:
            config: 模型配置
            
        Returns:
            加载的模型管道
            
        Raises:
            RuntimeError: 模型加载失败
        """
        model_type = config.model_type
        
        with self._get_model_lock(model_type):
            # 检查是否已缓存
            if model_type in self._models:
                logger.info(f"模型 {model_type.value} 已缓存，直接返回")
                return self._models[model_type]
            
            logger.info(f"开始加载模型: {config.model_id}")
            
            try:
                # 根据模型类型加载对应的管道
                if model_type == ModelType.INSTRUCT_PIX2PIX:
                    from .pipelines.instruct_pix2pix_pipeline import InstructPix2PixPipeline
                    pipeline = InstructPix2PixPipeline(config)
                else:
                    raise ValueError(f"不支持的模型类型: {model_type.value}")
                
                # 缓存模型
                self._models[model_type] = pipeline
                self._configs[model_type] = config
                
                logger.info(f"模型 {model_type.value} 加载成功")
                return pipeline
                
            except Exception as e:
                logger.error(f"模型 {model_type.value} 加载失败: {str(e)}")
                raise RuntimeError(f"模型加载失败: {str(e)}") from e
    
    def get_model(self, model_type: ModelType) -> Optional[Any]:
        """
        获取已加载的模型
        
        Args:
            model_type: 模型类型
            
        Returns:
            模型管道，如果未加载则返回None
        """
        return self._models.get(model_type)
    
    def is_model_loaded(self, model_type: ModelType) -> bool:
        """检查模型是否已加载"""
        return model_type in self._models
    
    def unload_model(self, model_type: ModelType) -> bool:
        """
        卸载指定模型，释放显存
        
        Args:
            model_type: 要卸载的模型类型
            
        Returns:
            是否成功卸载
        """
        with self._get_model_lock(model_type):
            if model_type not in self._models:
                logger.warning(f"模型 {model_type.value} 未加载，无需卸载")
                return False
            
            try:
                logger.info(f"卸载模型: {model_type.value}")
                
                # 删除模型
                del self._models[model_type]
                
                # 清理CUDA缓存
                if self._cuda_available:
                    torch.cuda.empty_cache()
                    logger.info("CUDA缓存已清理")
                
                return True
                
            except Exception as e:
                logger.error(f"卸载模型 {model_type.value} 失败: {str(e)}")
                return False
    
    def unload_all_models(self) -> None:
        """卸载所有模型，释放所有显存"""
        with self._global_lock:
            logger.info("开始卸载所有模型...")
            
            for model_type in list(self._models.keys()):
                self.unload_model(model_type)
            
            self._models.clear()
            self._configs.clear()
            
            # 强制垃圾回收
            import gc
            gc.collect()
            
            if self._cuda_available:
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            logger.info("所有模型已卸载，显存已释放")
    
    def generate(
        self,
        model_type: ModelType,
        **kwargs
    ) -> Any:
        """
        使用指定模型生成内容
        
        Args:
            model_type: 模型类型
            **kwargs: 生成参数
            
        Returns:
            生成结果
            
        Raises:
            RuntimeError: 模型未加载或生成失败
        """
        pipeline = self.get_model(model_type)
        
        if pipeline is None:
            raise RuntimeError(
                f"模型 {model_type.value} 未加载，请先调用 load_model()"
            )
        
        with self._get_model_lock(model_type):
            try:
                return pipeline.generate(**kwargs)
            except Exception as e:
                logger.error(f"生成失败: {str(e)}")
                raise RuntimeError(f"生成失败: {str(e)}") from e
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取显存使用统计
        
        Returns:
            显存统计信息字典
        """
        stats = {
            "cuda_available": self._cuda_available,
            "device": self._device,
            "loaded_models": list(self._models.keys()),
        }
        
        if self._cuda_available:
            stats.update({
                "allocated_gb": torch.cuda.memory_allocated() / 1e9,
                "reserved_gb": torch.cuda.memory_reserved() / 1e9,
                "max_allocated_gb": torch.cuda.max_memory_allocated() / 1e9,
                "total_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
            })
        
        return stats
    
    def print_memory_stats(self) -> None:
        """打印显存使用统计"""
        stats = self.get_memory_stats()
        
        print("=" * 50)
        print("显存使用统计:")
        print("=" * 50)
        print(f"CUDA可用: {stats['cuda_available']}")
        print(f"设备: {stats['device']}")
        print(f"已加载模型: {[m.value for m in stats['loaded_models']]}")
        
        if self._cuda_available:
            print(f"已分配显存: {stats['allocated_gb']:.2f} GB")
            print(f"预留显存: {stats['reserved_gb']:.2f} GB")
            print(f"最大分配显存: {stats['max_allocated_gb']:.2f} GB")
            print(f"总显存: {stats['total_gb']:.2f} GB")
        
        print("=" * 50)


# 全局模型管理器实例
_model_manager_instance: Optional[ModelManager] = None
_model_manager_lock = threading.Lock()


def get_model_manager() -> ModelManager:
    """
    获取全局模型管理器实例
    
    Returns:
        ModelManager单例实例
    """
    global _model_manager_instance
    
    if _model_manager_instance is None:
        with _model_manager_lock:
            if _model_manager_instance is None:
                _model_manager_instance = ModelManager()
    
    return _model_manager_instance


def reset_model_manager() -> None:
    """重置模型管理器（主要用于测试）"""
    global _model_manager_instance
    
    with _model_manager_lock:
        if _model_manager_instance is not None:
            _model_manager_instance.unload_all_models()
            _model_manager_instance = None
        
        # 重置类级别的单例
        ModelManager._instance = None
