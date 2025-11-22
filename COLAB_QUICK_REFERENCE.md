# ⚡ Colab Quick Reference

## 🚀 5-Minute Setup

### 1. Open Google Colab
- Go to [colab.research.google.com](https://colab.research.google.com)
- Create new notebook

### 2. Select GPU
- Runtime → Change Runtime Type → GPU (T4 or A100)

### 3. Run Server Cell
```python
%cd /content
# Copy entire COLAB_CELL.py here
```

### 4. Get Connection Info
```
📍 Endpoint: wss://xxxxx.trycloudflare.com
🔐 Password: AbCd1234
```

### 5. Connect Client
- Copy endpoint into your qDiffusion app
- Or use web UI link

## 📋 Two Cells Needed

### Cell 1: Server (run once, stays on)
- **File:** COLAB_CELL.py
- **Time:** 2-3 minutes
- **Keeps running:** 12+ hours

### Cell 2: Download Models (run as needed)
- **File:** COLAB_DOWNLOAD_CELL.py
- **Time:** Depends on model size
- **Example:** 4GB model = 2-5 minutes

## 📥 Download URLs

### CivitAI
```
https://civitai.com/api/download/models/123456
```

### HuggingFace
```
https://huggingface.co/user/model/resolve/main/file.safetensors
```

### Google Drive
```
https://drive.google.com/file/d/FILE_ID/view?usp=sharing
```

### Multiple (comma-separated)
```
url1, url2, url3
```

## 🔐 Tokens (Optional)

### CivitAI Token
- Get from: https://civitai.com/account/api-tokens
- Paste in Cell 2

### HuggingFace Token
- Get from: https://huggingface.co/settings/tokens
- Paste in Cell 2

## 🎯 Connection Options

### Option 1: Desktop Client
```
qdiffusion:?endpoint=wss://tunnel&password=pass
```

### Option 2: Web UI
```
https://arenasys.github.io/?endpoint=wss://tunnel&password=pass
```

### Option 3: Copy & Paste
```
Endpoint: wss://tunnel
Password: pass
```

## ✅ Checklist

- [ ] Create Colab notebook
- [ ] Enable GPU in Runtime
- [ ] Copy COLAB_CELL.py
- [ ] Run server cell
- [ ] Get connection info
- [ ] Configure client
- [ ] Connect!

## 📊 Performance

| Task | Time |
|------|------|
| First setup | 3-5 min |
| Server start | 1-2 min |
| Model download (4GB) | 2-5 min |
| Model download (7GB) | 3-10 min |
| Generation | Depends on settings |

## ⏰ Colab Session

- **Free:** 12 hours
- **Pro:** 24+ hours
- **Pro+:** Unlimited

Keep session alive by:
1. Using Colab Pro
2. Running multiple notebooks
3. Adding periodic pings

## 🆘 Troubleshooting

| Problem | Fix |
|---------|-----|
| GPU not available | Runtime → Change Type → GPU |
| Server won't start | Wait 3 minutes, check console |
| Tunnel timeout | Restart cell |
| Download stuck | Check internet, try again |
| Out of memory | Restart runtime |

## 📂 File Locations

```
/content/sd-inference-server/
├── models/        ← Checkpoints
├── loras/         ← LoRAs
├── vaes/          ← VAEs
├── upscalers/     ← Upscalers
└── server.py      ← Main server
```

## 🚨 Stop Server

Click **"Stop execution"** button or:
```python
stopping = True  # In server cell
```

## 💡 Pro Tips

1. **Faster downloads:** Models in Cell 2 use aria2c (16 threads)
2. **Better performance:** Use Colab Pro for A100 GPU
3. **Save bandwidth:** Use Google Drive storage
4. **Stay connected:** Keep browser tab active
5. **Multiple models:** Add URLs comma-separated

## 🔗 Useful Links

- **Colab:** https://colab.research.google.com
- **CivitAI:** https://civitai.com
- **HuggingFace:** https://huggingface.co
- **Documentation:** See COLAB_SETUP_GUIDE.md

## 📞 Need Help?

1. **Check logs:** Look at cell output
2. **Browser console:** F12 → Console tab
3. **Restart:** Stop and re-run cell
4. **Use Pro:** Upgrade to Colab Pro for support

---

**That's it! You're ready to generate! 🎉**

