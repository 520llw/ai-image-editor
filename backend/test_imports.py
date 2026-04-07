#!/usr/bin/env python3
"""
Test script to verify all modules can be imported correctly.
Run this after installing requirements: pip install -r requirements.txt
"""
import sys

def test_imports():
    """Test all module imports"""
    errors = []
    
    print("Testing module imports...\n")
    
    # Test config
    try:
        from app.config import settings
        print("✓ app.config imported successfully")
    except Exception as e:
        errors.append(f"✗ app.config: {e}")
    
    # Test schemas
    try:
        from app.models.schemas import (
            ImageUploadResponse, 
            ImageGenerateRequest,
            TaskStatus,
            GenerationStyle
        )
        print("✓ app.models.schemas imported successfully")
    except Exception as e:
        errors.append(f"✗ app.models.schemas: {e}")
    
    # Test image service
    try:
        from app.services.image_service import image_service
        print("✓ app.services.image_service imported successfully")
    except Exception as e:
        errors.append(f"✗ app.services.image_service: {e}")
    
    # Test AI service
    try:
        from app.services.ai_service import ai_service
        print("✓ app.services.ai_service imported successfully")
    except Exception as e:
        errors.append(f"✗ app.services.ai_service: {e}")
    
    # Test image routes
    try:
        from app.api.routes.image import router
        print("✓ app.api.routes.image imported successfully")
    except Exception as e:
        errors.append(f"✗ app.api.routes.image: {e}")
    
    # Test main
    try:
        from app.main import app
        print("✓ app.main imported successfully")
    except Exception as e:
        errors.append(f"✗ app.main: {e}")
    
    print()
    
    if errors:
        print("Errors found:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✓ All modules imported successfully!")
        print("\nYou can now start the server with:")
        print("  uvicorn app.main:app --reload")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
