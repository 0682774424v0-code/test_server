%cd /content/sd-inference-server

#@title 📥 Download Models (Checkpoints, LoRAs, VAEs, Upscalers)

import os
import requests
import urllib.parse
import re
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# ============================================================================
# Configuration
# ============================================================================

# URLs separated by commas
#@markdown #### 📦 Model Downloads

#@markdown **Checkpoints & Base Models** (Stable Diffusion, SDXL, etc.)
download_checkpoints = "https://huggingface.co/frankjoshua/toonyou_beta6/resolve/main/toonyou_beta6.safetensors"  # @param {type:"string"}

#@markdown **LoRA Models** (Style & character LoRAs)
download_loras = ""  # @param {type:"string"}

#@markdown **VAE Models** (Variational Autoencoders)
download_vaes = ""  # @param {type:"string"}

#@markdown **Upscalers** (Image upscaling models)
download_upscalers = ""  # @param {type:"string"}

#@markdown #### 🔐 Authentication Tokens

#@markdown **CivitAI API Key** (Get from: https://civitai.com/account/api-tokens)
CIVITAI_API_KEY = ""  # @param {type:"string"}

#@markdown **HuggingFace Token** (Get from: https://huggingface.co/settings/tokens)
HF_TOKEN = ""  # @param {type:"string"}

# ============================================================================
# Download Manager Implementation
# ============================================================================

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'

class DownloadManager:
    """Enhanced download manager with aria2c support"""
    
    def __init__(self):
        self.use_aria2c = self._check_aria2c()
    
    @staticmethod
    def _check_aria2c():
        """Check if aria2c is available"""
        try:
            import subprocess
            subprocess.run(['aria2c', '--version'], capture_output=True, timeout=5, check=True)
            print("✅ aria2c available - will use for FAST downloads")
            return True
        except:
            print("ℹ️  aria2c not available - using standard download")
            return False
    
    def get_filename_from_url(self, url):
        """Extract filename from URL"""
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True, headers={'User-Agent': USER_AGENT})
            content_disposition = resp.headers.get('content-disposition', '')
            if content_disposition:
                match = re.search(r'filename[^;=\n]*=(["\']?)([^";\n]*)\1', content_disposition)
                if match:
                    return match.group(2)
            
            parsed_url = urllib.parse.urlparse(url)
            filename = parsed_url.path.split('/')[-1]
            if filename:
                return urllib.parse.unquote(filename)
        except:
            pass
        return "downloaded_file"
    
    def download_with_aria2c(self, url, output_dir, filename):
        """Download using aria2c (16 parallel connections)"""
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        if os.path.exists(output_path):
            print(f"✅ File already exists: {filename}")
            return output_path
        
        print(f"📥 Downloading with aria2c: {filename}")
        cmd = f'aria2c --console-log-level=error --summary-interval=1 -c -x 16 -k 1M -s 16 -d "{output_dir}" -o "{filename}" "{url}"'
        
        try:
            os.system(cmd)
            if os.path.exists(output_path):
                print(f"✅ Downloaded: {filename}")
                return output_path
        except Exception as e:
            print(f"⚠️  aria2c failed: {e}, trying standard download...")
        
        return self.download_with_requests(url, output_dir, filename)
    
    def download_with_requests(self, url, output_dir, filename):
        """Standard download using requests"""
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        if os.path.exists(output_path):
            print(f"✅ File already exists: {filename}")
            return output_path
        
        print(f"📥 Downloading: {filename}")
        
        try:
            session = requests.Session()
            retry = Retry(total=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            
            resp = session.get(url, stream=True, timeout=30, headers={'User-Agent': USER_AGENT}, allow_redirects=True)
            resp.raise_for_status()
            
            total_size = int(resp.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path + '.tmp', 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"  Progress: {progress:.1f}%", end='\r')
            
            os.rename(output_path + '.tmp', output_path)
            print(f"✅ Downloaded: {filename}")
            return output_path
        except Exception as e:
            print(f"❌ Download failed: {e}")
            if os.path.exists(output_path + '.tmp'):
                os.remove(output_path + '.tmp')
            return None
    
    def download(self, url, model_type, civitai_token=None, hf_token=None):
        """Main download function"""
        if not url.strip():
            return None
        
        # Determine output directory
        dir_map = {
            'checkpoint': 'models',
            'lora': 'loras',
            'vae': 'vaes',
            'upscaler': 'upscalers'
        }
        output_dir = dir_map.get(model_type, 'models')
        
        # Prepare URL and headers
        final_url = url.strip()
        headers = {}
        
        # CivitAI handling
        if 'civitai.com' in final_url:
            if civitai_token:
                headers['Authorization'] = f'Bearer {civitai_token}'
            print(f"🎨 Downloading from CivitAI...")
        
        # HuggingFace handling
        elif 'huggingface.co' in final_url:
            if '/blob/' in final_url:
                final_url = final_url.replace('/blob/', '/resolve/')
            if hf_token:
                headers['Authorization'] = f'Bearer {hf_token}'
            print(f"🤗 Downloading from HuggingFace...")
        
        # Google Drive
        elif 'drive.google.com' in final_url:
            print(f"📁 Downloading from Google Drive...")
        
        # Get filename
        filename = self.get_filename_from_url(final_url)
        
        # Download
        if self.use_aria2c:
            return self.download_with_aria2c(final_url, output_dir, filename)
        else:
            return self.download_with_requests(final_url, output_dir, filename)

# ============================================================================
# Execute Downloads
# ============================================================================

print("\n" + "=" * 60)
print("📥 DOWNLOADING MODELS")
print("=" * 60)

dm = DownloadManager()

# Download checkpoints
if download_checkpoints.strip():
    print("\n🤖 Downloading Checkpoints...")
    for url in download_checkpoints.split(','):
        dm.download(url.strip(), 'checkpoint', CIVITAI_API_KEY, HF_TOKEN)

# Download LoRAs
if download_loras.strip():
    print("\n🎨 Downloading LoRAs...")
    for url in download_loras.split(','):
        dm.download(url.strip(), 'lora', CIVITAI_API_KEY, HF_TOKEN)

# Download VAEs
if download_vaes.strip():
    print("\n🔧 Downloading VAEs...")
    for url in download_vaes.split(','):
        dm.download(url.strip(), 'vae', CIVITAI_API_KEY, HF_TOKEN)

# Download Upscalers
if download_upscalers.strip():
    print("\n📈 Downloading Upscalers...")
    for url in download_upscalers.split(','):
        dm.download(url.strip(), 'upscaler', CIVITAI_API_KEY, HF_TOKEN)

print("\n" + "=" * 60)
print("✅ DOWNLOADS COMPLETE!")
print("=" * 60)

# List downloaded models
print("\n📂 Available Models:")
for model_type, folder in [('Checkpoints', 'models'), ('LoRAs', 'loras'), ('VAEs', 'vaes'), ('Upscalers', 'upscalers')]:
    if os.path.exists(folder):
        files = [f for f in os.listdir(folder) if f.endswith(('.safetensors', '.ckpt', '.pt', '.pth'))]
        if files:
            print(f"\n{model_type}:")
            for f in files:
                size = os.path.getsize(os.path.join(folder, f)) / (1024**3)
                print(f"  • {f} ({size:.2f} GB)")
