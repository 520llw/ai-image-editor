# AI Image Editor - Backend

FastAPI-based backend service for AI-powered image editing using Stable Diffusion.

## Features

- **Image Upload**: Upload images for editing (jpg, png, webp)
- **AI Generation**: Generate edited images using Stable Diffusion
- **Async Processing**: Background task processing for generation
- **Task Tracking**: Track generation progress in real-time
- **Model Management**: Automatic model loading and memory optimization
- **CORS Support**: Cross-origin requests enabled for frontend integration

## API Endpoints

### Image Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/images/upload` | Upload an image |
| POST | `/api/v1/images/generate` | Generate edited image |
| GET | `/api/v1/images/status/{task_id}` | Get generation status |
| GET | `/api/v1/images/download/{image_id}` | Download image |
| GET | `/api/v1/images/info/{image_id}` | Get image info |
| DELETE | `/api/v1/images/{image_id}` | Delete image |
| GET | `/api/v1/images/models/available` | List available models |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API info |
| POST | `/admin/cleanup` | Cleanup old files |

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | false | Debug mode |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `CORS_ORIGINS` | http://localhost:3000 | Allowed CORS origins |
| `MAX_FILE_SIZE` | 10485760 | Max upload size (10MB) |
| `DEVICE` | auto | AI device (auto/cuda/cpu) |
| `DEFAULT_MODEL` | runwayml/stable-diffusion-v1-5 | Default AI model |

## Usage Examples

### Upload Image

```bash
curl -X POST "http://localhost:8000/api/v1/images/upload" \
  -F "file=@image.jpg"
```

### Generate Image

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

### Check Status

```bash
curl "http://localhost:8000/api/v1/images/status/{task_id}"
```

### Download Result

```bash
curl "http://localhost:8000/api/v1/images/download/{image_id}?is_output=true" \
  -o result.png
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── image.py     # Image API routes
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_service.py # Image file operations
│   │   └── ai_service.py    # AI generation service
│   └── utils/
│       └── __init__.py
├── uploads/                 # Uploaded images
├── outputs/                 # Generated images
├── models/                  # AI model cache
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

- Python 3.10+
- CUDA-capable GPU (recommended, 8GB+ VRAM)
- 16GB+ RAM

## GPU Memory Optimization

The service includes several optimizations for GPU memory:

- Attention slicing
- VAE slicing
- XFormers memory efficient attention (if available)
- Automatic model unloading
- Memory cache clearing

## License

MIT License
