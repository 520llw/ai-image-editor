# backend/app/api/routes/image.py
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import aiofiles

from app.config import get_settings, Settings
from app.services.ai_service import AIService

router = APIRouter(prefix="/images", tags=["images"])

# 任务存储（生产环境应使用Redis）
tasks = {}


class GenerateRequest(BaseModel):
    image_id: str
    prompt: str
    negative_prompt: str = ""
    style: str = "default"
    strength: float = 0.75
    steps: int = 30
    guidance_scale: float = 7.5


class TaskResponse(BaseModel):
    task_id: str
    status: str
    progress: int = 0
    result_url: Optional[str] = None
    error: Optional[str] = None


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """上传图片"""
    # 验证文件类型
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件类型: {ext}")
    
    # 生成唯一ID
    image_id = str(uuid.uuid4())
    filename = f"{image_id}{ext}"
    file_path = Path(settings.UPLOAD_DIR) / filename
    
    # 保存文件
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(400, "文件大小超过限制")
            await f.write(content)
    except Exception as e:
        raise HTTPException(500, f"文件保存失败: {str(e)}")
    
    return {
        "image_id": image_id,
        "filename": filename,
        "url": f"/uploads/{filename}"
    }


@router.post("/generate", response_model=TaskResponse)
async def generate_image(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings)
):
    """提交图片生成任务"""
    # 检查源图片是否存在
    upload_dir = Path(settings.UPLOAD_DIR)
    source_files = list(upload_dir.glob(f"{request.image_id}.*"))
    if not source_files:
        raise HTTPException(404, "源图片不存在")
    
    # 创建任务
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "result_url": None,
        "error": None
    }
    
    # 后台执行生成
    background_tasks.add_task(
        process_generation,
        task_id,
        request,
        str(source_files[0]),
        settings
    )
    
    return TaskResponse(task_id=task_id, status="pending")


@router.get("/status/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")
    
    task = tasks[task_id]
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        result_url=task.get("result_url"),
        error=task.get("error")
    )


@router.get("/download/{image_id}")
async def download_image(
    image_id: str,
    settings: Settings = Depends(get_settings)
):
    """下载图片"""
    # 先在outputs中查找
    output_dir = Path(settings.OUTPUT_DIR)
    files = list(output_dir.glob(f"{image_id}.*"))
    
    if not files:
        # 再在uploads中查找
        upload_dir = Path(settings.UPLOAD_DIR)
        files = list(upload_dir.glob(f"{image_id}.*"))
    
    if not files:
        raise HTTPException(404, "图片不存在")
    
    return FileResponse(files[0])


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    settings: Settings = Depends(get_settings)
):
    """删除图片"""
    deleted = False
    
    # 删除uploads中的文件
    upload_dir = Path(settings.UPLOAD_DIR)
    for file in upload_dir.glob(f"{image_id}.*"):
        file.unlink()
        deleted = True
    
    # 删除outputs中的文件
    output_dir = Path(settings.OUTPUT_DIR)
    for file in output_dir.glob(f"{image_id}.*"):
        file.unlink()
        deleted = True
    
    if not deleted:
        raise HTTPException(404, "图片不存在")
    
    return {"success": True}


async def process_generation(
    task_id: str,
    request: GenerateRequest,
    source_path: str,
    settings: Settings
):
    """后台处理图片生成"""
    try:
        tasks[task_id]["status"] = "processing"
        
        # 初始化AI服务
        ai_service = AIService(settings)
        
        # 更新进度
        tasks[task_id]["progress"] = 10
        
        # 加载模型（如果未加载）
        ai_service.load_model()
        tasks[task_id]["progress"] = 30
        
        # 执行生成
        output_filename = f"{task_id}.png"
        output_path = Path(settings.OUTPUT_DIR) / output_filename
        
        await ai_service.generate(
            source_path=source_path,
            output_path=str(output_path),
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            strength=request.strength,
            steps=request.steps,
            guidance_scale=request.guidance_scale,
            progress_callback=lambda p: update_progress(task_id, 30 + int(p * 0.6))
        )
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result_url"] = f"/outputs/{output_filename}"
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)


def update_progress(task_id: str, progress: int):
    """更新任务进度"""
    if task_id in tasks:
        tasks[task_id]["progress"] = min(progress, 99)
