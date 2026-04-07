"""
图像处理工具模块

提供图像加载、保存、格式转换和预处理功能

作者: AI Assistant
"""

import logging
from typing import Union, Tuple, Optional, List
from pathlib import Path
from io import BytesIO
import base64

import torch
import numpy as np
from PIL import Image, ImageOps, ImageFilter

logger = logging.getLogger(__name__)


# 支持的图像格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}

# 默认图像尺寸
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
MAX_IMAGE_SIZE = 2048


def load_image(
    image_path: Union[str, Path],
    convert_mode: str = "RGB"
) -> Image.Image:
    """
    加载图像文件
    
    Args:
        image_path: 图像文件路径
        convert_mode: 转换模式（"RGB", "RGBA", "L"等）
        
    Returns:
        PIL Image对象
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 格式不支持或加载失败
    """
    image_path = Path(image_path)
    
    # 检查文件是否存在
    if not image_path.exists():
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    # 检查格式
    if image_path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"不支持的图像格式: {image_path.suffix}. "
            f"支持的格式: {SUPPORTED_FORMATS}"
        )
    
    try:
        # 加载图像
        image = Image.open(image_path)
        
        # 转换模式
        if convert_mode and image.mode != convert_mode:
            image = image.convert(convert_mode)
        
        logger.info(f"图像加载成功: {image_path}, 尺寸: {image.size}, 模式: {image.mode}")
        return image
        
    except Exception as e:
        raise ValueError(f"图像加载失败: {image_path}, 错误: {str(e)}") from e


def save_image(
    image: Image.Image,
    output_path: Union[str, Path],
    quality: int = 95,
    optimize: bool = True
) -> Path:
    """
    保存图像文件
    
    Args:
        image: PIL Image对象
        output_path: 输出路径
        quality: JPEG质量（1-100）
        optimize: 是否优化
        
    Returns:
        保存的文件路径
        
    Raises:
        ValueError: 保存失败
    """
    output_path = Path(output_path)
    
    # 创建输出目录
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # 保存参数
        save_kwargs = {"optimize": optimize}
        
        # JPEG格式使用质量参数
        if output_path.suffix.lower() in {'.jpg', '.jpeg'}:
            save_kwargs["quality"] = quality
            # JPEG不支持RGBA
            if image.mode == 'RGBA':
                image = image.convert('RGB')
        
        # PNG格式使用压缩
        elif output_path.suffix.lower() == '.png':
            save_kwargs["compress_level"] = 6
        
        image.save(output_path, **save_kwargs)
        logger.info(f"图像已保存: {output_path}")
        
        return output_path
        
    except Exception as e:
        raise ValueError(f"图像保存失败: {output_path}, 错误: {str(e)}") from e


def load_image_from_base64(
    base64_string: str,
    convert_mode: str = "RGB"
) -> Image.Image:
    """
    从Base64字符串加载图像
    
    Args:
        base64_string: Base64编码的图像数据
        convert_mode: 转换模式
        
    Returns:
        PIL Image对象
    """
    try:
        # 解码Base64
        image_data = base64.b64decode(base64_string)
        
        # 加载图像
        image = Image.open(BytesIO(image_data))
        
        # 转换模式
        if convert_mode and image.mode != convert_mode:
            image = image.convert(convert_mode)
        
        return image
        
    except Exception as e:
        raise ValueError(f"Base64图像加载失败: {str(e)}") from e


def image_to_base64(
    image: Image.Image,
    format: str = "PNG"
) -> str:
    """
    将图像转换为Base64字符串
    
    Args:
        image: PIL Image对象
        format: 输出格式
        
    Returns:
        Base64编码的字符串
    """
    try:
        buffer = BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        
        base64_string = base64.b64encode(buffer.read()).decode('utf-8')
        return base64_string
        
    except Exception as e:
        raise ValueError(f"图像转Base64失败: {str(e)}") from e


def pil_to_tensor(
    image: Image.Image,
    normalize: bool = True,
    device: str = "cpu"
) -> torch.Tensor:
    """
    将PIL图像转换为PyTorch张量
    
    Args:
        image: PIL Image对象
        normalize: 是否归一化到[0, 1]
        device: 目标设备
        
    Returns:
        PyTorch张量 (C, H, W) 或 (B, C, H, W)
    """
    # 转换为numpy数组
    np_image = np.array(image)
    
    # 转换为张量 (H, W, C) -> (C, H, W)
    tensor = torch.from_numpy(np_image).permute(2, 0, 1).float()
    
    # 归一化
    if normalize:
        tensor = tensor / 255.0
    
    # 移动到设备
    tensor = tensor.to(device)
    
    return tensor


def tensor_to_pil(
    tensor: torch.Tensor,
    denormalize: bool = True
) -> Image.Image:
    """
    将PyTorch张量转换为PIL图像
    
    Args:
        tensor: PyTorch张量 (C, H, W) 或 (B, C, H, W)
        denormalize: 是否从[0, 1]反归一化
        
    Returns:
        PIL Image对象
    """
    # 处理批次维度
    if tensor.dim() == 4:
        # (B, C, H, W) -> 取第一张
        tensor = tensor[0]
    
    # 确保在CPU上
    tensor = tensor.cpu().detach()
    
    # 反归一化
    if denormalize:
        tensor = torch.clamp(tensor, 0, 1)
        tensor = (tensor * 255).byte()
    else:
        tensor = tensor.byte()
    
    # 转换维度 (C, H, W) -> (H, W, C)
    np_image = tensor.permute(1, 2, 0).numpy()
    
    # 创建PIL图像
    image = Image.fromarray(np_image)
    
    return image


def resize_image(
    image: Image.Image,
    width: Optional[int] = None,
    height: Optional[int] = None,
    max_size: Optional[int] = None,
    keep_aspect_ratio: bool = True,
    resample: int = Image.LANCZOS
) -> Image.Image:
    """
    调整图像尺寸
    
    Args:
        image: PIL Image对象
        width: 目标宽度
        height: 目标高度
        max_size: 最大尺寸（优先级最高）
        keep_aspect_ratio: 是否保持宽高比
        resample: 重采样方法
        
    Returns:
        调整后的PIL Image对象
    """
    orig_width, orig_height = image.size
    
    # 如果指定了最大尺寸，按比例缩放
    if max_size is not None:
        if orig_width > orig_height:
            width = max_size
            height = int(orig_height * max_size / orig_width)
        else:
            height = max_size
            width = int(orig_width * max_size / orig_height)
    
    # 如果没有指定尺寸，使用默认值
    if width is None and height is None:
        width = DEFAULT_WIDTH
        height = DEFAULT_HEIGHT
    elif width is None:
        width = int(orig_width * height / orig_height)
    elif height is None:
        height = int(orig_height * width / orig_width)
    
    # 保持宽高比
    if keep_aspect_ratio and (width != orig_width or height != orig_height):
        ratio = min(width / orig_width, height / orig_height)
        width = int(orig_width * ratio)
        height = int(orig_height * ratio)
    
    # 确保尺寸有效
    width = max(1, min(width, MAX_IMAGE_SIZE))
    height = max(1, min(height, MAX_IMAGE_SIZE))
    
    # 调整尺寸
    if (width, height) != (orig_width, orig_height):
        image = image.resize((width, height), resample)
        logger.info(f"图像尺寸调整: {orig_width}x{orig_height} -> {width}x{height}")
    
    return image


def center_crop(
    image: Image.Image,
    width: int,
    height: int
) -> Image.Image:
    """
    中心裁剪图像
    
    Args:
        image: PIL Image对象
        width: 目标宽度
        height: 目标高度
        
    Returns:
        裁剪后的PIL Image对象
    """
    orig_width, orig_height = image.size
    
    # 计算裁剪区域
    left = (orig_width - width) // 2
    top = (orig_height - height) // 2
    right = left + width
    bottom = top + height
    
    # 裁剪
    image = image.crop((left, top, right, bottom))
    
    return image


def validate_image(
    image: Image.Image,
    min_size: Tuple[int, int] = (64, 64),
    max_size: Tuple[int, int] = (MAX_IMAGE_SIZE, MAX_IMAGE_SIZE),
    allowed_modes: Optional[List[str]] = None
) -> bool:
    """
    验证图像是否有效
    
    Args:
        image: PIL Image对象
        min_size: 最小尺寸
        max_size: 最大尺寸
        allowed_modes: 允许的图像模式列表
        
    Returns:
        是否有效
        
    Raises:
        ValueError: 图像无效
    """
    if allowed_modes is None:
        allowed_modes = ["RGB", "RGBA", "L"]
    
    width, height = image.size
    
    # 检查尺寸
    if width < min_size[0] or height < min_size[1]:
        raise ValueError(
            f"图像尺寸过小: {width}x{height}, "
            f"最小要求: {min_size[0]}x{min_size[1]}"
        )
    
    if width > max_size[0] or height > max_size[1]:
        raise ValueError(
            f"图像尺寸过大: {width}x{height}, "
            f"最大允许: {max_size[0]}x{max_size[1]}"
        )
    
    # 检查模式
    if image.mode not in allowed_modes:
        raise ValueError(
            f"不支持的图像模式: {image.mode}, "
            f"支持的模式: {allowed_modes}"
        )
    
    return True


def normalize_image_size(
    image: Image.Image,
    target_width: int = 512,
    target_height: int = 512,
    multiple_of: int = 64
) -> Image.Image:
    """
    标准化图像尺寸（用于扩散模型）
    
    扩散模型通常要求图像尺寸是64的倍数
    
    Args:
        image: PIL Image对象
        target_width: 目标宽度
        target_height: 目标高度
        multiple_of: 尺寸必须是该值的倍数
        
    Returns:
        标准化后的PIL Image对象
    """
    width, height = image.size
    
    # 计算目标尺寸（保持64的倍数）
    new_width = (target_width // multiple_of) * multiple_of
    new_height = (target_height // multiple_of) * multiple_of
    
    # 如果当前尺寸已经是目标尺寸，直接返回
    if width == new_width and height == new_height:
        return image
    
    # 调整尺寸
    image = image.resize((new_width, new_height), Image.LANCZOS)
    logger.info(f"图像尺寸标准化: {width}x{height} -> {new_width}x{new_height}")
    
    return image


def apply_image_filter(
    image: Image.Image,
    filter_type: str,
    **kwargs
) -> Image.Image:
    """
    应用图像滤镜
    
    Args:
        image: PIL Image对象
        filter_type: 滤镜类型
        **kwargs: 滤镜参数
        
    Returns:
        处理后的PIL Image对象
    """
    if filter_type == "blur":
        radius = kwargs.get("radius", 2)
        return image.filter(ImageFilter.GaussianBlur(radius))
    
    elif filter_type == "sharpen":
        return image.filter(ImageFilter.SHARPEN)
    
    elif filter_type == "edge_enhance":
        return image.filter(ImageFilter.EDGE_ENHANCE)
    
    elif filter_type == "contour":
        return image.filter(ImageFilter.CONTOUR)
    
    elif filter_type == "grayscale":
        return image.convert("L").convert("RGB")
    
    else:
        raise ValueError(f"未知的滤镜类型: {filter_type}")


def create_image_grid(
    images: List[Image.Image],
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    padding: int = 2,
    background_color: Tuple[int, int, int] = (255, 255, 255)
) -> Image.Image:
    """
    创建图像网格
    
    Args:
        images: PIL Image对象列表
        rows: 行数
        cols: 列数
        padding: 间距
        background_color: 背景颜色
        
    Returns:
        网格图像
    """
    if not images:
        raise ValueError("图像列表为空")
    
    n_images = len(images)
    
    # 自动计算行列数
    if rows is None and cols is None:
        cols = int(np.ceil(np.sqrt(n_images)))
        rows = int(np.ceil(n_images / cols))
    elif rows is None:
        rows = int(np.ceil(n_images / cols))
    elif cols is None:
        cols = int(np.ceil(n_images / rows))
    
    # 获取单张图像尺寸
    img_width, img_height = images[0].size
    
    # 计算网格尺寸
    grid_width = cols * img_width + (cols + 1) * padding
    grid_height = rows * img_height + (rows + 1) * padding
    
    # 创建背景
    grid = Image.new("RGB", (grid_width, grid_height), background_color)
    
    # 粘贴图像
    for idx, image in enumerate(images):
        if idx >= rows * cols:
            break
        
        row = idx // cols
        col = idx % cols
        
        x = col * img_width + (col + 1) * padding
        y = row * img_height + (row + 1) * padding
        
        # 确保图像是RGB模式
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        grid.paste(image, (x, y))
    
    return grid


def get_image_info(image: Image.Image) -> dict:
    """
    获取图像信息
    
    Args:
        image: PIL Image对象
        
    Returns:
        图像信息字典
    """
    return {
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "format": image.format if hasattr(image, 'format') else None,
        "size_bytes": len(image.tobytes()) if hasattr(image, 'tobytes') else None,
    }


def duplicate_image(image: Image.Image) -> Image.Image:
    """
    复制图像
    
    Args:
        image: PIL Image对象
        
    Returns:
        复制的PIL Image对象
    """
    return image.copy()


# 便捷函数
def load_and_preprocess(
    image_path: Union[str, Path],
    target_width: int = 512,
    target_height: int = 512,
    convert_mode: str = "RGB"
) -> Image.Image:
    """
    加载并预处理图像
    
    Args:
        image_path: 图像路径
        target_width: 目标宽度
        target_height: 目标高度
        convert_mode: 转换模式
        
    Returns:
        预处理后的PIL Image对象
    """
    # 加载图像
    image = load_image(image_path, convert_mode)
    
    # 验证图像
    validate_image(image)
    
    # 标准化尺寸
    image = normalize_image_size(image, target_width, target_height)
    
    return image
