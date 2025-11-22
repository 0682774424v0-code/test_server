# 🚀 Minimal Colab Copy-Paste Example

## Simplest Setup Ever

Just copy & paste these two cells into Google Colab!

---

## 📋 CELL 1: Run This First

```python
# @title 🚀 SD Server Setup
%cd /content

import IPython.display, os, sys, random, string, urllib.parse, subprocess, threading, time, re, socket

# Clone repo
if not os.path.exists("/content/sd-inference-server"):
    !git clone https://github.com/0682774424v0-code/test_server.git /content/sd-inference-server
    
%cd /content/sd-inference-server
!git pull origin main >/dev/null 2>&1

# Install if needed
if not os.path.exists("deps_installed"):
    print("📦 Installing dependencies...")
    !pip install -q diffusers==0.27.2 k_diffusion==0.0.15 spandrel==0.4.1 lark==1.1.5 transformers==4.36.2 websockets==11.0.3 bson==0.5.10 mega.py==1.0.8 pytorch-lightning==2.0.2 timm==0.9.2 tomesd==0.1.3 pycloudflared==0.2.0 segment-anything==1.0 geffnet==1.0.2 toml==0.10.2 voluptuous==0.13.1 accelerate==0.27.2 lycoris-lora==2.3.0.dev4 ultralytics==8.2.3 huggingface_hub==0.25.1 requests urllib3 2>/dev/null
    !apt -y install -qq aria2 >/dev/null 2>&1
    !wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
    !chmod +x cloudflared
    !touch deps_installed
    IPython.display.clear_output()

sys.path.insert(0, "/content/sd-inference-server/")

# Password
password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
print(f"🔐 Password: {password}\n")

# Tunnel thread
stopping = False
def tunnel_thread():
    while True:
        time.sleep(0.1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex(('127.0.0.1', 28888)) == 0:
            break
        sock.close()
    
    time.sleep(1)
    url_pattern = re.compile(r"(?P<url>https?://\S+\.trycloudflare\.com)")
    p = subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://127.0.0.1:28888"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, encoding="utf-8")
    
    for line in p.stderr:
        url_match = url_pattern.search(line)
        if url_match:
            tunnel_url = url_match.group("url")
            endpoint = tunnel_url.replace("https", "wss").strip()
            
            print("=" * 60)
            print("🎉 SERVER READY!")
            print("=" * 60)
            print(f"📍 Endpoint: {endpoint}")
            print(f"🔐 Password: {password}")
            print(f"\n🌐 Web UI:")
            web_url = f"https://arenasys.github.io/?endpoint={urllib.parse.quote(endpoint, safe='')}&password={password}"
            print(f"   {web_url}")
            print(f"\n💻 Desktop Client:")
            desktop_uri = f"qdiffusion:?endpoint={urllib.parse.quote(endpoint, safe='')}&password={password}"
            print(f"   {desktop_uri}")
            print("=" * 60)
            break
    
    while not stopping:
        time.sleep(0.1)
    p.kill()

threading.Thread(target=tunnel_thread, daemon=True).start()

# Start server
os.chdir("/content/sd-inference-server")
model_folder = "/content/sd-inference-server/models"

try:
    !python sd-inference-server-master/server.py --models "$model_folder" --password "$password"
except KeyboardInterrupt:
    stopping = True
    print("\n⚠️  Server stopped")
```

---

## 📥 CELL 2: Download Models (Optional)

```python
# @title 📥 Download Models
%cd /content/sd-inference-server

import os, requests, urllib.parse, re
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# CONFIGURE HERE:
download_checkpoints = "https://huggingface.co/frankjoshua/toonyou_beta6/resolve/main/toonyou_beta6.safetensors"  # Models
download_loras = ""  # LoRAs (comma-separated)
CIVITAI_API_KEY = ""  # From: civitai.com/account/api-tokens
HF_TOKEN = ""  # From: huggingface.co/settings/tokens

# Download function
class DL:
    def __init__(self):
        self.aria2c = self._check_aria2c()
    
    @staticmethod
    def _check_aria2c():
        try:
            import subprocess
            subprocess.run(['aria2c', '--version'], capture_output=True, timeout=5, check=True)
            return True
        except:
            return False
    
    def get_filename(self, url):
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            cd = resp.headers.get('content-disposition', '')
            match = re.search(r'filename[^;=\n]*=(["\']?)([^";\n]*)\1', cd)
            if match:
                return match.group(2)
            return urllib.parse.urlparse(url).path.split('/')[-1] or "file"
        except:
            return "file"
    
    def download(self, url, typ, civitai_token=None, hf_token=None):
        if not url.strip():
            return
        
        dirs = {'checkpoint': 'models', 'lora': 'loras', 'vae': 'vaes', 'upscaler': 'upscalers'}
        outdir = dirs.get(typ, 'models')
        os.makedirs(outdir, exist_ok=True)
        
        filename = self.get_filename(url)
        outpath = os.path.join(outdir, filename)
        
        if os.path.exists(outpath):
            print(f"✅ Already exists: {filename}")
            return
        
        print(f"📥 Downloading: {filename}...")
        
        if self.aria2c:
            cmd = f'aria2c --console-log-level=error -c -x 16 -k 1M -s 16 -d "{outdir}" -o "{filename}" "{url}"'
            os.system(cmd)
        else:
            resp = requests.get(url, stream=True, timeout=30, allow_redirects=True)
            with open(outpath + '.tmp', 'wb') as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)
            os.rename(outpath + '.tmp', outpath)
        
        print(f"✅ Done: {filename}")

dm = DL()

print("\n" + "="*60)
print("📥 DOWNLOADING MODELS")
print("="*60)

for url in download_checkpoints.split(','):
    if url.strip():
        dm.download(url.strip(), 'checkpoint', CIVITAI_API_KEY, HF_TOKEN)

for url in download_loras.split(','):
    if url.strip():
        dm.download(url.strip(), 'lora', CIVITAI_API_KEY, HF_TOKEN)

print("\n✅ DONE!")
```

---

## 🎯 How to Use

### Step 1: Create Colab Notebook
- Go to [colab.research.google.com](https://colab.research.google.com)
- New Notebook

### Step 2: Enable GPU
- Runtime → Change Runtime Type → GPU

### Step 3: Copy Cell 1
- Create new cell
- Copy entire Cell 1 code above
- Run (Ctrl+Enter)
- Wait 2-3 minutes

### Step 4: Get Connection Info
Look for output like:
```
📍 Endpoint: wss://xxxxx.trycloudflare.com
🔐 Password: AbCd1234
🌐 Web UI: https://arenasys.github.io/?endpoint=...
💻 Desktop: qdiffusion:?endpoint=...
```

### Step 5: Copy Cell 2 (Optional - for models)
- Create new cell
- Copy entire Cell 2 code above
- Edit configuration at top:
  ```python
  download_checkpoints = "your_url_here"
  CIVITAI_API_KEY = "your_key_here"  # Optional
  ```
- Run (Ctrl+Enter)
- Wait for downloads

### Step 6: Connect
- Use endpoint in your qDiffusion app
- Or open Web UI link
- Enter password

---

## 📝 Example URLs

### CivitAI
```
https://civitai.com/api/download/models/456194
```

### HuggingFace
```
https://huggingface.co/frankjoshua/toonyou_beta6/resolve/main/toonyou_beta6.safetensors
```

### Multiple (comma-separated)
```
url1, url2, url3
```

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| First setup | 3-5 min |
| Server startup | 1-2 min |
| Download 4GB | 2-5 min |
| Download 7GB | 5-10 min |

---

## 🆘 Quick Troubleshoot

| Issue | Fix |
|-------|-----|
| No GPU | Runtime → Change Type → GPU |
| Server stuck | Wait 3 min, then check console |
| Won't download | Check internet, verify URL |
| Slow download | aria2c should say ✅ |

---

## 💡 Tips

1. **Keep session alive:** Use Colab Pro for 24h sessions
2. **Faster downloads:** aria2c runs 16 parallel downloads
3. **Multiple models:** Add URLs comma-separated in Cell 2
4. **Save bandwidth:** Use Google Drive storage

---

That's it! Just copy, paste, and run! 🚀

