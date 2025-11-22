# Stable Diffusion Web UI - Deployment & Setup Guide

## Overview

This is a complete web-based UI for Stable Diffusion image generation that connects to the **qDiffusion inference server** (sd-inference-server) running on Google Colab via WebSocket over Cloudflare tunnel.

## Quick Start

### Prerequisites
- Google Colab notebook running sd-inference-server with Cloudflare tunnel
- Modern web browser (Chrome, Firefox, Safari, Edge)
- WebSocket endpoint (wss://xxx.trycloudflare.com)
- Server password

### Local Testing

1. **Serve the files locally**:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Or using Node.js http-server
   npx http-server
   
   # Or using Live Server VS Code extension
   ```

2. **Open in browser**:
   - Navigate to `http://localhost:8000`
   - Enter your WebSocket endpoint and password
   - Click "Connect"

3. **Test generation**:
   - Enter a prompt
   - Adjust settings as needed
   - Click "Generate"

## Deployment to GitHub Pages

### Method 1: Direct GitHub Pages (Recommended)

1. **Create/Update GitHub Repository**:
   ```bash
   # Initialize git (if not already done)
   git init
   git add .
   git commit -m "Initial commit: Stable Diffusion Web UI"
   git remote add origin https://github.com/YOUR_USERNAME/sd-web-ui.git
   git branch -M main
   git push -u origin main
   ```

2. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Select "Deploy from a branch"
   - Choose branch: `main`
   - Choose folder: `/ (root)`
   - Click "Save"

3. **Access your site**:
   - Your site will be available at: `https://YOUR_USERNAME.github.io/sd-web-ui/`
   - Or update settings to use custom domain if configured

### Method 2: Using GitHub Actions (Auto-Deploy)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./
          cname: yourdomain.com  # Optional: for custom domain
```

### Method 3: Deploy to Other Platforms

#### Vercel
```bash
npm i -g vercel
vercel
```

#### Netlify
```bash
npm i -g netlify-cli
netlify deploy --prod
```

#### Firebase Hosting
```bash
npm i -g firebase-tools
firebase init hosting
firebase deploy
```

## Project Structure

```
sd-web-ui/
├── index.html          # Main HTML structure
├── style.css           # Styling and responsive design
├── websocket.js        # WebSocket communication module
├── app.js              # Main application logic
└── README.md           # This file
```

## Features

### Connection Management
- WebSocket endpoint input with validation
- Password authentication
- Connection status indicator
- Automatic reconnection handling

### Image Generation
- **Text-to-Image (txt2img)**: Generate from prompt alone
- **Image-to-Image (img2img)**: Refine existing images
- Drag & drop image upload
- Base64 image encoding for server transmission

### Generation Settings
- **Model Selection**: Dynamic dropdown populated from server
- **Sampler**: DPM++, Euler, Heun, and more
- **Steps**: 1-150 (quality vs. speed tradeoff)
- **CFG Scale**: 1-30 (prompt adherence)
- **Dimensions**: Customizable width and height
- **Seed**: Manual or random seed selection
- **Denoising Strength**: For img2img (0-1)
- **Negative Prompts**: Specify what to avoid

### Real-Time Features
- **Progress Tracking**: Live generation progress bar
- **Preview Generation**: See results as they're generated
- **Status Updates**: Connection and generation status

### Results Management
- **Download**: Save generated images
- **Use as Input**: Use output as base for next generation
- **Share**: Share prompts and parameters
- **Metadata Display**: View generation details

### User Experience
- Dark theme optimized for image viewing
- Responsive design (desktop, tablet, mobile)
- Settings persistence (localStorage)
- Toast notifications for user feedback
- Error handling and recovery

## API Protocol

### Message Format

All messages are JSON objects sent over WebSocket.

#### Authentication
```json
{
  "password": "your_password"
}
```

#### Request Models
```json
{
  "action": "list_models"
}
```

#### Generate Image (txt2img)
```json
{
  "action": "generate",
  "prompt": "a beautiful landscape",
  "negative_prompt": "blurry, low quality",
  "model": "model_name",
  "sampler": "DPM++ 2M Karras",
  "steps": 20,
  "cfg_scale": 7.5,
  "width": 512,
  "height": 512,
  "seed": -1
}
```

#### Generate Image (img2img)
```json
{
  "action": "generate",
  "image": "base64_encoded_image_data",
  "prompt": "modifications to make",
  "negative_prompt": "blurry, low quality",
  "model": "model_name",
  "sampler": "DPM++ 2M Karras",
  "steps": 20,
  "cfg_scale": 7.5,
  "width": 512,
  "height": 512,
  "denoising_strength": 0.75,
  "seed": -1
}
```

#### Cancel Generation
```json
{
  "action": "cancel"
}
```

### Server Responses

#### Models List
```json
{
  "type": "models",
  "models": ["model1", "model2", "model3"]
}
```

#### Progress Update
```json
{
  "type": "progress",
  "value": 0.45
}
```

#### Preview Image
```json
{
  "type": "preview",
  "image": "base64_encoded_image"
}
```

#### Generation Result
```json
{
  "type": "result",
  "image": "base64_encoded_image",
  "metadata": {
    "prompt": "...",
    "steps": 20,
    "seed": 12345
  }
}
```

#### Error
```json
{
  "type": "error",
  "error": "Error message"
}
```

## Configuration

### Modifying Sampler Options

Edit `app.js` in the SDWebUI constructor to add/remove samplers:

```javascript
<option value="YourSampler">Display Name</option>
```

### Changing Default Values

Edit `app.js` loadSettings() method or modify HTML input values:

```html
<input type="range" value="20" ...>  <!-- Default steps -->
<input type="range" value="7.5" ...> <!-- Default CFG -->
```

### Customizing UI Colors

Edit `style.css` CSS variables:

```css
:root {
    --primary-color: #6366f1;      /* Main color */
    --success-color: #10b981;      /* Success color */
    --danger-color: #ef4444;       /* Error color */
    --bg-primary: #0f172a;         /* Background */
    --text-primary: #f1f5f9;       /* Text color */
}
```

## Troubleshooting

### Connection Issues

**Problem**: "Connection timeout" error
- Verify WebSocket endpoint is correct (should start with wss://)
- Check Colab server is running and tunnel is active
- Verify firewall/CORS settings allow connections

**Problem**: "Authentication failed"
- Double-check password matches server
- Ensure no extra whitespace in password field

### Generation Issues

**Problem**: "No models available"
- Server may not have loaded models yet
- Try reconnecting
- Check server logs in Colab

**Problem**: Generation stuck at 0%
- Server might be processing (no real-time progress)
- Wait longer or check server status
- Cancel and try again

### Display Issues

**Problem**: Image appears zoomed/cut off
- Check browser zoom level (Ctrl+0 to reset)
- Try different browser
- Check responsive design on smaller screens

## Browser Compatibility

- Chrome/Chromium: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (iOS 13+)
- Edge: ✅ Full support
- Opera: ✅ Full support

## Performance Tips

1. **Reduce image dimensions** for faster generation
2. **Lower step count** for quicker results (15-30 is often good)
3. **Use faster samplers** like Euler (faster but less quality)
4. **Optimize seed** - remember good seeds for consistent results
5. **Monitor server memory** - very large batches may timeout

## Security Considerations

1. **HTTPS Only**: Always use wss:// (secure WebSocket)
2. **Password Protection**: Server requires authentication
3. **No Data Storage**: Images are processed in real-time, not stored
4. **Client-Side Processing**: All image encoding happens locally
5. **CORS**: WebSocket bypasses CORS, but data should still be validated

## Advanced Usage

### Batch Generation Script

Create a script to generate multiple images:

```javascript
async function generateBatch(prompts, settings) {
    const results = [];
    for (const prompt of prompts) {
        const result = await generateImage({...settings, prompt});
        results.push(result);
        await new Promise(r => setTimeout(r, 1000)); // 1s delay between
    }
    return results;
}
```

### Custom Prompt Templates

Modify `app.js` to add preset prompts:

```javascript
const presets = {
    portrait: "portrait of a person, highly detailed, professional",
    landscape: "landscape, scenic, beautiful, detailed"
};
```

## Contributing

To contribute improvements:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/name`)
3. Make your changes
4. Commit (`git commit -am 'Add feature'`)
5. Push (`git push origin feature/name`)
6. Open a Pull Request

## License

MIT License - Feel free to use for personal or commercial projects.

## Support

For issues and questions:
- Check the Troubleshooting section
- Review browser console (F12) for errors
- Verify server is running and accessible
- Check Colab notebook logs

## Changelog

### Version 1.0.0 (Initial Release)
- Complete web UI for Stable Diffusion
- WebSocket communication
- txt2img and img2img support
- Progress tracking
- Settings persistence
- Responsive design
- Dark theme UI

## Roadmap

- [ ] Image history/gallery
- [ ] Batch generation interface
- [ ] Advanced settings panel
- [ ] Community prompt sharing
- [ ] Image comparison tools
- [ ] API documentation
- [ ] Mobile app

## Credits

- Built with vanilla HTML/CSS/JavaScript
- UI inspired by Discord and modern design systems
- Icons from Font Awesome 6
- Fonts from Google Fonts

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0
