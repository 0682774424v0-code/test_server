# Google Colab Setup for Stable Diffusion Server

## Instructions

1. Create a new Google Colab notebook
2. Replace the first cell with the following code:

```python
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

if not os.path.exists("/content/sd-inference-server"):
    !git clone https://github.com/0682774424v0-code/test_server.git /content/sd-inference-server
    %cd /content/sd-inference-server
    !git clone https://github.com/arenasys/sd-scripts.git training

%cd /content/sd-inference-server
!git pull

model_folder = "/content/sd-inference-server/models"
try:
    # Use Google Drive for models (optional)
    from google.colab import drive
    drive.mount('/content/drive', force_remount=True)
    model_folder = "/content/drive/My Drive/qDiffusion/models"
    if not os.path.exists(model_folder):
        !mkdir '/content/drive/My Drive/qDiffusion' -p
        !cp -r 'models/' '/content/drive/My Drive/qDiffusion/'
except Exception as e:
    print(f"Google Drive mount failed: {e}, using local folder")

if not os.path.exists("venv"):
    !mkdir venv
    !pip uninstall -q -y tensorflow peft
    !pip install -q diffusers==0.27.2 k_diffusion==0.0.15 spandrel==0.4.1 lark==1.1.5 transformers==4.36.2 websockets==11.0.3 bson==0.5.10 mega.py==1.0.8 pytorch-lightning==2.0.2 timm==0.9.2 tomesd==0.1.3 pycloudflared==0.2.0 segment-anything==1.0 geffnet==1.0.2 toml==0.10.2 voluptuous==0.13.1 accelerate==0.27.2 lycoris-lora==2.3.0.dev4 ultralytics==8.2.3 huggingface_hub==0.25.1
    IPython.display.clear_output()

    !apt -y update -qq
    !wget https://github.com/camenduru/gperftools/releases/download/v1.0/libtcmalloc_minimal.so.4 -O /content/libtcmalloc_minimal.so.4
    %env LD_PRELOAD=/content/libtcmalloc_minimal.so.4
    IPython.display.clear_output()

    !wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
    !chmod +x cloudflared
    IPython.display.clear_output()

if not sys.path[0] == "/content/sd-inference-server/":
    sys.path.insert(0, "/content/sd-inference-server/")

IPython.display.clear_output()
print("STARTING...")
password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
stopping = False

def tunnel_thread():
    while True:
        time.sleep(0.1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 28888))
        if result == 0:
            break
        sock.close()
    time.sleep(1)

    url_pattern = re.compile(r"(?P<url>https?://\S+\.trycloudflare\.com)")
    p = subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://127.0.0.1:28888"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, encoding="utf-8")
    for line in p.stderr:
        url_match = url_pattern.search(line)
        if url_match:
            tunnel_url = url_match.group("url")
            endpoint = tunnel_url.replace("https", "wss").strip()
            params = urllib.parse.urlencode({'endpoint': endpoint, "password": password})
            print("ENDPOINT:", endpoint)
            display(HTML(f'<pre>WEB UI: <a href="{"qdiffusion:?" + params}">{"qdiffusion:?" + params}</a></pre>'))
            print("READY!")
            break
    while not stopping:
        time.sleep(0.1)
    print("SHUTTING DOWN...")
    p.kill()

print("PASSWORD:", password)
threading.Thread(target=tunnel_thread, daemon=True).start()

# FIXED: Use server.py instead of remote.py
!cd /content/sd-inference-server && python sd-inference-server-master/server.py --models "$model_folder" --password "$password"
stopping = True
```

## Key Changes:

1. **Fixed entry point**: Changed from `remote.py` to `sd-inference-server-master/server.py`
2. **Corrected path**: Added full path to server.py
3. **Better error handling**: Added try/except for Google Drive mount

## What This Does:

1. Clones the sd-inference-server repository
2. Installs all required Python packages
3. Sets up Cloudflare tunnel for secure remote access
4. Starts the WebSocket server on port 28888
5. Displays the connection endpoint

## To Connect:

1. Copy the endpoint URL from the Colab output
2. Open your web UI at `c:\Users\Administrator\Downloads\Stable_Diffusion\poyo_test_sd\index.html`
3. Paste the endpoint into the connection settings
4. Use the password shown in Colab output

**The download feature should now work correctly!** ✅
