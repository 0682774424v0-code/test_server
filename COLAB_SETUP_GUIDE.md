# 🚀 Google Colab Setup Guide

## Overview

Two complete Colab cells for running Stable Diffusion server:

1. **COLAB_CELL.py** - Main server setup (runs 24/7)
2. **COLAB_DOWNLOAD_CELL.py** - Download models (run as needed)

## Setup Instructions

### Step 1: Create New Colab Notebook

1. Go to [Google Colab](https://colab.research.google.com)
2. Click **"New notebook"**
3. Name it: "SD Server"

### Step 2: Enable GPU (Important!)

1. Click **"Runtime"** menu
2. Select **"Change runtime type"**
3. Choose **"GPU"** (T4 or A100 recommended)
4. Click **"Save"**

### Step 3: Copy & Run Server Cell

1. Create new cell
2. Copy contents from **COLAB_CELL.py**
3. Paste into Colab cell
4. Run (Ctrl+Enter)
5. Wait for initialization (~2-3 minutes first run)

### Step 4: Get Connection Details

After server starts, you'll see:
```
🎉 SERVER READY - CONNECTION INFORMATION
================================================
📍 Endpoint: wss://example-tunnel.trycloudflare.com
🔐 Password: AbCd1234
```

### Step 5: Connect Your Client

Use the displayed endpoints to connect your:
- Desktop qDiffusion app
- Web browser UI
- Mobile app
- Custom clients

## Colab Cell 1: Server Setup

**File:** COLAB_CELL.py

### What It Does

1. ✅ Clones/updates repository
2. ✅ Installs all dependencies
3. ✅ Downloads system tools (aria2c, cloudflared)
4. ✅ Creates Cloudflare tunnel
5. ✅ Starts WebSocket server
6. ✅ Displays connection links

### Configuration Options

In the code, customize:

```python
# Google Drive (optional)
model_folder = "/content/drive/My Drive/qDiffusion/models"

# CivitAI Token (optional)
CIVITAI_API_KEY = ""

# HuggingFace Token (optional)  
HF_TOKEN = ""

# Server password (auto-generated)
password = ''.join(random.SystemRandom()...)
```

### Runtime

- **First Run:** 3-5 minutes (installation)
- **Subsequent Runs:** 1-2 minutes (startup)
- **Keep Running:** 24+ hours on Colab

### Troubleshooting

**"Connection timeout"**
- Check firewall settings
- Wait for server to fully start (2-3 min)
- Check browser console for errors

**"tunnel not found"**
- cloudflared may be blocked
- Try reconnecting
- Use alternative endpoint if available

**"Out of memory"**
- Too many simultaneous connections
- Reduce batch size in client
- Use smaller models

## Colab Cell 2: Download Models

**File:** COLAB_DOWNLOAD_CELL.py

### What It Does

1. ✅ Downloads models from CivitAI, HuggingFace, Google Drive
2. ✅ Uses aria2c for 10x faster downloads
3. ✅ Shows progress bar
4. ✅ Lists downloaded files

### How to Use

1. Prepare URLs (see examples below)
2. Add your API tokens (if needed)
3. Run the cell
4. Wait for downloads to complete

### Configuration

```python
# Separate by commas for multiple files
download_checkpoints = "url1, url2, url3"
download_loras = "url1, url2"
download_vaes = "url1"
download_upscalers = "url1"

# Optional tokens
CIVITAI_API_KEY = "your_key_here"
HF_TOKEN = "hf_your_token_here"
```

## Example URLs

### CivitAI Models

```
# Checkpoint (from API)
https://civitai.com/api/download/models/456194

# LoRA
https://civitai.com/api/download/models/97655

# Use API key for private/premium models
```

### HuggingFace Models

```
# Checkpoint
https://huggingface.co/frankjoshua/toonyou_beta6/resolve/main/toonyou_beta6.safetensors

# From collection
https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/model.safetensors

# Requires token for private repos
```

### Google Drive

```
# Direct link
https://drive.google.com/file/d/FILE_ID/view?usp=sharing
```

## Complete Example Setup

### Cell 1: Server Initialization
```python
%cd /content
# ... [Copy COLAB_CELL.py content here] ...
```

### Cell 2: Download Models
```python
# Fill in your URLs and tokens
download_checkpoints = "https://huggingface.co/frankjoshua/toonyou_beta6/resolve/main/toonyou_beta6.safetensors"
download_loras = "https://civitai.com/api/download/models/97655, https://civitai.com/api/download/models/124358"

CIVITAI_API_KEY = "your_civitai_key_here"
HF_TOKEN = "hf_your_hf_token_here"

# ... [Copy COLAB_DOWNLOAD_CELL.py content here] ...
```

### Cell 3: Check Status
```python
import os
import subprocess

print("Server Status:")
result = subprocess.run(['pgrep', '-f', 'server.py'], capture_output=True)
if result.stdout:
    print("✅ Server is running")
else:
    print("❌ Server is not running")

print("\nAvailable Models:")
for folder in ['models', 'loras', 'vaes', 'upscalers']:
    if os.path.exists(folder):
        files = os.listdir(folder)
        print(f"  {folder}: {len(files)} files")
```

## Features

### ⚡ Performance
- **aria2c integration** - 10-30x faster downloads
- **16 parallel connections** - Optimal bandwidth usage
- **Resume capability** - Restart interrupted downloads
- **Progress tracking** - Real-time status updates

### 🔐 Security
- **Token management** - Proper authentication
- **Cloudflare tunnel** - Secure connection
- **Password protected** - Server access control
- **HTTPS/WSS only** - Encrypted connections

### 🎯 Compatibility
- **Works with any SD client** - Desktop, web, mobile
- **Supports all sources** - CivitAI, HF, GDrive, direct URLs
- **Multiple models** - Checkpoints, LoRAs, VAEs, upscalers
- **Flexible storage** - Local or Google Drive

## Advanced Options

### Mount Personal Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
# Models save to: /content/drive/My Drive/qDiffusion/
```

### Use Different GPU

```python
# Check available:
!nvidia-smi

# Use specific GPU:
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
```

### Optimize Memory Usage

```python
# Enable memory optimization
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'

# Reduce batch size in client
# Use memory-efficient models
```

### Custom Model Location

```python
model_folder = "/content/my_custom_models/"
os.makedirs(model_folder, exist_ok=True)
```

## Connection Methods

### 1. Desktop qDiffusion App
```
qdiffusion:?endpoint=wss://your-tunnel.trycloudflare.com&password=YourPass123
```

### 2. Web Browser
```
https://arenasys.github.io/?endpoint=wss://your-tunnel.trycloudflare.com&password=YourPass123
```

### 3. Python Client
```python
import websocket

ws = websocket.WebSocketApp("wss://your-tunnel.trycloudflare.com?password=YourPass123")
ws.on_open = lambda ws: ws.send('{"type": "ping"}')
```

### 4. Custom Integration
```
WebSocket: wss://your-tunnel.trycloudflare.com
Password: YourPass123
Protocol: BSON (binary)
```

## Monitoring & Maintenance

### Check Server Status
```python
!ps aux | grep server.py
```

### View Logs
```python
!tail -f crash.log
```

### Monitor Resources
```python
!nvidia-smi
```

### Restart Server
1. Stop cell (press stop button)
2. Re-run cell

## Time Limits & Quotas

### Colab Free Tier
- ⏱️ **Session limit:** 12 hours
- 📊 **Daily usage:** ~40-56 hours
- 🔋 **GPU hours:** Limited

### Keep-Alive Options
1. Use Colab Pro ($9.99/month)
   - 24+ hour sessions
   - Priority GPU access
   - Faster performance

2. Multiple instances
   - Run multiple Colab notebooks
   - Rotate between them

3. Auto-reload
```python
# Add to cell
while True:
    time.sleep(300)  # Keep alive
```

## Cost Estimation

### Free Tier (Colab)
- ✅ **Cost:** $0
- ⚠️ **Limit:** 12 hours/session
- ✅ **Performance:** Good (T4 GPU)

### Colab Pro
- 💰 **Cost:** $9.99/month
- ✅ **Limit:** 24+ hours
- ✅ **Performance:** Very Good (P100/V100)

### Colab Pro+
- 💰 **Cost:** $49.99/month
- ✅ **Limit:** Unlimited
- 🚀 **Performance:** Excellent (A100)

## Tips & Tricks

### Faster First Run
- Use free Colab first
- Pre-download models locally
- Cache dependencies

### Reduce Model Size
- Use fp16 models (half size)
- Use pruned checkpoints
- Convert CKPT → Safetensors

### Better Performance
- Use smaller batch sizes
- Close other browser tabs
- Disable browser extensions
- Use wired connection

### Save Bandwidth
- Store models on Google Drive
- Share models with others
- Use model compression

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Disconnected after 30 min" | Use Colab Pro for 24h sessions |
| "Out of memory" | Reduce batch size or use smaller models |
| "Slow downloads" | Install aria2c or use better connection |
| "Can't find models" | Check folder path matches model_folder |
| "Token invalid" | Regenerate from provider website |
| "Connection timeout" | Wait for server startup (2-3 min) |

## Support Resources

- **Documentation:** See DOWNLOAD_QUICK_START.md
- **Issues:** Check GitHub issues
- **Discord:** https://discord.gg/UtYvGwFfvx
- **Email:** support@example.com

---

**Enjoy your Stable Diffusion server on Google Colab! 🚀**

