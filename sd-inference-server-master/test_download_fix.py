#!/usr/bin/env python3
"""
Test script to verify download_manager fixes
"""

import os
import sys
import time

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import download_manager

def test_callback(data):
    """Test progress callback"""
    status = data.get('status', 'unknown')
    print(f"[CALLBACK] Status: {status}")
    
    if status == 'info':
        print(f"  → {data.get('message', '')}")
    elif status == 'metadata':
        info = data.get('info', {})
        print(f"  → Base Model: {info.get('base_model', 'N/A')}")
        print(f"  → Trained Words: {info.get('trained_words', 'N/A')}")
    elif status == 'progress':
        progress = data.get('progress', 0)
        downloaded = data.get('downloaded', 0)
        total = data.get('total', 0)
        speed = data.get('speed', '? MB/s')
        eta = data.get('eta', 0)
        print(f"  → Progress: {progress*100:.1f}% ({downloaded}/{total} bytes)")
        print(f"  → Speed: {speed}")
        print(f"  → ETA: {eta}s")
    elif status == 'completed':
        print(f"  → Download completed!")
    elif status == 'error':
        print(f"  → ERROR: {data.get('error', 'Unknown error')}")

def main():
    print("=" * 60)
    print("Testing download_manager fixes")
    print("=" * 60)
    
    # Test URL (small file)
    test_url = "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/vae/config.json"
    
    print(f"\n[TEST] Downloading test file...")
    print(f"  URL: {test_url}")
    
    # Create test directory
    test_dir = os.path.join(os.path.dirname(__file__), 'test_downloads')
    os.makedirs(test_dir, exist_ok=True)
    
    # Test download
    result = download_manager.download_model(
        url=test_url,
        model_type='test',
        folder=test_dir,
        progress_callback=test_callback
    )
    
    if result:
        print(f"\n✅ Download successful!")
        print(f"  File: {result}")
        print(f"  Size: {os.path.getsize(result)} bytes")
    else:
        print(f"\n❌ Download failed!")
        return 1
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
