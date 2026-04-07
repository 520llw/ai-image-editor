#!/usr/bin/env python3
"""
AI Image Editor - Backend Testing Script
Tests backend API endpoints, models, and services
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add backend to path
sys.path.insert(0, '/mnt/okcomputer/output/backend')

# Test result tracking
class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"

@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str = ""

class TestRunner:
    def __init__(self):
        self.results: List[TestResult] = []
        self.backend_dir = Path("/mnt/okcomputer/output/backend")
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        colors = {
            "INFO": "\033[0;34m",
            "PASS": "\033[0;32m",
            "FAIL": "\033[0;31m",
            "WARN": "\033[1;33m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        print(f"{color}[{level}]{reset} {message}")
        
    def test(self, name: str, condition: bool, message: str = "") -> bool:
        """Run a test and record result"""
        status = TestStatus.PASSED if condition else TestStatus.FAILED
        result = TestResult(name=name, status=status, message=message)
        self.results.append(result)
        
        if condition:
            self.log(f"✓ {name}", "PASS")
        else:
            self.log(f"✗ {name}: {message}", "FAIL")
        return condition
        
    def warn(self, name: str, message: str):
        """Record a warning"""
        result = TestResult(name=name, status=TestStatus.WARNING, message=message)
        self.results.append(result)
        self.log(f"⚠ {name}: {message}", "WARN")
        
    def file_exists(self, path: Path, description: str) -> bool:
        """Test if a file exists"""
        return self.test(f"{description} exists", path.exists(), f"File not found: {path}")
        
    def dir_exists(self, path: Path, description: str) -> bool:
        """Test if a directory exists"""
        return self.test(f"{description} exists", path.is_dir(), f"Directory not found: {path}")
        
    def print_summary(self):
        """Print test summary"""
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        warnings = sum(1 for r in self.results if r.status == TestStatus.WARNING)
        total = len(self.results)
        
        print("\n" + "=" * 50)
        print("           TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total}")
        print(f"\033[0;32mPassed:      {passed}\033[0m")
        print(f"\033[0;31mFailed:      {failed}\033[0m")
        print(f"\033[1;33mWarnings:    {warnings}\033[0m")
        print("=" * 50)
        
        if failed == 0:
            print("\033[0;32m✓ All tests passed!\033[0m")
            return 0
        else:
            print("\033[0;31m✗ Some tests failed!\033[0m")
            return 1


def test_project_structure(runner: TestRunner):
    """Test project structure"""
    runner.log("\n=== TEST GROUP: Project Structure ===", "INFO")
    
    # Main directories
    runner.dir_exists(runner.backend_dir, "Backend directory")
    runner.dir_exists(runner.backend_dir / "app", "App directory")
    runner.dir_exists(runner.backend_dir / "app" / "api", "API directory")
    runner.dir_exists(runner.backend_dir / "app" / "api" / "routes", "Routes directory")
    runner.dir_exists(runner.backend_dir / "app" / "models", "Models directory")
    runner.dir_exists(runner.backend_dir / "app" / "services", "Services directory")
    runner.dir_exists(runner.backend_dir / "app" / "core", "Core directory")
    runner.dir_exists(runner.backend_dir / "app" / "utils", "Utils directory")


def test_configuration_files(runner: TestRunner):
    """Test configuration files"""
    runner.log("\n=== TEST GROUP: Configuration Files ===", "INFO")
    
    runner.file_exists(runner.backend_dir / "requirements.txt", "requirements.txt")
    runner.file_exists(runner.backend_dir / "app" / "config.py", "config.py")
    runner.file_exists(runner.backend_dir / "app" / "main.py", "main.py")


def test_model_files(runner: TestRunner):
    """Test Pydantic model files"""
    runner.log("\n=== TEST GROUP: Model Files ===", "INFO")
    
    models_file = runner.backend_dir / "app" / "models" / "schemas.py"
    runner.file_exists(models_file, "schemas.py")
    
    if models_file.exists():
        content = models_file.read_text()
        
        # Check for required models
        runner.test("TaskStatus enum defined", "class TaskStatus" in content)
        runner.test("ImageUploadResponse model defined", "class ImageUploadResponse" in content)
        runner.test("ImageGenerateRequest model defined", "class ImageGenerateRequest" in content)
        runner.test("ImageGenerateResponse model defined", "class ImageGenerateResponse" in content)
        runner.test("TaskStatusResponse model defined", "class TaskStatusResponse" in content)
        runner.test("HealthCheckResponse model defined", "class HealthCheckResponse" in content)
        runner.test("ErrorResponse model defined", "class ErrorResponse" in content)


def test_route_files(runner: TestRunner):
    """Test API route files"""
    runner.log("\n=== TEST GROUP: Route Files ===", "INFO")
    
    routes_file = runner.backend_dir / "app" / "api" / "routes" / "image.py"
    runner.file_exists(routes_file, "image.py routes")
    
    if routes_file.exists():
        content = routes_file.read_text()
        
        # Check for required endpoints
        runner.test("Upload endpoint defined", '@router.post("/upload")' in content or '"/upload"' in content)
        runner.test("Generate endpoint defined", '@router.post("/generate")' in content or '"/generate"' in content)
        runner.test("Status endpoint defined", '@router.get("/status/' in content or '"/status/"' in content)
        runner.test("Download endpoint defined", '@router.get("/download/' in content or '"/download/"' in content)
        runner.test("Models endpoint defined", '"/models/' in content or "models/available" in content)
        runner.test("Delete endpoint defined", '@router.delete' in content)


def test_service_files(runner: TestRunner):
    """Test service files"""
    runner.log("\n=== TEST GROUP: Service Files ===", "INFO")
    
    ai_service = runner.backend_dir / "app" / "services" / "ai_service.py"
    image_service = runner.backend_dir / "app" / "services" / "image_service.py"
    
    runner.file_exists(ai_service, "ai_service.py")
    runner.file_exists(image_service, "image_service.py")
    
    if ai_service.exists():
        content = ai_service.read_text()
        runner.test("ModelManager class defined", "class ModelManager" in content)
        runner.test("AIService class defined", "class AIService" in content)
        runner.test("Style presets defined", "STYLE_PROMPTS" in content)
        runner.test("Task management defined", "GenerationTask" in content)
    
    if image_service.exists():
        content = image_service.read_text()
        runner.test("ImageService class defined", "class ImageService" in content)
        runner.test("File validation defined", "validate_file" in content)
        runner.test("Image saving defined", "save_upload" in content)


def test_requirements(runner: TestRunner):
    """Test requirements.txt"""
    runner.log("\n=== TEST GROUP: Requirements ===", "INFO")
    
    req_file = runner.backend_dir / "requirements.txt"
    if not req_file.exists():
        runner.test("requirements.txt exists", False, "File not found")
        return
    
    content = req_file.read_text()
    
    # Check for required dependencies
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("python-multipart", "Python Multipart"),
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("diffusers", "Diffusers"),
        ("Pillow", "Pillow"),
        ("numpy", "NumPy"),
        ("aiofiles", "Aiofiles"),
    ]
    
    for package, name in required_packages:
        runner.test(f"{name} in requirements", package.lower() in content.lower())


def test_main_application(runner: TestRunner):
    """Test main application"""
    runner.log("\n=== TEST GROUP: Main Application ===", "INFO")
    
    main_file = runner.backend_dir / "app" / "main.py"
    if not main_file.exists():
        runner.test("main.py exists", False, "File not found")
        return
    
    content = main_file.read_text()
    
    # Check FastAPI app setup
    runner.test("FastAPI app created", "FastAPI(" in content)
    runner.test("CORS middleware configured", "CORSMiddleware" in content)
    runner.test("Router included", "include_router" in content)
    runner.test("Static files mounted", "StaticFiles" in content)
    runner.test("Health check endpoint", '"/health"' in content or "/health" in content)
    runner.test("Exception handlers defined", "exception_handler" in content)
    runner.test("Lifespan context manager", "lifespan" in content or "@asynccontextmanager" in content)


def test_config(runner: TestRunner):
    """Test configuration"""
    runner.log("\n=== TEST GROUP: Configuration ===", "INFO")
    
    config_file = runner.backend_dir / "app" / "config.py"
    if not config_file.exists():
        runner.test("config.py exists", False, "File not found")
        return
    
    content = config_file.read_text()
    
    # Check configuration
    runner.test("Settings class defined", "class Settings" in content)
    runner.test("BaseSettings used", "BaseSettings" in content)
    runner.test("CORS origins configured", "CORS_ORIGINS" in content)
    runner.test("File upload config", "MAX_FILE_SIZE" in content)
    runner.test("Model config", "DEFAULT_MODEL" in content)
    runner.test("get_settings function", "def get_settings" in content)


def test_pydantic_models():
    """Test Pydantic models can be imported and validated"""
    runner = TestRunner()
    runner.log("\n=== TEST GROUP: Pydantic Model Validation ===", "INFO")
    
    try:
        from app.models.schemas import (
            TaskStatus, ImageUploadResponse, ImageGenerateRequest,
            ImageGenerateResponse, TaskStatusResponse, HealthCheckResponse,
            ErrorResponse, GenerationStyle
        )
        runner.test("Import schemas", True)
        
        # Test TaskStatus enum
        runner.test("TaskStatus enum values", 
                   all(hasattr(TaskStatus, s) for s in ["PENDING", "PROCESSING", "COMPLETED", "FAILED"]))
        
        # Test GenerationStyle enum
        runner.test("GenerationStyle enum values",
                   all(hasattr(GenerationStyle, s) for s in ["NONE", "PHOTOREALISTIC", "ANIME", "DIGITAL_ART"]))
        
        # Test ImageUploadResponse model
        try:
            response = ImageUploadResponse(
                success=True,
                image_id="test-id",
                filename="test.jpg",
                url="/uploads/test.jpg",
                width=512,
                height=512,
                format="jpg",
                size_bytes=1024
            )
            runner.test("ImageUploadResponse validation", True)
        except Exception as e:
            runner.test("ImageUploadResponse validation", False, str(e))
        
        # Test ImageGenerateRequest model
        try:
            request = ImageGenerateRequest(
                image_id="test-id",
                prompt="test prompt",
                strength=0.75,
                steps=30
            )
            runner.test("ImageGenerateRequest validation", True)
        except Exception as e:
            runner.test("ImageGenerateRequest validation", False, str(e))
        
        # Test validation for invalid request
        try:
            request = ImageGenerateRequest(
                image_id="test-id",
                prompt="",  # Empty prompt should fail
                strength=0.75,
                steps=30
            )
            runner.test("Empty prompt validation", False, "Should have raised validation error")
        except Exception:
            runner.test("Empty prompt validation", True)  # Expected to fail
        
        # Test HealthCheckResponse
        try:
            from datetime import datetime
            response = HealthCheckResponse(
                status="healthy",
                version="1.0.0",
                timestamp=datetime.now(),
                device="cpu",
                cuda_available=False,
                models_loaded=0
            )
            runner.test("HealthCheckResponse validation", True)
        except Exception as e:
            runner.test("HealthCheckResponse validation", False, str(e))
            
    except ImportError as e:
        runner.test("Import schemas", False, str(e))
    except Exception as e:
        runner.test("Pydantic model validation", False, str(e))
    
    return runner


def test_api_endpoints():
    """Test API endpoints (requires running server)"""
    runner = TestRunner()
    runner.log("\n=== TEST GROUP: API Endpoints (Optional) ===", "INFO")
    
    try:
        import httpx
        
        # Test health endpoint
        try:
            response = httpx.get("http://localhost:8000/health", timeout=5)
            runner.test("Health endpoint accessible", response.status_code == 200)
            if response.status_code == 200:
                data = response.json()
                runner.test("Health response has status", "status" in data)
        except Exception as e:
            runner.warn("Health endpoint test", f"Server not running: {e}")
        
        # Test root endpoint
        try:
            response = httpx.get("http://localhost:8000/", timeout=5)
            runner.test("Root endpoint accessible", response.status_code == 200)
        except Exception as e:
            runner.warn("Root endpoint test", f"Server not running: {e}")
            
    except ImportError:
        runner.warn("API endpoint tests", "httpx not installed")
    
    return runner


def main():
    """Run all tests"""
    print("=" * 50)
    print("  AI Image Editor - Backend Tests")
    print("=" * 50)
    
    # Create main runner
    main_runner = TestRunner()
    
    # Run static tests
    test_project_structure(main_runner)
    test_configuration_files(main_runner)
    test_model_files(main_runner)
    test_route_files(main_runner)
    test_service_files(main_runner)
    test_requirements(main_runner)
    test_main_application(main_runner)
    test_config(main_runner)
    
    # Run dynamic tests
    pydantic_runner = test_pydantic_models()
    main_runner.results.extend(pydantic_runner.results)
    
    # Run API tests (optional)
    api_runner = test_api_endpoints()
    main_runner.results.extend(api_runner.results)
    
    # Print summary
    return main_runner.print_summary()


if __name__ == "__main__":
    sys.exit(main())
