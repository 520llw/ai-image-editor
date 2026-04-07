# AI批图软件完整技术架构设计

## 项目概述

一个基于AI的图片编辑Web应用，用户上传图片并输入文本提示词，AI模型根据提示词编辑图片并返回结果。

---

## 一、技术栈总览

### 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2.x | UI框架 |
| TypeScript | 5.3.x | 类型安全 |
| Vite | 5.0.x | 构建工具 |
| Tailwind CSS | 3.4.x | 样式框架 |
| shadcn/ui | 最新 | UI组件库 |
| Zustand | 4.4.x | 状态管理 |
| React Query | 5.x | 服务端状态管理 |
| Axios | 1.6.x | HTTP客户端 |

### 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 编程语言 |
| FastAPI | 0.109.x | Web框架 |
| Uvicorn | 0.27.x | ASGI服务器 |
| Pillow | 10.x | 图像处理 |
| Python-multipart | 0.0.6 | 文件上传 |
| Pydantic | 2.5.x | 数据验证 |

### AI模型技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| PyTorch | 2.1.x | 深度学习框架 |
| Transformers | 4.36.x | 预训练模型 |
| Diffusers | 0.25.x | 扩散模型 |
| Accelerate | 0.25.x | 模型加速 |
| XFormers | 0.0.23 | 内存优化 |

---

## 二、项目目录结构

```
ai-image-editor/
├── frontend/                          # 前端项目
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/                       # API接口
│   │   │   ├── client.ts              # Axios实例
│   │   │   └── imageApi.ts            # 图片相关API
│   │   ├── components/                # 组件
│   │   │   ├── ui/                    # shadcn/ui组件
│   │   │   ├── layout/                # 布局组件
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── image/                 # 图片相关组件
│   │   │   │   ├── ImageUploader.tsx  # 图片上传
│   │   │   │   ├── ImagePreview.tsx   # 图片预览
│   │   │   │   └── ImageComparison.tsx # 对比组件
│   │   │   └── editor/                # 编辑器组件
│   │   │       ├── PromptInput.tsx    # 提示词输入
│   │   │       ├── StyleSelector.tsx  # 风格选择
│   │   │       └── GenerateButton.tsx # 生成按钮
│   │   ├── hooks/                     # 自定义Hooks
│   │   │   ├── useImageUpload.ts
│   │   │   └── useImageGeneration.ts
│   │   ├── stores/                    # 状态管理
│   │   │   └── editorStore.ts
│   │   ├── types/                     # TypeScript类型
│   │   │   └── index.ts
│   │   ├── utils/                     # 工具函数
│   │   │   └── helpers.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── components.json                # shadcn配置
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                           # 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI入口
│   │   ├── config.py                  # 配置管理
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   └── image.py           # 图片API路由
│   │   │   └── dependencies.py        # 依赖注入
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # 安全相关
│   │   │   └── exceptions.py          # 异常处理
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py             # Pydantic模型
│   │   │   └── enums.py               # 枚举定义
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── image_service.py       # 图片服务
│   │   │   └── ai_service.py          # AI服务
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── file_utils.py          # 文件工具
│   ├── models/                        # AI模型目录
│   │   └── .gitkeep
│   ├── uploads/                       # 上传文件目录
│   │   └── .gitkeep
│   ├── outputs/                       # 输出文件目录
│   │   └── .gitkeep
│   ├── tests/
│   │   └── __init__.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── ai_models/                         # AI模型代码
│   ├── __init__.py
│   ├── model_manager.py               # 模型管理器
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── base_pipeline.py           # 基础管道
│   │   ├── inpainting_pipeline.py     # 图像修复
│   │   ├── img2img_pipeline.py        # 图生图
│   │   └── controlnet_pipeline.py     # ControlNet
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── memory_utils.py            # 显存管理
│   │   └── image_utils.py             # 图像处理
│   └── configs/
│       └── model_config.yaml          # 模型配置
│
├── docker-compose.yml
├── README.md
└── .env.example
```

---

## 三、前端架构详解

### 3.1 组件结构

```
src/components/
├── ui/                    # shadcn/ui 基础组件
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   ├── textarea.tsx
│   ├── slider.tsx
│   ├── select.tsx
│   └── toast.tsx
├── layout/                # 布局组件
│   ├── Header.tsx         # 顶部导航
│   ├── Footer.tsx         # 底部信息
│   └── MainLayout.tsx     # 主布局
├── image/                 # 图片相关组件
│   ├── ImageUploader.tsx  # 图片上传（拖拽+点击）
│   ├── ImagePreview.tsx   # 图片预览
│   ├── ImageComparison.tsx # 前后对比
│   └── ImageGallery.tsx   # 图片画廊
└── editor/                # 编辑器组件
    ├── PromptInput.tsx    # 提示词输入
    ├── StyleSelector.tsx  # 风格选择
    ├── StrengthSlider.tsx # 强度调节
    └── GenerateButton.tsx # 生成按钮
```

### 3.2 状态管理 (Zustand)

```typescript
// stores/editorStore.ts
interface EditorState {
  // 图片状态
  originalImage: string | null;
  generatedImage: string | null;
  isUploading: boolean;
  isGenerating: boolean;
  
  // 编辑参数
  prompt: string;
  negativePrompt: string;
  style: string;
  strength: number;
  steps: number;
  
  // Actions
  setOriginalImage: (url: string) => void;
  setGeneratedImage: (url: string) => void;
  setPrompt: (prompt: string) => void;
  generateImage: () => Promise<void>;
  reset: () => void;
}
```

### 3.3 关键Hooks

```typescript
// hooks/useImageUpload.ts
- 处理图片上传
- 文件类型验证
- 图片尺寸检查
- 预览生成

// hooks/useImageGeneration.ts
- 调用生成API
- 轮询任务状态
- 错误处理
- 进度显示
```

---

## 四、后端架构详解

### 4.1 API端点设计

```python
# POST /api/v1/images/upload
# 上传图片
Request:  multipart/form-data (file)
Response: { "image_id": "uuid", "url": "/uploads/xxx.jpg" }

# POST /api/v1/images/generate
# 生成图片
Request:  {
  "image_id": "uuid",
  "prompt": "string",
  "negative_prompt": "string",
  "style": "string",
  "strength": 0.75,
  "steps": 30
}
Response: { "task_id": "uuid", "status": "pending" }

# GET /api/v1/images/status/{task_id}
# 查询任务状态
Response: {
  "task_id": "uuid",
  "status": "processing|completed|failed",
  "progress": 50,
  "result_url": "/outputs/xxx.jpg"
}

# GET /api/v1/images/download/{image_id}
# 下载图片
Response: image binary

# DELETE /api/v1/images/{image_id}
# 删除图片
Response: { "success": true }
```

### 4.2 核心服务

```python
# services/image_service.py
class ImageService:
    - save_upload(file) -> image_id
    - get_image(image_id) -> image_path
    - delete_image(image_id)
    - validate_image(file) -> bool

# services/ai_service.py  
class AIService:
    - load_model(model_name)
    - generate_image(params) -> task_id
    - get_task_status(task_id)
    - unload_model()
```

### 4.3 异步任务处理

```python
# 使用BackgroundTasks处理生成任务
@app.post("/generate")
async def generate(
    params: GenerateParams,
    background_tasks: BackgroundTasks
):
    task_id = create_task()
    background_tasks.add_task(process_generation, task_id, params)
    return {"task_id": task_id}
```

---

## 五、AI模型集成架构

### 5.1 模型管理器

```python
# ai_models/model_manager.py
class ModelManager:
    """单例模式管理模型加载和显存"""
    
    _instance = None
    _models = {}
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def load_model(self, model_name: str, model_class):
        """懒加载模型"""
        if model_name not in self._models:
            self._models[model_name] = model_class.from_pretrained(...)
        return self._models[model_name]
    
    def unload_model(self, model_name: str):
        """卸载模型释放显存"""
        if model_name in self._models:
            del self._models[model_name]
            torch.cuda.empty_cache()
    
    def get_memory_usage(self):
        """获取显存使用情况"""
        return torch.cuda.memory_allocated() / 1024**3  # GB
```

### 5.2 管道实现

```python
# ai_models/pipelines/img2img_pipeline.py
class Img2ImgPipeline:
    """图生图管道"""
    
    def __init__(self):
        self.model_id = "runwayml/stable-diffusion-v1-5"
        self.pipe = None
    
    def load(self):
        self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            use_safetensors=True
        )
        self.pipe = self.pipe.to("cuda")
        self.pipe.enable_xformers_memory_efficient_attention()
    
    def generate(self, image, prompt, strength=0.75, steps=30):
        result = self.pipe(
            prompt=prompt,
            image=image,
            strength=strength,
            num_inference_steps=steps
        )
        return result.images[0]
```

### 5.3 显存管理策略

```python
# ai_models/utils/memory_utils.py
class MemoryManager:
    """显存管理工具"""
    
    @staticmethod
    def optimize_memory():
        """启用内存优化"""
        # 启用梯度检查点
        pipe.enable_gradient_checkpointing()
        # 启用xformers
        pipe.enable_xformers_memory_efficient_attention()
        # 启用CPU卸载
        pipe.enable_model_cpu_offload()
    
    @staticmethod
    def clear_cache():
        """清理显存缓存"""
        gc.collect()
        torch.cuda.empty_cache()
    
    @staticmethod
    def get_memory_info():
        """获取显存信息"""
        return {
            "allocated": torch.cuda.memory_allocated() / 1e9,
            "reserved": torch.cuda.memory_reserved() / 1e9,
            "max_allocated": torch.cuda.max_memory_allocated() / 1e9
        }
```

---

## 六、组件交互流程

### 6.1 图片上传流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户      │────▶│  前端上传   │────▶│  FastAPI    │────▶│  保存文件   │
│ 选择图片    │     │  组件       │     │  /upload    │     │  返回URL    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       │                   ▼                   ▼                   ▼
       │            ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
       │            │  显示预览   │◀────│  返回响应   │◀────│  存储元数据 │
       │            │  图         │     │             │     │             │
       │            └─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│  输入提示词  │
└─────────────┘
```

### 6.2 图片生成流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户      │────▶│  点击生成   │────▶│  POST       │────▶│  创建任务   │
│ 提交请求    │     │  按钮       │     │  /generate  │     │  返回task_id│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  显示结果   │◀────│  轮询状态   │◀────│  GET        │◀────│  后台任务   │
│  图片       │     │  进度条     │     │  /status    │     │  执行生成   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                                          ┌─────────────┐
                                                          │  加载模型   │
                                                          │  (懒加载)   │
                                                          └─────────────┘
                                                                   │
                                                                   ▼
                                                          ┌─────────────┐
                                                          │  执行推理   │
                                                          │  Diffusers  │
                                                          └─────────────┘
                                                                   │
                                                                   ▼
                                                          ┌─────────────┐
                                                          │  保存结果   │
                                                          │  更新状态   │
                                                          └─────────────┘
```

### 6.3 模型加载流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  首次生成   │────▶│  检查模型   │────▶│  模型未加载 │────▶│  从Hugging  │
│  请求       │     │  缓存       │     │             │     │  Face下载   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                                            │
       │                   │                                            │
       │                   ▼                                            ▼
       │            ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
       │            │  模型已加载 │────▶│  直接使用   │◀────│  加载到GPU  │
       │            │             │     │             │     │             │
       │            └─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│  执行推理   │
└─────────────┘
```

---

## 七、配置文件模板

### 7.1 前端配置

```json
// frontend/package.json
{
  "name": "ai-image-editor-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.2",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0",
    "lucide-react": "^0.303.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```

```javascript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

### 7.2 后端配置

```txt
# backend/requirements.txt
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0

# AI/ML
torch==2.1.2
torchvision==0.16.2
transformers==4.36.2
diffusers==0.25.0
accelerate==0.25.0
xformers==0.0.23
safetensors==0.4.1

# Image Processing
Pillow==10.1.0
opencv-python-headless==4.9.0.80
numpy==1.24.3

# Utils
python-dotenv==1.0.0
aiofiles==23.2.1
httpx==0.26.0
```

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Image Editor"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./outputs"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}
    
    # AI Model
    MODEL_CACHE_DIR: str = "./models"
    DEFAULT_MODEL: str = "runwayml/stable-diffusion-v1-5"
    DEVICE: str = "cuda"
    
    # Generation
    DEFAULT_STEPS: int = 30
    DEFAULT_STRENGTH: float = 0.75
    MAX_STEPS: int = 50
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.api.routes import image

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(image.router, prefix="/api/v1")

# Static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 7.3 AI模型配置

```yaml
# ai_models/configs/model_config.yaml
models:
  stable_diffusion_v1_5:
    id: "runwayml/stable-diffusion-v1-5"
    type: "img2img"
    dtype: "float16"
    enable_xformers: true
    enable_cpu_offload: true
    
  stable_diffusion_xl:
    id: "stabilityai/stable-diffusion-xl-base-1.0"
    type: "img2img"
    dtype: "float16"
    enable_xformers: true
    enable_cpu_offload: true
    
  controlnet_canny:
    id: "lllyasviel/control_v11p_sd15_canny"
    base_model: "runwayml/stable-diffusion-v1-5"
    type: "controlnet"
    dtype: "float16"

generation:
  defaults:
    steps: 30
    strength: 0.75
    guidance_scale: 7.5
    num_images: 1
  
  limits:
    max_steps: 50
    max_strength: 1.0
    min_strength: 0.1
    max_image_size: 1024

memory:
  enable_gradient_checkpointing: true
  enable_attention_slicing: true
  max_memory_gb: 8
```

### 7.4 Docker配置

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY ai_models/ ./ai_models/

# Create directories
RUN mkdir -p uploads outputs models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
      - ./models:/app/models
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - DEVICE=cuda
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

### 7.5 环境变量模板

```bash
# .env.example
# App
DEBUG=false
APP_NAME="AI Image Editor"

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# File Upload
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
MAX_FILE_SIZE=10485760

# AI Model
MODEL_CACHE_DIR=./models
DEFAULT_MODEL=runwayml/stable-diffusion-v1-5
DEVICE=cuda

# Hugging Face
HF_TOKEN=your_huggingface_token_here

# Generation Defaults
DEFAULT_STEPS=30
DEFAULT_STRENGTH=0.75
```

---

## 八、性能优化建议

### 8.1 前端优化
- 图片懒加载
- 生成进度实时显示 (WebSocket/SSE)
- 图片压缩预览
- 请求防抖

### 8.2 后端优化
- 异步任务队列 (Celery/Redis)
- 图片缓存
- 模型预热
- 批量处理

### 8.3 AI优化
- 模型量化 (INT8)
- TensorRT加速
- 批量推理
- 显存优化

---

## 九、安全考虑

1. **文件上传安全**
   - 文件类型验证
   - 文件大小限制
   - 病毒扫描
   - 存储隔离

2. **API安全**
   - 速率限制
   - 输入验证
   - CORS配置
   - 错误信息隐藏

3. **模型安全**
   - 提示词过滤
   - 内容审核
   - 资源限制

---

*文档版本: 1.0*
*创建日期: 2024*
