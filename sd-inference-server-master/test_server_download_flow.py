#!/usr/bin/env python3
"""
Test the complete server.py download callback chain
"""

import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import download_manager
import json

def simulate_server_download(url, model_type, civitai_token=None, hf_token=None):
    """Simulate what server.py does"""
    
    print("=" * 70)
    print("SIMULATING SERVER.PY DOWNLOAD FLOW")
    print("=" * 70)
    
    # Simulate storage path
    storage_path = os.path.join(os.path.dirname(__file__), 'test_models')
    os.makedirs(storage_path, exist_ok=True)
    
    # This is what server.py creates as folder
    folder = os.path.join(storage_path, model_type)
    
    # Get base_folder like server.py does
    base_folder = os.path.dirname(folder)  # Back to storage_path
    
    print(f"\n[SERVER] Settings:")
    print(f"  Storage path: {storage_path}")
    print(f"  Model type: {model_type}")
    print(f"  Folder: {folder}")
    print(f"  Base folder: {base_folder}")
    
    # Callback to simulate WebSocket send
    callback_count = 0
    
    def progress_callback(progress_data):
        nonlocal callback_count
        callback_count += 1
        
        status = progress_data.get('status', 'unknown')
        print(f"\n[CALLBACK #{callback_count}] Status: {status}")
        
        # Simulate what server.py does with progress_callback
        if status == 'metadata':
            info = progress_data.get('info', {})
            message = {
                "type": "download",
                "data": {
                    "status": "metadata",
                    "base_model": info.get('base_model', ''),
                    "trained_words": info.get('trained_words', '')
                }
            }
            print(f"  Would send to client: {json.dumps(message, indent=2)}")
        
        elif 'progress' in progress_data or 'downloaded' in progress_data:
            progress = progress_data.get('progress', 0)
            downloaded = progress_data.get('downloaded', 0)
            total = progress_data.get('total', 0)
            
            # Convert to 0-1 range if needed
            if isinstance(progress, str):
                try:
                    progress = float(progress.replace('%', '')) / 100
                except:
                    progress = 0
            elif total > 0:
                progress = min(1.0, downloaded / total)
            
            rate_str = progress_data.get('speed', '0 KB/s')
            try:
                if 'MB' in rate_str:
                    rate = float(rate_str.replace('MB/s', ''))
                elif 'KB' in rate_str:
                    rate = float(rate_str.replace('KB/s', '')) / 1024
                else:
                    rate = 0
            except:
                rate = 0
            
            if downloaded > 0 and total > downloaded:
                bytes_per_sec = max(rate * 1024 * 1024, 1)
                eta = int((total - downloaded) / bytes_per_sec)
            else:
                eta = 0
            
            message = {
                "type": "download",
                "data": {
                    "status": "progress",
                    "progress": min(1.0, progress),
                    "rate": rate,
                    "eta": eta,
                    "downloaded": downloaded,
                    "total": total
                }
            }
            print(f"  Downloaded: {downloaded}/{total} ({progress*100:.1f}%)")
            print(f"  Speed: {rate_str}, ETA: {eta}s")
            print(f"  Would send to client: {json.dumps(message, indent=2)}")
        
        elif status == 'error':
            message = {
                "type": "download",
                "data": {
                    "status": "error",
                    "message": progress_data.get('error', 'Unknown error')
                }
            }
            print(f"  Would send to client: {json.dumps(message, indent=2)}")
        
        elif status == 'info':
            message = {
                "type": "download",
                "data": {
                    "status": "info",
                    "message": progress_data.get('message', '')
                }
            }
            print(f"  Message: {progress_data.get('message', '')}")
    
    # Call download_model like server.py does
    print(f"\n[SERVER] Starting download_model()...")
    
    filename = download_manager.download_model(
        url=url,
        model_type=model_type,
        folder=base_folder,
        progress_callback=progress_callback,
        civitai_token=civitai_token,
        hf_token=hf_token
    )
    
    print(f"\n[SERVER] Download completed!")
    print(f"  Result: {filename}")
    print(f"  Total callbacks: {callback_count}")
    
    if filename:
        print(f"  File size: {os.path.getsize(filename)} bytes")
        return True
    else:
        print("  ❌ Download failed!")
        return False

def main():
    # Test with HuggingFace (no token needed for public models)
    test_url = "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/vae/config.json"
    
    success = simulate_server_download(
        url=test_url,
        model_type="checkpoint"
    )
    
    print("\n" + "=" * 70)
    if success:
        print("✅ TEST PASSED: Download and callback chain working!")
    else:
        print("❌ TEST FAILED")
    print("=" * 70)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
