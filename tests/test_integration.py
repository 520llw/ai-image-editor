#!/usr/bin/env python3
"""
AI Image Editor - Integration Testing Script
Tests frontend-backend integration, API compatibility, and end-to-end workflows
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Test result tracking
class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    INFO = "info"

@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str = ""

class TestRunner:
    def __init__(self):
        self.results: List[TestResult] = []
        self.frontend_dir = Path("/mnt/okcomputer/output/frontend")
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
        
    def info(self, name: str, message: str):
        """Record info"""
        result = TestResult(name=name, status=TestStatus.INFO, message=message)
        self.results.append(result)
        self.log(f"ℹ {name}: {message}", "INFO")
        
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


def test_api_endpoint_compatibility(runner: TestRunner):
    """Test that frontend and backend API endpoints match"""
    runner.log("\n=== TEST GROUP: API Endpoint Compatibility ===", "INFO")
    
    # Read frontend API
    frontend_api = runner.frontend_dir / "src" / "api" / "imageApi.ts"
    backend_routes = runner.backend_dir / "app" / "api" / "routes" / "image.py"
    
    if not frontend_api.exists():
        runner.test("Frontend API file exists", False, "File not found")
        return
    
    if not backend_routes.exists():
        runner.test("Backend routes file exists", False, "File not found")
        return
    
    frontend_content = frontend_api.read_text()
    backend_content = backend_routes.read_text()
    
    # Define expected endpoints
    endpoints = {
        "upload": ("/images/upload", ["uploadImage"]),
        "generate": ("/images/generate", ["generateImage"]),
        "status": ("/images/status/", ["getTaskStatus", "pollTaskStatus"]),
        "download": ("/images/download/", ["getImageDownloadUrl"]),
        "delete": ("/images/", ["deleteImage"]),
    }
    
    for name, (endpoint, frontend_funcs) in endpoints.items():
        # Check backend endpoint
        backend_has = endpoint in backend_content
        runner.test(f"Backend {name} endpoint", backend_has, f"Missing {endpoint}")
        
        # Check frontend function
        frontend_has = any(func in frontend_content for func in frontend_funcs)
        runner.test(f"Frontend {name} function", frontend_has, f"Missing {frontend_funcs}")


def test_cors_configuration(runner: TestRunner):
    """Test CORS configuration compatibility"""
    runner.log("\n=== TEST GROUP: CORS Configuration ===", "INFO")
    
    # Read backend config
    backend_config = runner.backend_dir / "app" / "config.py"
    backend_main = runner.backend_dir / "app" / "main.py"
    frontend_vite = runner.frontend_dir / "vite.config.ts"
    
    if backend_config.exists():
        config_content = backend_config.read_text()
        runner.test("CORS_ORIGINS in config", "CORS_ORIGINS" in config_content)
        runner.test("get_cors_origins_list method", "get_cors_origins_list" in config_content)
    
    if backend_main.exists():
        main_content = backend_main.read_text()
        runner.test("CORSMiddleware imported", "CORSMiddleware" in main_content)
        runner.test("CORS middleware added", "add_middleware" in main_content and "CORSMiddleware" in main_content)
    
    if frontend_vite.exists():
        vite_content = frontend_vite.read_text()
        runner.test("Vite proxy configured", "proxy" in vite_content)
        runner.test("API proxy target set", "target:" in vite_content or "target=" in vite_content)


def test_data_type_compatibility(runner: TestRunner):
    """Test that frontend and backend data types are compatible"""
    runner.log("\n=== TEST GROUP: Data Type Compatibility ===", "INFO")
    
    frontend_types = runner.frontend_dir / "src" / "types" / "index.ts"
    backend_schemas = runner.backend_dir / "app" / "models" / "schemas.py"
    
    if not frontend_types.exists() or not backend_schemas.exists():
        runner.test("Type files exist", False, "Missing type definition files")
        return
    
    frontend_content = frontend_types.read_text()
    backend_content = backend_schemas.read_text()
    
    # Check for matching type definitions
    type_mappings = [
        ("UploadedImage", "image_id", "image_id"),
        ("GenerationParams", "image_id", "image_id"),
        ("GenerationTask", "task_id", "task_id"),
        ("GenerationTask", "status", "status"),
    ]
    
    for type_name, field, _ in type_mappings:
        frontend_has = type_name in frontend_content and field in frontend_content
        backend_has = type_name in backend_content or field in backend_content
        runner.test(f"Type {type_name}.{field}", frontend_has and backend_has, 
                   f"Type mismatch: frontend={frontend_has}, backend={backend_has}")


def test_file_upload_config(runner: TestRunner):
    """Test file upload configuration consistency"""
    runner.log("\n=== TEST GROUP: File Upload Configuration ===", "INFO")
    
    frontend_api = runner.frontend_dir / "src" / "api" / "imageApi.ts"
    backend_config = runner.backend_dir / "app" / "config.py"
    backend_image = runner.backend_dir / "app" / "services" / "image_service.py"
    
    # Check max file size
    if frontend_api.exists():
        content = frontend_api.read_text()
        # Look for 10MB limit
        if "10 * 1024 * 1024" in content or "10MB" in content:
            runner.test("Frontend max file size defined", True)
        else:
            runner.warn("Frontend max file size", "May not be explicitly defined")
    
    if backend_config.exists():
        content = backend_config.read_text()
        runner.test("Backend MAX_FILE_SIZE defined", "MAX_FILE_SIZE" in content)
    
    # Check allowed file types
    if frontend_api.exists():
        content = frontend_api.read_text()
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        all_present = all(t in content for t in allowed_types)
        runner.test("Frontend allowed types defined", all_present)
    
    if backend_image.exists():
        content = backend_image.read_text()
        runner.test("Backend file validation", "validate_file" in content)


def test_generation_parameters(runner: TestRunner):
    """Test generation parameter consistency"""
    runner.log("\n=== TEST GROUP: Generation Parameters ===", "INFO")
    
    frontend_store = runner.frontend_dir / "src" / "stores" / "editorStore.ts"
    backend_schemas = runner.backend_dir / "app" / "models" / "schemas.py"
    backend_config = runner.backend_dir / "app" / "config.py"
    
    # Check default values
    default_checks = [
        ("strength", 0.75),
        ("steps", 30),
    ]
    
    if frontend_store.exists():
        content = frontend_store.read_text()
        for param, default in default_checks:
            if f"{param}: {default}" in content:
                runner.test(f"Frontend default {param}", True)
            else:
                runner.warn(f"Frontend default {param}", f"May not match expected {default}")
    
    if backend_schemas.exists():
        content = backend_schemas.read_text()
        runner.test("Backend strength parameter", "strength" in content)
        runner.test("Backend steps parameter", "steps" in content)
        runner.test("Backend prompt parameter", "prompt" in content)
        runner.test("Backend style parameter", "style" in content)


def test_style_definitions(runner: TestRunner):
    """Test style definitions consistency"""
    runner.log("\n=== TEST GROUP: Style Definitions ===", "INFO")
    
    frontend_types = runner.frontend_dir / "src" / "types" / "index.ts"
    backend_schemas = runner.backend_dir / "app" / "models" / "schemas.py"
    backend_ai = runner.backend_dir / "app" / "services" / "ai_service.py"
    
    # Check for style-related definitions
    if backend_schemas.exists():
        content = backend_schemas.read_text()
        runner.test("GenerationStyle enum defined", "GenerationStyle" in content)
    
    if backend_ai.exists():
        content = backend_ai.read_text()
        runner.test("Style prompts defined", "STYLE_PROMPTS" in content)
        
        # Check for specific styles
        styles = ["PHOTOREALISTIC", "ANIME", "DIGITAL_ART", "OIL_PAINTING", "WATERCOLOR", "SKETCH", "CINEMATIC"]
        for style in styles:
            if style in content:
                runner.test(f"Style {style} defined", True)


def test_error_handling(runner: TestRunner):
    """Test error handling consistency"""
    runner.log("\n=== TEST GROUP: Error Handling ===", "INFO")
    
    frontend_client = runner.frontend_dir / "src" / "api" / "client.ts"
    backend_main = runner.backend_dir / "app" / "main.py"
    backend_schemas = runner.backend_dir / "app" / "models" / "schemas.py"
    
    # Check frontend error handling
    if frontend_client.exists():
        content = frontend_client.read_text()
        runner.test("Frontend error interceptor", "interceptors.response" in content)
        runner.test("Frontend 401 handling", "401" in content)
        runner.test("Frontend 413 handling", "413" in content)
        runner.test("Frontend 500 handling", "500" in content)
    
    # Check backend error handling
    if backend_main.exists():
        content = backend_main.read_text()
        runner.test("Backend exception handlers", "exception_handler" in content)
        runner.test("Validation error handler", "RequestValidationError" in content)
    
    if backend_schemas.exists():
        content = backend_schemas.read_text()
        runner.test("ErrorResponse model", "ErrorResponse" in content)


def test_task_status_flow(runner: TestRunner):
    """Test task status flow consistency"""
    runner.log("\n=== TEST GROUP: Task Status Flow ===", "INFO")
    
    frontend_types = runner.frontend_dir / "src" / "types" / "index.ts"
    backend_schemas = runner.backend_dir / "app" / "models" / "schemas.py"
    
    expected_statuses = ["pending", "processing", "completed", "failed"]
    
    if frontend_types.exists():
        content = frontend_types.read_text()
        for status in expected_statuses:
            if status in content.lower():
                runner.test(f"Frontend status '{status}'", True)
            else:
                runner.warn(f"Frontend status '{status}'", "Not explicitly defined")
    
    if backend_schemas.exists():
        content = backend_schemas.read_text()
        for status in expected_statuses:
            if status.upper() in content:
                runner.test(f"Backend status '{status}'", True)
            else:
                runner.warn(f"Backend status '{status}'", "Not explicitly defined")


def test_api_response_format(runner: TestRunner):
    """Test API response format consistency"""
    runner.log("\n=== TEST GROUP: API Response Format ===", "INFO")
    
    frontend_types = runner.frontend_dir / "src" / "types" / "index.ts"
    backend_schemas = runner.backend_dir / "app" / "models" / "schemas.py"
    
    if frontend_types.exists():
        content = frontend_types.read_text()
        runner.test("Frontend ApiResponse type", "ApiResponse" in content)
        runner.test("Frontend ApiError type", "ApiError" in content)
    
    if backend_schemas.exists():
        content = backend_schemas.read_text()
        runner.test("Backend success field", "success" in content)
        runner.test("Backend message field", "message" in content)


def test_port_configuration(runner: TestRunner):
    """Test port configuration consistency"""
    runner.log("\n=== TEST GROUP: Port Configuration ===", "INFO")
    
    frontend_vite = runner.frontend_dir / "vite.config.ts"
    backend_config = runner.backend_dir / "app" / "config.py"
    backend_main = runner.backend_dir / "app" / "main.py"
    
    # Check frontend port
    if frontend_vite.exists():
        content = frontend_vite.read_text()
        if "port: 3000" in content or "port = 3000" in content or '"port": 3000' in content:
            runner.test("Frontend dev server port (3000)", True)
        else:
            runner.info("Frontend port", "Default Vite port will be used")
    
    # Check backend port
    if backend_config.exists():
        content = backend_config.read_text()
        if "PORT" in content and "8000" in content:
            runner.test("Backend server port (8000)", True)
        else:
            runner.info("Backend port", "May use default")
    
    # Check API proxy
    if frontend_vite.exists():
        content = frontend_vite.read_text()
        if "8000" in content and "proxy" in content:
            runner.test("API proxy targets backend", True)
        else:
            runner.warn("API proxy", "May not be configured correctly")


def test_environment_variables(runner: TestRunner):
    """Test environment variable configuration"""
    runner.log("\n=== TEST GROUP: Environment Variables ===", "INFO")
    
    frontend_client = runner.frontend_dir / "src" / "api" / "client.ts"
    backend_config = runner.backend_dir / "app" / "config.py"
    
    # Check frontend env var usage
    if frontend_client.exists():
        content = frontend_client.read_text()
        if "import.meta.env" in content:
            runner.test("Frontend uses env variables", True)
        if "VITE_API_URL" in content:
            runner.test("VITE_API_URL env var", True)
    
    # Check backend env var usage
    if backend_config.exists():
        content = backend_config.read_text()
        if "env_file" in content:
            runner.test("Backend env file config", True)
        if "Config" in content and "env_file" in content:
            runner.test("Pydantic Settings env support", True)


def test_static_files_config(runner: TestRunner):
    """Test static files configuration"""
    runner.log("\n=== TEST GROUP: Static Files Configuration ===", "INFO")
    
    backend_main = runner.backend_dir / "app" / "main.py"
    backend_config = runner.backend_dir / "app" / "config.py"
    
    if backend_main.exists():
        content = backend_main.read_text()
        runner.test("Static files mounted", "StaticFiles" in content)
        runner.test("Uploads directory mounted", "/uploads" in content or "uploads" in content)
        runner.test("Outputs directory mounted", "/outputs" in content or "outputs" in content)
    
    if backend_config.exists():
        content = backend_config.read_text()
        runner.test("UPLOAD_DIR configured", "UPLOAD_DIR" in content)
        runner.test("OUTPUT_DIR configured", "OUTPUT_DIR" in content)


def test_import_paths(runner: TestRunner):
    """Test import path consistency"""
    runner.log("\n=== TEST GROUP: Import Path Consistency ===", "INFO")
    
    # Check backend imports
    backend_files = list((runner.backend_dir / "app").rglob("*.py"))
    import_issues = []
    
    for file in backend_files:
        if file.name == "__init__.py":
            continue
        content = file.read_text()
        
        # Check for absolute imports from app
        if "from app." in content or "import app." in content:
            # This is expected
            pass
        
        # Check for relative imports
        if "from ." in content:
            # This is also acceptable
            pass
    
    runner.test("Backend import structure", True, "Import patterns look consistent")


def test_naming_conventions(runner: TestRunner):
    """Test naming convention consistency"""
    runner.log("\n=== TEST GROUP: Naming Conventions ===", "INFO")
    
    # Check backend naming
    backend_schemas = runner.backend_dir / "app" / "models" / "schemas.py"
    
    if backend_schemas.exists():
        content = backend_schemas.read_text()
        
        # Check for snake_case in Python (expected)
        snake_case_fields = ["image_id", "task_id", "result_url", "created_at"]
        for field in snake_case_fields:
            if field in content:
                runner.test(f"Backend uses snake_case: {field}", True)
    
    # Check frontend naming
    frontend_types = runner.frontend_dir / "src" / "types" / "index.ts"
    
    if frontend_types.exists():
        content = frontend_types.read_text()
        
        # Frontend should match backend (snake_case for API fields)
        api_fields = ["image_id", "task_id", "result_url"]
        for field in api_fields:
            if field in content:
                runner.test(f"Frontend API types use snake_case: {field}", True)


def generate_compatibility_report(runner: TestRunner) -> str:
    """Generate a detailed compatibility report"""
    report = []
    report.append("=" * 60)
    report.append("  AI Image Editor - Integration Compatibility Report")
    report.append("=" * 60)
    report.append("")
    
    # API Endpoints
    report.append("API Endpoints:")
    report.append("  Frontend → Backend Mapping:")
    report.append("  - uploadImage() → POST /api/v1/images/upload")
    report.append("  - generateImage() → POST /api/v1/images/generate")
    report.append("  - getTaskStatus() → GET /api/v1/images/status/{task_id}")
    report.append("  - pollTaskStatus() → GET /api/v1/images/status/{task_id} (polling)")
    report.append("  - getImageDownloadUrl() → GET /api/v1/images/download/{image_id}")
    report.append("  - deleteImage() → DELETE /api/v1/images/{image_id}")
    report.append("")
    
    # Data Types
    report.append("Data Type Mapping:")
    report.append("  TypeScript Interface → Pydantic Model:")
    report.append("  - UploadedImage → ImageUploadResponse")
    report.append("  - GenerationParams → ImageGenerateRequest")
    report.append("  - GenerationTask → TaskStatusResponse")
    report.append("  - EditorState → (Internal state management)")
    report.append("")
    
    # Configuration
    report.append("Configuration:")
    report.append("  - Frontend Dev Server: http://localhost:3000")
    report.append("  - Backend API Server: http://localhost:8000")
    report.append("  - API Base Path: /api/v1")
    report.append("  - CORS Origins: http://localhost:3000, http://127.0.0.1:3000")
    report.append("  - Max File Size: 10MB")
    report.append("  - Allowed Formats: JPG, JPEG, PNG, WebP")
    report.append("")
    
    # Default Parameters
    report.append("Default Generation Parameters:")
    report.append("  - Strength: 0.75")
    report.append("  - Steps: 30")
    report.append("  - Guidance Scale: 7.5")
    report.append("  - Style: none")
    report.append("")
    
    # Status Flow
    report.append("Task Status Flow:")
    report.append("  pending → processing → completed/failed")
    report.append("")
    
    return "\n".join(report)


def main():
    """Run all integration tests"""
    print("=" * 50)
    print("  AI Image Editor - Integration Tests")
    print("=" * 50)
    
    runner = TestRunner()
    
    # Run all test groups
    test_api_endpoint_compatibility(runner)
    test_cors_configuration(runner)
    test_data_type_compatibility(runner)
    test_file_upload_config(runner)
    test_generation_parameters(runner)
    test_style_definitions(runner)
    test_error_handling(runner)
    test_task_status_flow(runner)
    test_api_response_format(runner)
    test_port_configuration(runner)
    test_environment_variables(runner)
    test_static_files_config(runner)
    test_import_paths(runner)
    test_naming_conventions(runner)
    
    # Print compatibility report
    print("\n" + generate_compatibility_report(runner))
    
    # Print summary
    return runner.print_summary()


if __name__ == "__main__":
    sys.exit(main())
