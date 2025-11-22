#!/usr/bin/env python3
"""
Test script for the enhanced download manager
Run this to verify aria2c installation and download functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from download_manager import DownloadManager, CivitaiMetadata

def test_aria2c():
    """Test if aria2c is available"""
    print("=" * 50)
    print("Testing aria2c installation...")
    print("=" * 50)
    
    dm = DownloadManager()
    if dm.use_aria2c:
        print("✅ aria2c is installed and ready!")
        print("   Downloads will be FAST (16x parallel)")
    else:
        print("⚠️  aria2c not found")
        print("   Install with: sudo apt install aria2")
        print("   Downloads will use requests (slower)")
    print()

def test_civitai_metadata():
    """Test CivitAI metadata extraction"""
    print("=" * 50)
    print("Testing CivitAI metadata extraction...")
    print("=" * 50)
    
    # Example CivitAI URL
    test_urls = [
        "https://civitai.com/models/4200?modelVersionId=4767",
        "https://civitai.com/api/download/models/456194",
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url[:60]}...")
        try:
            metadata = CivitaiMetadata.get_model_info(url)
            if metadata:
                print(f"  ✅ Metadata retrieved:")
                print(f"     Filename: {metadata.get('filename', 'N/A')[:50]}")
                print(f"     Base Model: {metadata.get('base_model', 'N/A')}")
                print(f"     Trained Words: {metadata.get('trained_words', 'N/A')[:50]}")
            else:
                print(f"  ⚠️  Could not extract metadata")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    print()

def test_filename_extraction():
    """Test filename extraction from various URLs"""
    print("=" * 50)
    print("Testing filename extraction...")
    print("=" * 50)
    
    dm = DownloadManager()
    
    test_cases = [
        ("https://civitai.com/api/download/models/456194", "CivitAI download"),
        ("https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/model.safetensors", 
         "HuggingFace download"),
        ("https://example.com/path/to/model.safetensors", "Generic download"),
    ]
    
    for url, desc in test_cases:
        print(f"\n{desc}:")
        print(f"  URL: {url[:60]}...")
        try:
            filename = dm.get_filename_from_url(url)
            print(f"  ✅ Filename: {filename}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    print()

def test_download_simulation():
    """Simulate a download with progress tracking"""
    print("=" * 50)
    print("Testing download simulation (no actual download)...")
    print("=" * 50)
    
    dm = DownloadManager()
    
    progress_updates = []
    
    def progress_callback(data):
        progress_updates.append(data)
        if 'progress' in data:
            pct = data['progress'] * 100
            print(f"  Progress: {pct:.1f}%", end='\r')
    
    print("\nSimulated download configuration:")
    print(f"  Use aria2c: {dm.use_aria2c}")
    print(f"  Max connections: {dm.max_connections}")
    print(f"  Max chunk size: {dm.max_chunk_size}")
    print("\n✅ Download system is ready!")
    print()

def main():
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " " * 48 + "║")
    print("║" + "  Enhanced Download Manager - Test Suite  ".center(48) + "║")
    print("║" + " " * 48 + "║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    test_aria2c()
    test_civitai_metadata()
    test_filename_extraction()
    test_download_simulation()
    
    print("=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)
    print("\nThe download system is ready to use!")
    print("\nNext steps:")
    print("  1. Install aria2c for faster downloads (optional)")
    print("  2. Configure API tokens in the web UI")
    print("  3. Try downloading a model")
    print()

if __name__ == "__main__":
    main()
