# Quick Start Configuration

## Setting Up Your WebSocket Endpoint

### From Google Colab

When running the sd-inference-server in Colab, you'll see output like:

```
Starting Cloudflare tunnel...
Tunnel URL: https://abc-123-xyz.trycloudflare.com
WebSocket: wss://abc-123-xyz.trycloudflare.com
Password: your_secure_password_here
```

### Connecting to the Web UI

1. Open `index.html` in your browser
2. In the "WebSocket Endpoint" field, enter: `wss://abc-123-xyz.trycloudflare.com`
3. In the "Password" field, enter: `your_secure_password_here`
4. Click "Connect"

You should see:
- ✅ Status changes to "Connected"
- ✅ Models dropdown populates with available models
- ✅ Main generation panel appears

## Troubleshooting Checklist

- [ ] Colab server is running (check kernel state)
- [ ] Cloudflare tunnel is active (no "tunnel expired" message)
- [ ] WebSocket endpoint starts with `wss://`
- [ ] Password matches server setting
- [ ] Browser allows WebSocket connections (not blocked by firewall)
- [ ] No typos in endpoint or password
- [ ] Browser console (F12) shows no errors

## Common Server Messages

### On Successful Connection
```
[Connected to server]
WebSocket connected
Received: {"type": "models", "models": ["model1", "model2"]}
```

### On Failed Connection
```
WebSocket connection error: 400 Bad Request
Connection timeout after 30 seconds
Failed to parse authentication response
```

## Example Prompts

### Landscape
```
A serene mountain landscape with a crystal clear lake, golden hour lighting, 
professional photography, high detail, 8k resolution
```

### Portrait
```
Portrait of a woman with striking blue eyes, professional lighting, 
studio photography, sharp focus, detailed skin texture
```

### Fantasy
```
Dragon flying over a mystical castle, fantasy art style, 
dramatic lighting, highly detailed, cinematic
```

## Generation Tips

### For Faster Results
- Reduce Steps to 15-20
- Use Euler sampler
- Lower resolution (512x512)

### For Better Quality
- Increase Steps to 40-50
- Use DPM++ 2M Karras sampler
- Increase CFG Scale to 10-15
- Higher resolution (768x768)

### For Consistent Results
- Use a fixed Seed (any number)
- Keep the same Model and Sampler
- Fine-tune negative prompt

## Example Generation Workflow

1. **First Generation** (Explore)
   - Prompt: "a beautiful sunset"
   - Steps: 20
   - CFG: 7.5
   - Seed: -1 (random)

2. **Second Generation** (Refine)
   - Use result as input (img2img)
   - Adjusted prompt: "a beautiful sunset, more detailed clouds"
   - Steps: 20
   - Denoising: 0.7

3. **Third Generation** (Polish)
   - Use result as input again
   - Adjusted prompt: "a beautiful sunset, dramatic lighting, professional"
   - Steps: 15
   - Denoising: 0.5

## Storage & History

Settings are automatically saved to browser's localStorage:
- Last used endpoint
- Model and sampler preferences
- Previous prompts
- Slider positions

To clear: Open DevTools (F12) → Application → LocalStorage → Clear

## Mobile Usage

The UI is fully responsive and works on:
- ✅ Tablets (iPad, Android)
- ✅ Mobile phones
- ✅ Small laptops

Adjust settings for slower connections:
- Lower resolution
- Fewer steps
- Faster sampler

## Performance Metrics

On typical connection (50 Mbps):
- **Connection Time**: 2-5 seconds
- **Generation Time** (20 steps, 512x512): 30-60 seconds
- **Preview Update**: Every 5-10 seconds (if enabled)
- **Result Download**: < 1 second

## API Reference

See `DEVELOPMENT.md` for:
- Detailed WebSocket protocol
- Message format examples
- Custom implementation guides
- Advanced integration options

## Support

For issues:
1. Check browser console (F12) for error messages
2. Verify Colab server is running
3. Test WebSocket connection: Open DevTools → Network → click connection
4. Review README.md troubleshooting section
