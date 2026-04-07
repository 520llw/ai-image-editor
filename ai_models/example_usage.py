"""
AI模型集成示例代码

演示如何使用InstructPix2Pix进行图像编辑

作者: AI Assistant
"""

import torch
from model_manager import ModelManager, ModelConfig, ModelType, get_model_manager


def example_basic_usage():
    """
    基础使用示例
    
    使用模型管理器加载模型并编辑图像
    """
    print("=" * 60)
    print("示例1: 基础使用")
    print("=" * 60)
    
    # 获取模型管理器实例
    manager = get_model_manager()
    
    # 配置模型
    config = ModelConfig(
        model_id="timbrooks/instruct-pix2pix",
        model_type=ModelType.INSTRUCT_PIX2PIX,
        torch_dtype=torch.float16,
        device="cuda",
        enable_cpu_offload=True,  # 关键优化，适合12GB显存
    )
    
    # 加载模型
    pipeline = manager.load_model(config)
    
    # 编辑图像
    result = manager.generate(
        model_type=ModelType.INSTRUCT_PIX2PIX,
        image="input.jpg",  # 替换为你的图像路径
        prompt="make it sunny",  # 编辑指令
        output_path="output_sunny.jpg",
        num_inference_steps=10,
        image_guidance_scale=1.5,
        guidance_scale=7.5,
    )
    
    print(f"编辑完成，结果已保存")
    
    # 打印显存统计
    manager.print_memory_stats()
    
    # 卸载模型
    manager.unload_model(ModelType.INSTRUCT_PIX2PIX)


def example_direct_pipeline():
    """
    直接使用管道示例
    
    不使用模型管理器，直接创建和使用管道
    """
    print("\n" + "=" * 60)
    print("示例2: 直接使用管道")
    print("=" * 60)
    
    from pipelines.instruct_pix2pix_pipeline import create_instruct_pix2pix_pipeline
    
    # 创建并加载管道
    pipeline = create_instruct_pix2pix_pipeline(
        model_id="timbrooks/instruct-pix2pix",
        device="cuda",
        enable_cpu_offload=True,
    )
    
    # 编辑图像
    result = pipeline.edit_image(
        image="input.jpg",
        prompt="turn it into a painting",
        output_path="output_painting.jpg",
        num_inference_steps=15,
        image_guidance_scale=1.5,
        guidance_scale=7.5,
        seed=42,  # 设置随机种子以获得可重复的结果
    )
    
    print(f"编辑完成")
    
    # 获取模型信息
    info = pipeline.get_model_info()
    print(f"模型信息: {info}")
    
    # 卸载模型
    pipeline.unload()


def example_batch_processing():
    """
    批量处理示例
    
    批量编辑多张图像
    """
    print("\n" + "=" * 60)
    print("示例3: 批量处理")
    print("=" * 60)
    
    from pipelines.instruct_pix2pix_pipeline import create_instruct_pix2pix_pipeline
    
    # 创建管道
    pipeline = create_instruct_pix2pix_pipeline()
    
    # 图像列表
    images = ["image1.jpg", "image2.jpg", "image3.jpg"]
    
    # 批量编辑
    results = pipeline.batch_edit(
        images=images,
        prompt="add sunset lighting",
        num_inference_steps=10,
    )
    
    print(f"批量处理完成，共处理 {len(results)} 张图像")
    
    # 卸载模型
    pipeline.unload()


def example_memory_management():
    """
    显存管理示例
    
    演示如何监控和管理显存
    """
    print("\n" + "=" * 60)
    print("示例4: 显存管理")
    print("=" * 60)
    
    from utils.memory_utils import (
        get_gpu_memory_info,
        print_memory_stats,
        clear_gpu_cache,
        MemoryMonitor,
    )
    
    # 打印初始显存状态
    print("初始显存状态:")
    print_memory_stats()
    
    # 使用上下文管理器监控显存
    with MemoryMonitor("模型加载"):
        manager = get_model_manager()
        config = ModelConfig(
            model_id="timbrooks/instruct-pix2pix",
            model_type=ModelType.INSTRUCT_PIX2PIX,
            torch_dtype=torch.float16,
            enable_cpu_offload=True,
        )
        pipeline = manager.load_model(config)
    
    # 获取显存信息
    mem_info = get_gpu_memory_info()
    print(f"当前显存使用: {mem_info.allocated_gb:.2f} GB")
    
    # 清理缓存
    clear_gpu_cache()
    
    # 卸载所有模型
    manager.unload_all_models()
    
    print("最终显存状态:")
    print_memory_stats()


def example_different_prompts():
    """
    不同提示词示例
    
    展示各种有效的编辑指令
    """
    print("\n" + "=" * 60)
    print("示例5: 不同提示词")
    print("=" * 60)
    
    from pipelines.instruct_pix2pix_pipeline import create_instruct_pix2pix_pipeline
    
    # 创建管道
    pipeline = create_instruct_pix2pix_pipeline()
    
    # 各种编辑指令示例
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
    
    image_path = "input.jpg"
    
    for i, prompt in enumerate(prompts):
        print(f"处理: {prompt}")
        try:
            result = pipeline.edit_image(
                image=image_path,
                prompt=prompt,
                output_path=f"output_{i:02d}_{prompt.replace(' ', '_')}.jpg",
                num_inference_steps=10,
            )
        except Exception as e:
            print(f"处理失败: {e}")
    
    pipeline.unload()


def example_api_style():
    """
    API风格使用示例
    
    演示如何在后端API中使用
    """
    print("\n" + "=" * 60)
    print("示例6: API风格使用")
    print("=" * 60)
    
    from fastapi import FastAPI, File, UploadFile, Form
    from fastapi.responses import FileResponse
    import tempfile
    import os
    
    app = FastAPI()
    manager = get_model_manager()
    
    # 确保模型已加载
    if not manager.is_model_loaded(ModelType.INSTRUCT_PIX2PIX):
        config = ModelConfig(
            model_id="timbrooks/instruct-pix2pix",
            model_type=ModelType.INSTRUCT_PIX2PIX,
            torch_dtype=torch.float16,
            enable_cpu_offload=True,
        )
        manager.load_model(config)
    
    @app.post("/edit-image")
    async def edit_image(
        file: UploadFile = File(...),
        prompt: str = Form(...),
        num_steps: int = Form(10),
    ):
        """
        图像编辑API端点
        
        Args:
            file: 上传的图像文件
            prompt: 编辑指令
            num_steps: 推理步数
            
        Returns:
            编辑后的图像
        """
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            input_path = tmp.name
        
        # 生成输出路径
        output_path = input_path.replace(".jpg", "_edited.jpg")
        
        try:
            # 编辑图像
            result = manager.generate(
                model_type=ModelType.INSTRUCT_PIX2PIX,
                image=input_path,
                prompt=prompt,
                output_path=output_path,
                num_inference_steps=num_steps,
            )
            
            # 返回结果
            return FileResponse(output_path)
            
        finally:
            # 清理临时文件
            if os.path.exists(input_path):
                os.remove(input_path)
    
    print("API示例代码已定义")
    print("运行: uvicorn example_usage:app --reload")


def main():
    """
    主函数
    
    运行所有示例
    """
    print("InstructPix2Pix AI图像编辑示例")
    print("=" * 60)
    
    # 检查CUDA可用性
    if not torch.cuda.is_available():
        print("警告: CUDA不可用，将使用CPU运行（性能会显著降低）")
    else:
        print(f"CUDA可用: {torch.cuda.get_device_name(0)}")
    
    # 运行示例（取消注释以运行）
    # example_basic_usage()
    # example_direct_pipeline()
    # example_batch_processing()
    # example_memory_management()
    # example_different_prompts()
    # example_api_style()
    
    print("\n示例代码已准备就绪！")
    print("请根据需求取消注释相应的示例函数来运行。")


if __name__ == "__main__":
    main()
