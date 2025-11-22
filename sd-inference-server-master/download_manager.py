"""
Enhanced download manager with aria2c support for faster multi-threaded downloads
Supports: CivitAI, HuggingFace, Google Drive, Direct URLs
"""

import os
import subprocess
import requests
import re
import urllib.parse
import json
from urllib.parse import urlparse
import time

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'

class CivitaiMetadata:
    """Extract metadata from CivitAI models"""
    
    @staticmethod
    def get_model_info(url):
        """Get model info from CivitAI API"""
        try:
            if "civitai.com" in url:
                # Extract model version ID
                model_version_id = url.split('/')[-1]
                if "?modelVersionId=" in model_version_id:
                    match = re.search(r'modelVersionId=(\d+)', url)
                    model_version_id = match.group(1)
                
                endpoint_url = f"https://civitai.com/api/v1/model-versions/{model_version_id}"
            else:
                endpoint_url = f"https://civitai.com/api/v1/model-versions/by-hash/{url}"
            
            headers = {'User-Agent': USER_AGENT, 'content-type': 'application/json'}
            resp = requests.get(endpoint_url, headers=headers, timeout=5)
            resp.raise_for_status()
            
            data = resp.json()
            return {
                'filename': data.get('files', [{}])[0].get('name', ''),
                'download_url': data.get('downloadUrl', ''),
                'base_model': data.get('baseModel', ''),
                'trained_words': ', '.join(data.get('trainedWords', [])),
                'description': data.get('description', '')
            }
        except Exception as e:
            print(f"Error getting CivitAI metadata: {e}")
            return None

class DownloadManager:
    """Multi-source download manager with aria2c support"""
    
    def __init__(self, use_aria2c=True, max_connections=16):
        self.use_aria2c = use_aria2c and self._check_aria2c()
        self.max_connections = max_connections
        self.max_chunk_size = "1M"
    
    @staticmethod
    def _check_aria2c():
        """Check if aria2c is installed"""
        try:
            subprocess.run(['aria2c', '--version'], 
                         capture_output=True, 
                         timeout=5,
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            print("⚠️ aria2c not found. Falling back to standard requests.")
            return False
    
    def get_filename_from_url(self, url):
        """Extract filename from URL - fast version without HEAD request"""
        try:
            # Parse URL to get path
            parsed = urlparse(url)
            
            # Get filename from path
            filename = parsed.path.split('/')[-1]
            
            # If filename is empty, try query parameters
            if not filename or filename in ['download', 'api']:
                # Try to extract from query parameters
                query_params = urllib.parse.parse_qs(parsed.query)
                if 'filename' in query_params:
                    filename = query_params['filename'][0]
                elif 'name' in query_params:
                    filename = query_params['name'][0]
            
            # URL decode
            if filename:
                filename = urllib.parse.unquote(filename)
                # Clean up CivitAI and other special formats
                if filename.endswith('?type=Model'):
                    filename = filename.replace('?type=Model', '')
                return filename
        except Exception as e:
            print(f"[DownloadManager] Error parsing filename: {e}")
        
        # Last resort - generate based on URL
        try:
            model_id = url.split('/')[-1].split('?')[0]
            if model_id and model_id != 'download':
                return f"model_{model_id}"
        except:
            pass
        
        return "downloaded_file"
    
    def download_with_aria2c(self, url, output_dir, filename=None, headers=None, 
                            progress_callback=None):
        """Download using aria2c for multi-threaded downloads"""
        if not self.use_aria2c:
            return self.download_with_requests(url, output_dir, filename, headers, 
                                              progress_callback)
        
        os.makedirs(output_dir, exist_ok=True)
        
        if not filename:
            filename = self.get_filename_from_url(url)
        
        output_path = os.path.join(output_dir, filename)
        
        # Check if already downloaded
        if os.path.exists(output_path):
            print(f"✓ File already exists: {output_path}")
            return output_path
        
        print(f"📥 Downloading with aria2c: {filename}")
        
        cmd = [
            'aria2c',
            '--console-log-level=error',
            '--summary-interval=1',
            '-c',  # Continue incomplete downloads
            '-x', str(self.max_connections),  # Max concurrent connections
            '-k', self.max_chunk_size,  # Minimum chunk size
            '-s', str(self.max_connections),  # Split
            '-d', output_dir,
            '-o', filename
        ]
        
        # Add headers if provided
        if headers:
            for key, value in headers.items():
                cmd.extend(['--header', f'{key}: {value}'])
        
        cmd.append(url)
        
        try:
            process = subprocess.Popen(cmd, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      text=True)
            
            # Monitor download progress
            for line in process.stderr:
                if progress_callback and '%' in line:
                    try:
                        progress_match = re.search(r'(\d+)%', line)
                        if progress_match:
                            progress = int(progress_match.group(1)) / 100.0
                            progress_callback({'progress': progress, 'status': line.strip()})
                    except:
                        pass
            
            returncode = process.wait()
            
            if returncode == 0 and os.path.exists(output_path):
                print(f"✓ Download completed: {output_path}")
                return output_path
            else:
                raise RuntimeError(f"aria2c download failed with code {returncode}")
        
        except Exception as e:
            print(f"❌ aria2c download failed: {e}")
            # Fallback to requests
            return self.download_with_requests(url, output_dir, filename, headers, 
                                              progress_callback)
    
    def download_with_requests(self, url, output_dir, filename=None, headers=None, 
                              progress_callback=None):
        """Fallback: Download using requests library"""
        os.makedirs(output_dir, exist_ok=True)
        
        if not filename:
            filename = self.get_filename_from_url(url)
        
        output_path = os.path.join(output_dir, filename)
        
        # Check if already downloaded
        if os.path.exists(output_path):
            print(f"✓ File already exists: {output_path}")
            if progress_callback:
                progress_callback({'status': 'info', 'message': 'File already exists'})
            return output_path
        
        print(f"📥 Downloading with requests: {filename}")
        
        try:
            # Send starting signal
            if progress_callback:
                progress_callback({'status': 'info', 'message': f'Downloading {filename}...'})
            
            default_headers = {'User-Agent': USER_AGENT}
            if headers:
                default_headers.update(headers)
            
            resp = requests.get(url, stream=True, timeout=30, 
                              headers=default_headers, allow_redirects=True)
            resp.raise_for_status()
            
            total_size = int(resp.headers.get('content-length', 0))
            downloaded = 0
            last_update = 0
            update_interval = 0.5  # Update every 0.5 seconds
            start_time = time.time()
            
            with open(output_path + '.tmp', 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Send progress updates
                        if progress_callback:
                            current_time = time.time()
                            if current_time - last_update >= update_interval:
                                elapsed = current_time - start_time
                                if total_size > 0:
                                    progress = min(1.0, downloaded / total_size)
                                    speed_bps = downloaded / max(elapsed, 1)
                                    speed_str = f"{speed_bps / (1024*1024):.2f} MB/s"
                                else:
                                    progress = 0
                                    speed_str = "? MB/s"
                                
                                progress_callback({
                                    'progress': progress,
                                    'downloaded': downloaded,
                                    'total': total_size,
                                    'speed': speed_str
                                })
                                last_update = current_time
            
            os.rename(output_path + '.tmp', output_path)
            print(f"✓ Download completed: {output_path}")
            
            if progress_callback:
                progress_callback({'status': 'completed', 'progress': 1.0})
            
            return output_path
        
        except Exception as e:
            print(f"❌ Download failed: {e}")
            if progress_callback:
                progress_callback({'status': 'error', 'error': str(e)})
            if os.path.exists(output_path + '.tmp'):
                os.remove(output_path + '.tmp')
            raise
    
    def download(self, url, output_dir, filename=None, headers=None, 
                progress_callback=None, civitai_token=None, hf_token=None):
        """
        Smart download function that handles different sources
        """
        # Prepare headers
        final_headers = {}
        
        # CivitAI handling
        if 'civitai.com' in url:
            if civitai_token:
                final_headers['Authorization'] = f'Bearer {civitai_token}'
        
        # HuggingFace handling
        if 'huggingface.co' in url:
            if hf_token:
                final_headers['Authorization'] = f'Bearer {hf_token}'
            if '/blob/' in url:
                url = url.replace('/blob/', '/resolve/')
        
        if headers:
            final_headers.update(headers)
        
        # Download
        if self.use_aria2c:
            return self.download_with_aria2c(url, output_dir, filename, 
                                           final_headers, progress_callback)
        else:
            return self.download_with_requests(url, output_dir, filename, 
                                              final_headers, progress_callback)


# Create global instance
download_manager = DownloadManager()


def download_model(url, model_type, folder, progress_callback=None, 
                  civitai_token=None, hf_token=None):
    """
    High-level function for downloading models
    
    Args:
        url: Download URL
        model_type: 'checkpoint', 'lora', 'upscaler', etc.
        folder: Base folder path
        progress_callback: Function to call with progress updates
        civitai_token: CivitAI API token
        hf_token: HuggingFace token
    
    Returns:
        Path to downloaded file or None
    """
    output_dir = os.path.join(folder, model_type)
    
    try:
        # Report starting
        if progress_callback:
            progress_callback({'status': 'info', 'message': f'Preparing download from {url[:50]}...'})
        
        filename = None
        
        # Extract CivitAI metadata if needed
        if 'civitai.com' in url and not filename:
            try:
                metadata = CivitaiMetadata.get_model_info(url)
                if metadata:
                    filename = metadata['filename']
                    if progress_callback:
                        progress_callback({
                            'status': 'metadata',
                            'info': metadata
                        })
            except Exception as e:
                print(f"[DownloadManager] Could not get CivitAI metadata: {e}")
        
        print(f"[DownloadManager] Starting download: {url}")
        print(f"[DownloadManager] Model type: {model_type}, Output dir: {output_dir}")
        print(f"[DownloadManager] Filename: {filename}")
        
        # Download file
        result = download_manager.download(
            url=url,
            output_dir=output_dir,
            filename=filename,
            progress_callback=progress_callback,
            civitai_token=civitai_token,
            hf_token=hf_token
        )
        
        print(f"[DownloadManager] Download result: {result}")
        
        return result
    
    except Exception as e:
        print(f"❌ Download failed: {e}")
        import traceback
        traceback.print_exc()
        if progress_callback:
            progress_callback({
                'status': 'error',
                'error': str(e)
            })
        return None
