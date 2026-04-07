# AI Image Editor Frontend

AI智能图片编辑器前端项目 - 基于 React + TypeScript + Vite + Tailwind CSS + shadcn/ui

## 功能特性

- **图片上传**: 支持拖拽上传和点击选择，支持 JPG/PNG/WebP 格式
- **AI编辑**: 输入自然语言描述，AI智能编辑图片
- **风格选择**: 支持多种艺术风格（赛博朋克、水彩画、油画等）
- **参数调节**: 可调节编辑强度和推理步数
- **对比查看**: 原图与编辑后图片的滑动对比
- **高清下载**: 一键下载生成的图片

## 技术栈

- **框架**: React 18.2
- **语言**: TypeScript 5.3
- **构建工具**: Vite 5.0
- **样式**: Tailwind CSS 3.4
- **UI组件**: shadcn/ui
- **状态管理**: Zustand
- **HTTP客户端**: Axios

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API接口
│   │   ├── client.ts      # Axios实例
│   │   └── imageApi.ts    # 图片相关API
│   ├── components/        # 组件
│   │   ├── ui/            # shadcn/ui组件
│   │   ├── layout/        # 布局组件
│   │   ├── image/         # 图片相关组件
│   │   └── editor/        # 编辑器组件
│   ├── hooks/             # 自定义Hooks
│   ├── stores/            # 状态管理
│   ├── types/             # TypeScript类型
│   ├── utils/             # 工具函数
│   ├── App.tsx            # 主应用组件
│   ├── main.tsx           # 入口文件
│   └── index.css          # 全局样式
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## 环境变量

创建 `.env` 文件：

```env
# API基础URL
VITE_API_URL=http://localhost:8000
```

## API接口

### 上传图片
```
POST /api/v1/images/upload
Content-Type: multipart/form-data

Response:
{
  "image_id": "uuid",
  "url": "/uploads/xxx.jpg"
}
```

### 生成图片
```
POST /api/v1/images/generate
Content-Type: application/json

Request:
{
  "image_id": "uuid",
  "prompt": "描述文本",
  "negative_prompt": "反向描述",
  "style": "风格ID",
  "strength": 0.75,
  "steps": 30
}

Response:
{
  "task_id": "uuid",
  "status": "pending"
}
```

### 查询任务状态
```
GET /api/v1/images/status/{task_id}

Response:
{
  "task_id": "uuid",
  "status": "processing|completed|failed",
  "progress": 50,
  "result_url": "/outputs/xxx.jpg"
}
```

## 组件说明

### ImageUploader
图片上传组件，支持拖拽和点击上传

### ImagePreview
图片预览组件，支持缩放、重置、下载

### ImageComparison
图片对比组件，支持滑动对比原图和编辑后的图片

### PromptInput
提示词输入组件，支持示例提示词选择

### GenerateButton
生成按钮组件，显示生成状态和进度

## 自定义配置

### 添加新的艺术风格

在 `src/components/editor/StyleSelector.tsx` 中的 `STYLE_OPTIONS` 数组添加新风格：

```typescript
{ 
  id: 'new-style', 
  name: '新风格名称', 
  description: '风格描述' 
}
```

### 修改默认参数

在 `src/stores/editorStore.ts` 中修改 `initialState`：

```typescript
const initialState = {
  strength: 0.75,  // 默认编辑强度
  steps: 30,       // 默认推理步数
  // ...
}
```

## 浏览器支持

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 许可证

MIT License
