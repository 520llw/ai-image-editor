# AI图像编辑模型集成

基于Diffusers的InstructPix2Pix模型后端集成，支持文本指令驱动的图像编辑。

## 特性

- **模型**: InstructPix2Pix (timbrooks/instruct-pix2pix)
- **显存优化**: FP16 + CPU Offload，适合12GB显存
- **架构**: 单例模式模型管理器，支持懒加载和缓存
- **显存需求**: 6-8GB (FP16)，峰值约10GB

## 目录结构

```
ai_models/
├── __init__.py                    # 包初始化
├── model_manager.py               # 模型管理器（单例模式）
├── pipelines/
│   ├── __init__.py
│   └── instruct_pix2pix_pipeline.py  # InstructPix2Pix管道
├── utils/
│   ├── __init__.py
│   ├── memory_utils.py            # 显存管理工具
│   └── image_utils.py             # 图像处理工具
├── example_usage.py               # 使用示例
├── test_imports.py                # 导入测试
├── requirements.txt               # 依赖列表
└── README.md                      # 本文档
```

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 可选：安装xformers加速（Linux）
pip install xformers
```

## 快速开始

### 基础使用

```python
import torch
from ai_models import ModelManager, ModelConfig, ModelType, get_model_manager

# 获取模型管理器
manager = get_model_manager()

# 配置模型
config = ModelConfig(
    model_id="timbrooks/instruct-pix2pix",
    model_type=ModelType.INSTRUCT_PIX2PIX,
    torch_dtype=torch.float16,
    device="cuda",
    enable_cpu_offload=True,  # 关键优化
)

# 加载模型
pipeline = manager.load_model(config)

# 编辑图像
result = manager.generate(
    model_type=ModelType.INSTRUCT_PIX2PIX,
    image="input.jpg",
    prompt="make it sunny",
    output_path="output.jpg",
    num_inference_steps=10,
)
```

### 直接使用管道

```python
from ai_models.pipelines.instruct_pix2pix_pipeline import create_instruct_pix2pix_pipeline

# 创建管道
pipeline = create_instruct_pix2pix_pipeline()

# 编辑图像
result = pipeline.edit_image(
    image="input.jpg",
    prompt="turn it into a painting",
    output_path="output.jpg",
    num_inference_steps=15,
    seed=42,
)
```

## 显存优化配置

```python
pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    "timbrooks/instruct-pix2pix",
    torch_dtype=torch.float16,
    safety_checker=None
)
pipe.enable_model_cpu_offload()  # 关键优化
```

## 支持的编辑指令

```python
prompts = [
    "make it snowy",                    # 让它下雪
    "turn it into a painting",          # 变成油画风格
    "make it look like a cartoon",      # 卡通风格
    "add sunset lighting",              # 添加日落光线
    "make it night time",               # 变成夜晚
    "add fireworks to the sky",         # 天空添加烟花
    "turn him into a cyborg",           # 变成赛博格
    "make it look like a watercolor",   # 水彩画风格
    "add fog to the scene",             # 添加雾气
    "make it look vintage",             # 复古风格
]
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `num_inference_steps` | int | 10 | 推理步数（10-20） |
| `image_guidance_scale` | float | 1.5 | 图像引导强度（1.0-2.0） |
| `guidance_scale` | float | 7.5 | 文本引导强度（7.5-10.0） |
| `seed` | int | None | 随机种子 |

## API集成示例

```python
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse

app = FastAPI()
manager = get_model_manager()

@app.post("/edit-image")
async def edit_image(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    # 保存上传文件
    input_path = save_upload_file(file)
    
    # 编辑图像
    result = manager.generate(
        model_type=ModelType.INSTRUCT_PIX2PIX,
        image=input_path,
        prompt=prompt,
        output_path="output.jpg",
    )
    
    return FileResponse("output.jpg")
```

## 显存监控

```python
from ai_models.utils.memory_utils import (
    get_gpu_memory_info,
    print_memory_stats,
    clear_gpu_cache,
    MemoryMonitor,
)

# 打印显存统计
print_memory_stats()

# 使用上下文管理器
with MemoryMonitor("模型加载"):
    pipeline.load()

# 清理缓存
clear_gpu_cache()
```

## 测试

```bash
# 测试导入
python test_imports.py

# 运行示例
python example_usage.py
```

## 系统要求

- Python 3.8+
- PyTorch 2.1+
- CUDA 11.8+ (推荐)
- 显存: 12GB (推荐)

## 许可证

MIT License
