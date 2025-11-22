%cd /content

import IPython.display
from IPython.core.display import display, HTML
import os
import sys
import random
import string
import urllib.parse
import subprocess
import threading
import time
import re
import socket

# ============================================================================
# SETUP: Clone Repository if Needed
# ============================================================================

if not os.path.exists("/content/sd-inference-server"):
    print("📦 Cloning repository...")
    !git clone https://github.com/0682774424v0-code/test_server.git /content/sd-inference-server
    %cd /content/sd-inference-server
    print("✅ Repository cloned!")
else:
    print("✅ Repository already exists, updating...")
    %cd /content/sd-inference-server
    !git pull origin main

# ============================================================================
# SETUP: Model Folders
# ============================================================================

model_folder = "/content/sd-inference-server/models"
try:
    # Try to use Google Drive for models (optional)
    from google.colab import drive
    drive.mount('/content/drive', force_remount=True)
    model_folder = "/content/drive/My Drive/qDiffusion/models"
    print(f"📁 Using Google Drive: {model_folder}")
    if not os.path.exists(model_folder):
        !mkdir -p '/content/drive/My Drive/qDiffusion'
        !cp -r 'models/' '/content/drive/My Drive/qDiffusion/' 2>/dev/null || true
except Exception as e:
    print(f"⚠️  Google Drive mount skipped: {e}")
    print(f"📁 Using local folder: {model_folder}")
    pass

# ============================================================================
# SETUP: Dependencies & Environment
# ============================================================================

if not os.path.exists("venv_initialized"):
    print("\n📦 Installing dependencies...")
    
    # Uninstall conflicting packages
    !pip uninstall -q -y tensorflow peft 2>/dev/null || true
    
    # Install required packages
    !pip install -q \
        diffusers==0.27.2 \
        k_diffusion==0.0.15 \
        spandrel==0.4.1 \
        lark==1.1.5 \
        transformers==4.36.2 \
        websockets==11.0.3 \
        bson==0.5.10 \
        mega.py==1.0.8 \
        pytorch-lightning==2.0.2 \
        timm==0.9.2 \
        tomesd==0.1.3 \
        pycloudflared==0.2.0 \
        segment-anything==1.0 \
        geffnet==1.0.2 \
        toml==0.10.2 \
        voluptuous==0.13.1 \
        accelerate==0.27.2 \
        lycoris-lora==2.3.0.dev4 \
        ultralytics==8.2.3 \
        huggingface_hub==0.25.1 \
        requests \
        urllib3
    
    print("✅ Dependencies installed!")
    IPython.display.clear_output()
    
    # System tools
    !apt -y update -qq >/dev/null 2>&1
    !apt -y install -qq aria2 >/dev/null 2>&1  # For faster downloads
    print("✅ System tools installed!")
    
    # Cloudflared for tunneling
    !wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
    !chmod +x cloudflared
    print("✅ Cloudflared installed!")
    
    # Memory optimization (optional)
    !wget -q https://github.com/camenduru/gperftools/releases/download/v1.0/libtcmalloc_minimal.so.4 -O /content/libtcmalloc_minimal.so.4 2>/dev/null || true
    
    # Mark as initialized
    !touch venv_initialized
    IPython.display.clear_output()

# ============================================================================
# SETUP: Python Path
# ============================================================================

if not sys.path[0] == "/content/sd-inference-server/":
    sys.path.insert(0, "/content/sd-inference-server/")

IPython.display.clear_output()

# ============================================================================
# CONFIGURATION: API Tokens & Settings
# ============================================================================

print("🔧 CONFIGURATION")
print("=" * 60)

# CivitAI Token (optional - needed for private models)
CIVITAI_API_KEY = ""  # @param {type:"string"}
if CIVITAI_API_KEY:
    print(f"✅ CivitAI API Key configured")
else:
    print(f"ℹ️  CivitAI API Key not set (optional)")

# HuggingFace Token (optional - needed for gated models)
HF_TOKEN = ""  # @param {type:"string"}
if HF_TOKEN:
    print(f"✅ HuggingFace Token configured")
else:
    print(f"ℹ️  HuggingFace Token not set (optional)")

# Server password
password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
print(f"\n🔐 Server Password: {password}")

# ============================================================================
# SERVER: Generate Connection Link
# ============================================================================

stopping = False

def tunnel_thread():
    """Create Cloudflare tunnel and display connection link"""
    # Wait for server to start
    while True:
        time.sleep(0.1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 28888))
        if result == 0:
            break
        sock.close()
    
    time.sleep(1)
    
    # Extract tunnel URL
    url_pattern = re.compile(r"(?P<url>https?://\S+\.trycloudflare\.com)")
    print("\n⏳ Starting Cloudflare tunnel...")
    
    p = subprocess.Popen(
        ["./cloudflared", "tunnel", "--url", "http://127.0.0.1:28888"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    
    tunnel_found = False
    for line in p.stderr:
        url_match = url_pattern.search(line)
        if url_match and not tunnel_found:
            tunnel_found = True
            tunnel_url = url_match.group("url")
            endpoint = tunnel_url.replace("https", "wss").strip()
            params = urllib.parse.urlencode({'endpoint': endpoint, "password": password})
            
            # Display connection information
            print("\n" + "=" * 60)
            print("🎉 SERVER READY - CONNECTION INFORMATION")
            print("=" * 60)
            print(f"\n📍 Endpoint: {endpoint}")
            print(f"🔐 Password: {password}")
            print(f"\n📱 WebSocket URI:")
            print(f"   {endpoint}?password={password}")
            
            print(f"\n💻 Desktop Client URI:")
            desktop_uri = "qdiffusion:?" + params
            print(f"   {desktop_uri}")
            display(HTML(f'<pre><a href="{desktop_uri}" target="_blank">Click to open in qDiffusion</a></pre>'))
            
            print(f"\n🌐 Web UI:")
            web_url = f"https://arenasys.github.io/?endpoint={urllib.parse.quote(endpoint, safe='')}&password={password}"
            print(f"   {web_url}")
            display(HTML(f'<pre><a href="{web_url}" target="_blank">Click to open Web UI</a></pre>'))
            
            print("\n" + "=" * 60)
            print("✅ READY FOR CONNECTIONS!")
            print("=" * 60)
            break
    
    # Keep tunnel alive
    while not stopping:
        time.sleep(0.1)
    
    print("\n👋 Server shutting down...")
    p.kill()

# ============================================================================
# SERVER: Start Server
# ============================================================================

print("\n📡 STARTING SERVER")
print("=" * 60)
print("🚀 Launching sd-inference-server on port 28888...")

# Start tunnel thread
tunnel_thread_obj = threading.Thread(target=tunnel_thread, daemon=True)
tunnel_thread_obj.start()

try:
    # Start the server
    os.chdir("/content/sd-inference-server")
    
    # Set environment variables for optimization
    os.environ['LD_PRELOAD'] = '/content/libtcmalloc_minimal.so.4'
    
    # Run server with proper arguments
    !python sd-inference-server-master/server.py \
        --models "$model_folder" \
        --password "$password"

except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user")
except Exception as e:
    print(f"\n❌ Server error: {e}")
finally:
    stopping = True
    print("✋ Server stopped")
