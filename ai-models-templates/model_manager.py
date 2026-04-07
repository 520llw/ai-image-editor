# ai_models/model_manager.py
import torch
import gc
from typing import Dict, Optional, Type, Any
from pathlib import Path
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """
    AI模型管理器 - 单例模式
    
    功能：
    1. 统一管理模型加载和卸载
    2. 显存管理和优化
    3. 模型缓存策略
    4. 支持多种模型类型
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        if self._initialized:
            return
        
        self._models: Dict[str, Any] = {}
        self._model_configs: Dict[str, dict] = {}
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 加载配置
        if config_path:
            self._load_config(config_path)
        
        self._initialized = True
        logger.info(f"ModelManager初始化完成，设备: {self._device}")
    
    def _load_config(self, config_path: str):
        """加载模型配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self._model_configs = config.get('models', {})
                logger.info(f"加载了 {len(self._model_configs)} 个模型配置")
        except Exception as e:
            logger.warning(f"配置文件加载失败: {e}")
    
    def register_model(self, name: str, model_class: Type, **kwargs):
        """
        注册模型
        
        Args:
            name: 模型名称
            model_class: 模型类
            **kwargs: 模型初始化参数
        """
        if name in self._model_configs:
            logger.warning(f"模型 {name} 已存在，将覆盖")
        
        self._model_configs[name] = {
            'class': model_class,
            'params': kwargs,
            'loaded': False
        }
        logger.info(f"模型 {name} 已注册")
    
    def load_model(self, name: str, force_reload: bool = False) -> Any:
        """
        加载模型
        
        Args:
            name: 模型名称
            force_reload: 是否强制重新加载
            
        Returns:
            加载的模型实例
        """
        # 检查是否已加载
        if name in self._models and not force_reload:
            logger.info(f"模型 {name} 已加载，返回缓存实例")
            return self._models[name]
        
        # 检查配置是否存在
        if name not in self._model_configs:
            raise ValueError(f"模型 {name} 未注册")
        
        config = self._model_configs[name]
        model_class = config.get('class')
        
        if model_class is None:
            raise ValueError(f"模型 {name} 配置缺少class定义")
        
        # 卸载其他模型以释放显存（如果显存不足）
        if self._device == "cuda":
            self._manage_memory()
        
        logger.info(f"正在加载模型: {name}")
        
        try:
            # 实例化模型
            if isinstance(model_class, type):
                model = model_class(**config.get('params', {}))
            else:
                # 假设是已加载的pipeline
                model = model_class
            
            self._models[name] = model
            config['loaded'] = True
            
            logger.info(f"模型 {name} 加载完成")
            
            # 打印显存使用情况
            if self._device == "cuda":
                self._log_memory_usage()
            
            return model
            
        except Exception as e:
            logger.error(f"模型 {name} 加载失败: {e}")
            raise
    
    def unload_model(self, name: str):
        """
        卸载模型
        
        Args:
            name: 模型名称
        """
        if name not in self._models:
            logger.warning(f"模型 {name} 未加载")
            return
        
        logger.info(f"正在卸载模型: {name}")
        
        try:
            del self._models[name]
            
            if name in self._model_configs:
                self._model_configs[name]['loaded'] = False
            
            # 清理显存
            if self._device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()
            
            logger.info(f"模型 {name} 已卸载")
            
        except Exception as e:
            logger.error(f"模型 {name} 卸载失败: {e}")
    
    def get_model(self, name: str) -> Optional[Any]:
        """
        获取已加载的模型
        
        Args:
            name: 模型名称
            
        Returns:
            模型实例或None
        """
        return self._models.get(name)
    
    def is_loaded(self, name: str) -> bool:
        """检查模型是否已加载"""
        return name in self._models
    
    def list_models(self) -> Dict[str, bool]:
        """
        列出所有模型及其加载状态
        
        Returns:
            {模型名: 是否已加载}
        """
        return {
            name: config.get('loaded', False)
            for name, config in self._model_configs.items()
        }
    
    def clear_cache(self):
        """清理所有模型缓存"""
        logger.info("清理所有模型缓存")
        
        for name in list(self._models.keys()):
            self.unload_model(name)
        
        if self._device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()
        
        logger.info("模型缓存已清理")
    
    def _manage_memory(self):
        """管理显存，必要时卸载其他模型"""
        if not torch.cuda.is_available():
            return
        
        # 获取当前显存使用情况
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        
        logger.debug(f"显存使用: 已分配={allocated:.2f}GB, 已预留={reserved:.2f}GB")
        
        # 如果显存使用超过阈值，卸载其他模型
        memory_threshold = 6.0  # GB
        
        if allocated > memory_threshold and len(self._models) > 0:
            logger.info("显存不足，卸载其他模型")
            # 保留最后使用的模型，卸载其他
            models_to_unload = list(self._models.keys())[:-1]
            for name in models_to_unload:
                self.unload_model(name)
    
    def _log_memory_usage(self):
        """打印显存使用情况"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            max_allocated = torch.cuda.max_memory_allocated() / 1e9
            
            logger.info(
                f"显存使用: "
                f"已分配={allocated:.2f}GB, "
                f"已预留={reserved:.2f}GB, "
                f"峰值={max_allocated:.2f}GB"
            )
    
    def get_memory_info(self) -> Dict[str, float]:
        """获取显存信息"""
        if torch.cuda.is_available():
            return {
                'allocated_gb': torch.cuda.memory_allocated() / 1e9,
                'reserved_gb': torch.cuda.memory_reserved() / 1e9,
                'max_allocated_gb': torch.cuda.max_memory_allocated() / 1e9,
                'total_gb': torch.cuda.get_device_properties(0).total_memory / 1e9,
            }
        return {'device': 'cpu'}
    
    def optimize_memory(self):
        """执行内存优化"""
        if not torch.cuda.is_available():
            return
        
        logger.info("执行内存优化")
        
        # 清理缓存
        torch.cuda.empty_cache()
        gc.collect()
        
        # 启用内存优化（需要在模型加载前调用）
        torch.backends.cudnn.benchmark = True
        
        self._log_memory_usage()


# 全局模型管理器实例
_model_manager = None

def get_model_manager(config_path: Optional[str] = None) -> ModelManager:
    """获取模型管理器单例"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager(config_path)
    return _model_manager
