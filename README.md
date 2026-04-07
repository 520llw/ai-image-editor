# AI Image Editor - AI智能图片编辑器

<p align="center">
  <img src="https://img.shields.io/badge/React-18.2-blue?style=flat-square&logo=react" alt="React">
  <img src="https://img.shields.io/badge/Python-3.10+-green?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-teal?style=flat-square&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/PyTorch-2.1+-orange?style=flat-square&logo=pytorch" alt="PyTorch">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
</p>

<p align="center">
  <b>基于AI的智能图片编辑Web应用</b><br>
  上传图片，输入自然语言描述，AI自动编辑生成新图片
</p>

---

## 项目介绍

AI Image Editor 是一个全栈Web应用，使用最先进的AI模型（InstructPix2Pix）实现文本驱动的图像编辑。用户只需上传图片并输入自然语言描述，AI就能智能理解并编辑图片。

### 核心功能

- **智能图片上传**: 支持拖拽上传，支持 JPG/PNG/WebP 格式
- **AI智能编辑**: 输入自然语言描述，AI自动编辑图片
- **多种艺术风格**: 赛博朋克、水彩画、油画、卡通等预设风格
- **参数精细调节**: 可调节编辑强度和推理步数
- **实时进度显示**: 生成过程实时显示进度
- **对比查看**: 原图与编辑后图片的滑动对比
- **高清下载**: 一键下载生成的图片

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Frontend)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  React 18   │  │ TypeScript  │  │   Tailwind CSS      │  │
│  │  Vite       │  │  Zustand    │  │    shadcn/ui        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST API
┌───────────────────────────▼─────────────────────────────────┐
│                        后端 (Backend)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   FastAPI   │  │   Pydantic  │  │   Background Tasks  │  │
│  │   Uvicorn   │  │   Pillow    │  │    File Upload      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      AI模型 (AI Models)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   PyTorch   │  │  Diffusers  │  │ InstructPix2Pix     │  │
│  │  Transformers│  │   CUDA      │  │  Model Manager      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 技术栈

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2.x | UI框架 |
| TypeScript | 5.3.x | 类型安全 |
| Vite | 5.0.x | 构建工具 |
| Tailwind CSS | 3.4.x | 样式框架 |
| shadcn/ui | 最新 | UI组件库 |
| Zustand | 4.4.x | 状态管理 |
| React Query | 5.x | 服务端状态管理 |

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 编程语言 |
| FastAPI | 0.109.x | Web框架 |
| Uvicorn | 0.27.x | ASGI服务器 |
| Pillow | 10.x | 图像处理 |

### AI模型
| 技术 | 版本 | 用途 |
|------|------|------|
| PyTorch | 2.1.x | 深度学习框架 |
| Transformers | 4.36.x | 预训练模型 |
| Diffusers | 0.25.x | 扩散模型 |
| InstructPix2Pix | timbrooks/instruct-pix2pix | 图像编辑模型 |

---

## 项目结构

```
ai-image-editor/
├── frontend/                    # 前端代码
│   ├── src/
│   │   ├── api/                # API接口
│   │   ├── components/         # React组件
│   │   │   ├── ui/            # shadcn/ui组件
│   │   │   ├── image/         # 图片相关组件
│   │   │   └── editor/        # 编辑器组件
│   │   ├── hooks/             # 自定义Hooks
│   │   ├── stores/            # 状态管理
│   │   ├── types/             # TypeScript类型
│   │   └── utils/             # 工具函数
│   ├── public/                # 静态资源
│   ├── package.json           # 依赖配置
│   ├── vite.config.ts         # Vite配置
│   └── README.md              # 前端文档
│
├── backend/                     # 后端代码
│   ├── app/
│   │   ├── api/routes/        # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── uploads/               # 上传图片存储
│   ├── outputs/               # 生成图片存储
│   ├── models/                # AI模型缓存
│   ├── requirements.txt       # Python依赖
│   └── README.md              # 后端文档
│
├── ai_models/                   # AI模型代码
│   ├── pipelines/             # 模型管道
│   ├── utils/                 # 显存/图像工具
│   ├── model_manager.py       # 模型管理器
│   ├── example_usage.py       # 使用示例
│   └── requirements.txt       # AI模型依赖
│
├── tests/                       # 测试代码
│   ├── test_backend.py        # 后端测试
│   ├── test_integration.py    # 集成测试
│   └── TEST_REPORT.md         # 测试报告
│
├── .gitignore                   # Git忽略文件
└── README.md                    # 项目文档
```

---

## 快速开始

### 系统要求

**最低配置:**
- CPU: 4核
- 内存: 8GB
- 存储: 20GB
- Python: 3.10+
- Node.js: 18+

**推荐配置 (GPU加速):**
- GPU: NVIDIA GTX 1060 6GB+ 或 RTX 5070
- 显存: 8GB+
- CUDA: 11.8+
- 内存: 16GB+

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ai-image-editor.git
cd ai-image-editor
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建必要目录
mkdir -p uploads outputs models

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动
后端API将在 http://localhost:8000 运行

---

## API文档

### 图片操作

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/images/upload` | 上传图片 |
| POST | `/api/v1/images/generate` | 生成编辑后的图片 |
| GET | `/api/v1/images/status/{task_id}` | 查询任务状态 |
| GET | `/api/v1/images/download/{image_id}` | 下载图片 |
| DELETE | `/api/v1/images/{image_id}` | 删除图片 |

### 系统接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | API信息 |
| GET | `/health` | 健康检查 |
| GET | `/docs` | Swagger文档 |

### 使用示例

**上传图片:**
```bash
curl -X POST "http://localhost:8000/api/v1/images/upload" \
  -F "file=@your-image.jpg"
```

**生成图片:**
```bash
curl -X POST "http://localhost:8000/api/v1/images/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "your-image-id",
    "prompt": "make it look like a painting",
    "strength": 0.75,
    "steps": 30
  }'
```

---

## 功能演示

### 图片上传
- 支持拖拽上传
- 支持点击选择文件
- 支持 JPG/PNG/WebP 格式
- 最大文件大小: 10MB

### AI编辑
输入自然语言描述，例如:
- "make it snowy" - 添加雪景效果
- "turn it into a painting" - 转换为油画风格
- "make it look like a cartoon" - 卡通风格
- "add sunset lighting" - 添加日落光线
- "make it night time" - 转换为夜晚场景

### 参数调节
- **编辑强度**: 控制AI编辑的程度 (0.1 - 1.0)
- **推理步数**: 影响生成质量和速度 (10 - 50)

---

## 环境变量

### 后端配置 (.env)

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 文件上传
MAX_FILE_SIZE=10485760  # 10MB

# AI模型
DEFAULT_MODEL=timbrooks/instruct-pix2pix
DEVICE=auto  # auto, cuda, cpu

# HuggingFace Token (可选，用于下载模型)
HF_TOKEN=your_token_here
```

### 前端配置 (.env)

```bash
# API基础URL
VITE_API_URL=http://localhost:8000
```

---

## 性能优化

### 前端优化
- 图片懒加载
- 生成进度实时显示
- 请求防抖
- 组件懒加载

### 后端优化
- 异步任务处理
- 图片缓存
- 模型预热
- 后台任务队列

### AI优化
- FP16半精度推理
- CPU Offload显存优化
- XFormers加速 (可选)
- 注意力切片
- 显存自动清理

---

## 测试

```bash
# 运行后端测试
cd backend
pytest

# 运行集成测试
cd tests
python test_integration.py
```

---

## 常见问题

### Q: 模型下载失败怎么办?
A: 设置 HuggingFace Token 或手动下载模型到 `backend/models/` 目录

### Q: 显存不足怎么办?
A: 启用 CPU Offload 或降低推理步数

### Q: 生成速度慢怎么办?
A: 确保使用GPU加速，安装xformers，降低推理步数

---

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 致谢

- [InstructPix2Pix](https://github.com/timothybrooks/instruct-pix2pix) - AI图像编辑模型
- [Diffusers](https://github.com/huggingface/diffusers) - HuggingFace扩散模型库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [shadcn/ui](https://ui.shadcn.com/) - 漂亮的UI组件

---

<p align="center">
  Made with ❤️ by AI Image Editor Team
</p>
