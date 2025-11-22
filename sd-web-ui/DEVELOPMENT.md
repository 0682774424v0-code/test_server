# Development & Customization Guide

## WebSocket Message Examples

### Complete Generation Workflow

```javascript
// 1. Connect and authenticate
const wsClient = new SDWebSocketClient();
await wsClient.connect('wss://example.trycloudflare.com', 'password123');

// 2. Listen for models
wsClient.on('models', (models) => {
    console.log('Available models:', models);
});

// 3. Request models
wsClient.requestModels();

// 4. Listen for generation progress
wsClient.on('progress', (progress) => {
    console.log(`Generation: ${progress * 100}%`);
});

// 5. Listen for preview
wsClient.on('preview', (data) => {
    console.log('Preview received:', data);
});

// 6. Listen for result
wsClient.on('result', (data) => {
    console.log('Result:', data.image);
    // data.image is base64 encoded
    const img = new Image();
    img.src = 'data:image/png;base64,' + data.image;
});

// 7. Generate image
wsClient.generateImage({
    prompt: 'a beautiful landscape painting',
    negative_prompt: 'blurry, low quality',
    model: 'model_name',
    sampler: 'DPM++ 2M Karras',
    steps: 20,
    cfg_scale: 7.5,
    width: 512,
    height: 512,
    seed: -1
});

// 8. Cancel if needed
wsClient.cancelGeneration();

// 9. Listen for errors
wsClient.on('error', (error) => {
    console.error('Error:', error);
});
```

## Extending the UI

### Adding New Slider Controls

1. **Add HTML element** in `index.html`:
```html
<div class="slider-group">
    <div class="slider-header">
        <label>My Setting</label>
        <span class="slider-value" id="mySettingValue">0.5</span>
    </div>
    <input 
        type="range" 
        id="mySetting" 
        min="0" 
        max="1" 
        step="0.1" 
        value="0.5" 
        class="slider">
</div>
```

2. **Add event listener** in `app.js`:
```javascript
this.els.mySetting.addEventListener('input', (e) => {
    this.els.mySettingValue.textContent = parseFloat(e.target.value).toFixed(1);
});
```

3. **Include in generation params**:
```javascript
const params = {
    // ... existing params
    my_setting: parseFloat(this.els.mySetting.value)
};
```

### Custom Sampler List

Edit the sampler dropdown in `index.html`:

```html
<select id="sampler" class="form-select">
    <option value="DPM++ 2M Karras">DPM++ 2M Karras (Best Quality)</option>
    <option value="Euler a">Euler A (Fast)</option>
    <option value="DDIM">DDIM (Standard)</option>
    <!-- Add more options -->
</select>
```

### Adding Image Filters/Preprocessing

Modify `handleImageSelect()` in `app.js`:

```javascript
async handleImageSelect(event) {
    // ... existing code ...
    
    // Apply preprocessing
    const processed = await this.preprocessImage(this.uploadedImage);
    this.uploadedImage = processed;
}

async preprocessImage(base64) {
    // Apply filters, resizing, etc.
    const img = new Image();
    img.src = base64;
    
    return new Promise(resolve => {
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 512;
            const ctx = canvas.getContext('2d');
            
            // Apply any canvas transformations
            ctx.drawImage(img, 0, 0, 512, 512);
            
            resolve(canvas.toDataURL('image/png'));
        };
    });
}
```

### Adding Real-Time Preview Mode

```javascript
class SDWebUI {
    constructor() {
        // ... existing code ...
        this.previewUpdateInterval = null;
    }

    enableLivePreview() {
        // Request preview updates every 500ms
        this.previewUpdateInterval = setInterval(() => {
            if (this.isGenerating) {
                sdClient.sendMessage({ action: 'request_preview' });
            }
        }, 500);
    }

    disableLivePreview() {
        if (this.previewUpdateInterval) {
            clearInterval(this.previewUpdateInterval);
            this.previewUpdateInterval = null;
        }
    }
}
```

## API Integration Examples

### Sending to External API After Generation

```javascript
async sendToExternalAPI(imageBase64) {
    const response = await fetch('https://your-api.com/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            image: imageBase64,
            metadata: this.generationMetadata
        })
    });
    return response.json();
}
```

### Retrieving Prompts from API

```javascript
async loadPromptsFromAPI() {
    const response = await fetch('https://your-api.com/prompts');
    const prompts = await response.json();
    
    // Populate a new dropdown
    const select = document.createElement('select');
    prompts.forEach(prompt => {
        const option = document.createElement('option');
        option.value = prompt.text;
        option.textContent = prompt.name;
        select.appendChild(option);
    });
}
```

## Performance Optimization

### Lazy Load Large Images

```javascript
class ImageLazyLoader {
    constructor() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                }
            });
        });
    }

    loadImage(img) {
        const src = img.dataset.src;
        if (src) {
            img.src = src;
            this.observer.unobserve(img);
        }
    }
}
```

### Cache Management

```javascript
class ImageCache {
    constructor(maxSize = 50) {
        this.cache = new Map();
        this.maxSize = maxSize;
    }

    set(key, value) {
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, value);
    }

    get(key) {
        return this.cache.get(key);
    }
}
```

## Testing

### Unit Test Example

```javascript
describe('SDWebUI', () => {
    let ui;

    beforeEach(() => {
        ui = new SDWebUI();
    });

    test('should validate endpoint format', () => {
        const isValid = ui.validateEndpoint('wss://example.com');
        expect(isValid).toBe(true);
    });

    test('should reject invalid endpoint', () => {
        const isValid = ui.validateEndpoint('http://example.com');
        expect(isValid).toBe(false);
    });

    test('should convert image to base64', async () => {
        const base64 = await ui.imageToBase64(mockFile);
        expect(base64.startsWith('data:image')).toBe(true);
    });
});
```

## Dark Mode Implementation

The UI already includes dark mode by default. To add light mode toggle:

```javascript
class ThemeToggle {
    constructor() {
        this.isDark = true;
    }

    toggle() {
        this.isDark = !this.isDark;
        document.documentElement.setAttribute(
            'data-theme', 
            this.isDark ? 'dark' : 'light'
        );
        localStorage.setItem('theme', this.isDark ? 'dark' : 'light');
    }

    init() {
        const saved = localStorage.getItem('theme');
        if (saved === 'light') {
            this.isDark = false;
            document.documentElement.setAttribute('data-theme', 'light');
        }
    }
}
```

Add CSS:
```css
html[data-theme="light"] {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #1a1a1a;
    /* ... more adjustments */
}
```

## Server-Side Enhancements

### Implementing Queue System

Enhance server to support multiple clients:

```python
# On server (pseudocode)
class GenerationQueue:
    def __init__(self):
        self.queue = []
        self.current = None
    
    def add_task(self, params):
        self.queue.append(params)
        if not self.current:
            self.process_next()
    
    def process_next(self):
        if self.queue:
            self.current = self.queue.pop(0)
            # Start generation
```

### Database Integration

Store generation history:

```javascript
// Client-side storage
class GenerationHistory {
    async save(generation) {
        const db = await this.openDB();
        const tx = db.transaction(['generations'], 'readwrite');
        await tx.objectStore('generations').add(generation);
    }

    async getHistory(limit = 100) {
        const db = await this.openDB();
        const tx = db.transaction(['generations'], 'readonly');
        return tx.objectStore('generations')
            .getAll()
            .limit(limit);
    }
}
```

## Debugging Tips

### Enable Verbose Logging

```javascript
class Logger {
    constructor(enabled = true) {
        this.enabled = enabled;
    }

    log(message, data = null) {
        if (this.enabled) {
            console.log(`[${new Date().toISOString()}] ${message}`, data);
        }
    }

    error(message, error = null) {
        if (this.enabled) {
            console.error(`[ERROR] ${message}`, error);
        }
    }
}

const logger = new Logger(true);
```

### Monitor WebSocket Traffic

```javascript
// Intercept all messages
const originalSend = WebSocket.prototype.send;
WebSocket.prototype.send = function(data) {
    console.log('→ Sending:', JSON.parse(data));
    return originalSend.call(this, data);
};

const originalOnMessage = WebSocket.prototype.onmessage;
Object.defineProperty(WebSocket.prototype, 'onmessage', {
    get() { return this._onMessage; },
    set(handler) {
        this._onMessage = function(event) {
            console.log('← Received:', JSON.parse(event.data));
            handler(event);
        };
    }
});
```

---

For more information, see README.md
