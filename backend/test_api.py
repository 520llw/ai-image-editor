#!/usr/bin/env python3
"""
API test script for AI Image Editor Backend
"""
import sys
import requests
import argparse
from pathlib import Path


def test_health(base_url: str) -> bool:
    """Test health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed")
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Device: {data.get('device')}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_root(base_url: str) -> bool:
    """Test root endpoint"""
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint OK")
            print(f"  Name: {data.get('name')}")
            print(f"  Version: {data.get('version')}")
            return True
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Root endpoint error: {e}")
        return False


def test_upload(base_url: str, image_path: str) -> str:
    """Test upload endpoint"""
    try:
        path = Path(image_path)
        if not path.exists():
            print(f"✗ File not found: {image_path}")
            return None
        
        with open(path, "rb") as f:
            files = {"file": (path.name, f, "image/jpeg")}
            response = requests.post(
                f"{base_url}/api/v1/images/upload",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Upload successful")
            print(f"  Image ID: {data.get('image_id')}")
            print(f"  URL: {data.get('url')}")
            print(f"  Size: {data.get('width')}x{data.get('height')}")
            return data.get('image_id')
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return None


def test_generate(base_url: str, image_id: str, prompt: str) -> str:
    """Test generate endpoint"""
    try:
        data = {
            "image_id": image_id,
            "prompt": prompt,
            "strength": 0.75,
            "steps": 20
        }
        response = requests.post(
            f"{base_url}/api/v1/images/generate",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Generation started")
            print(f"  Task ID: {data.get('task_id')}")
            print(f"  Status: {data.get('status')}")
            return data.get('task_id')
        else:
            print(f"✗ Generation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Generation error: {e}")
        return None


def test_status(base_url: str, task_id: str) -> bool:
    """Test status endpoint"""
    try:
        response = requests.get(
            f"{base_url}/api/v1/images/status/{task_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status check successful")
            print(f"  Task ID: {data.get('task_id')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Progress: {data.get('progress')}%")
            return True
        else:
            print(f"✗ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Status check error: {e}")
        return False


def test_models(base_url: str) -> bool:
    """Test models endpoint"""
    try:
        response = requests.get(
            f"{base_url}/api/v1/images/models/available",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Models endpoint OK")
            print(f"  Default model: {data.get('default_model')}")
            print(f"  Available models: {len(data.get('models', []))}")
            return True
        else:
            print(f"✗ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Models endpoint error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test AI Image Editor API")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--image",
        help="Path to test image for upload/generate tests"
    )
    parser.add_argument(
        "--prompt",
        default="make it look like a painting",
        help="Prompt for generation test"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full test suite including generation"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("AI Image Editor - API Test")
    print("=" * 50)
    print(f"Base URL: {args.url}\n")
    
    results = []
    
    # Basic tests
    results.append(("Root", test_root(args.url)))
    results.append(("Health", test_health(args.url)))
    results.append(("Models", test_models(args.url)))
    
    # Upload and generate tests
    if args.image and args.full:
        print("\n--- Upload Test ---")
        image_id = test_upload(args.url, args.image)
        
        if image_id:
            print("\n--- Generate Test ---")
            task_id = test_generate(args.url, image_id, args.prompt)
            
            if task_id:
                print("\n--- Status Test ---")
                results.append(("Status", test_status(args.url, task_id)))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
