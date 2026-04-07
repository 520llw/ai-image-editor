"""
导入测试脚本

验证所有模块是否可以正确导入
"""

import sys
import os
import traceback

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_import(module_name, import_statement):
    """测试单个导入"""
    try:
        exec(import_statement)
        print(f"✓ {module_name}")
        return True
    except Exception as e:
        print(f"✗ {module_name}: {e}")
        return False


def main():
    """运行所有导入测试"""
    print("=" * 60)
    print("AI模型集成导入测试")
    print("=" * 60)
    
    # 基础依赖测试
    basic_tests = [
        ("torch", "import torch"),
        ("PIL", "from PIL import Image"),
        ("numpy", "import numpy as np"),
    ]
    
    print("\n基础依赖:")
    basic_results = []
    for name, statement in basic_tests:
        basic_results.append(test_import(name, statement))
    
    # 可选依赖测试
    optional_tests = [
        ("diffusers", "from diffusers import StableDiffusionInstructPix2PixPipeline"),
        ("transformers", "import transformers"),
    ]
    
    print("\n可选依赖:")
    optional_results = []
    for name, statement in optional_tests:
        result = test_import(name, statement)
        optional_results.append(result)
    
    # 本地模块测试
    local_tests = [
        ("model_manager", "from model_manager import ModelManager, ModelConfig, ModelType, get_model_manager"),
        ("instruct_pix2pix_pipeline", "from pipelines.instruct_pix2pix_pipeline import InstructPix2PixPipeline"),
        ("memory_utils", "from utils.memory_utils import get_gpu_memory_info, clear_gpu_cache, MemoryMonitor"),
        ("image_utils", "from utils.image_utils import load_image, save_image, pil_to_tensor, tensor_to_pil"),
    ]
    
    print("\n本地模块:")
    local_results = []
    for name, statement in local_tests:
        local_results.append(test_import(name, statement))
    
    # 汇总
    print("\n" + "=" * 60)
    basic_passed = sum(basic_results)
    optional_passed = sum(optional_results)
    local_passed = sum(local_results)
    
    print(f"基础依赖: {basic_passed}/{len(basic_results)} 通过")
    print(f"可选依赖: {optional_passed}/{len(optional_results)} 通过")
    print(f"本地模块: {local_passed}/{len(local_results)} 通过")
    
    total_passed = basic_passed + optional_passed + local_passed
    total_tests = len(basic_tests) + len(optional_tests) + len(local_tests)
    
    print(f"总计: {total_passed}/{total_tests} 通过")
    
    if basic_passed == len(basic_tests) and local_passed == len(local_tests):
        print("\n✓ 核心模块测试通过！")
        print("注意: 可选依赖(diffusers等)需要在运行时安装")
        return 0
    elif basic_passed == len(basic_tests):
        print("\n⚠ 基础依赖通过，但本地模块有问题")
        return 1
    else:
        print("\n✗ 基础依赖测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
