# File Reference Guide

## Core Application Files

### `index.html` (300+ lines)
**Purpose**: Main HTML structure and layout

**Contains**:
- Connection panel with endpoint/password inputs
- Main generation interface
- Image upload area (drag & drop)
- Control sections for generation settings
- Results display area
- Loading overlay
- Toast notification container

**Key Elements**:
- `#connectionPanel`: Connection form
- `#mainPanel`: Main generation interface
- `#uploadArea`: Image upload area
- `#prompt`, `#negativePrompt`: Text areas
- `#generateBtn`, `#stopBtn`: Action buttons
- `#progressBar`: Generation progress indicator
- `#resultsSection`: Results display
- `#toastContainer`: Notifications

**External Libraries**:
- Font Awesome (icons)
- Google Fonts (typography)

---

### `style.css` (1000+ lines)
**Purpose**: Complete styling and responsive design

**Contains**:
- CSS variables for theming
- Component styles:
  - Connection panel
  - Form elements
  - Buttons
  - Sliders
  - Cards/sections
  - Notifications
- Responsive breakpoints
- Animations and transitions
- Dark theme colors

**Key Classes**:
- `.app-container`: Main container
- `.connection-panel`: Connection area
- `.main-panel`: Generation area
- `.control-column`: Settings column
- `.preview-column`: Results column
- `.btn`, `.btn-primary`, `.btn-success`: Buttons
- `.slider`, `.slider-group`: Slider styles
- `.toast`: Notification styles
- `.loading-overlay`: Loading screen

**Responsive Breakpoints**:
- Desktop: Full layout (1400px+)
- Tablet: Two-column stacked (768px-1400px)
- Mobile: Single column (< 768px)
- Small mobile: Full-screen (<480px)

---

### `websocket.js` (350+ lines)
**Purpose**: WebSocket communication with server

**Main Class**: `SDWebSocketClient`

**Properties**:
- `ws`: WebSocket connection object
- `isConnected`: Connection status
- `endpoint`: Server endpoint URL
- `password`: Authentication password
- `handlers`: Event handler callbacks

**Key Methods**:
- `connect(endpoint, password)`: Establish connection
- `authenticate(password)`: Send authentication
- `requestModels()`: Request available models
- `generateImage(params)`: txt2img request
- `generateImageToImage(image, params)`: img2img request
- `cancelGeneration()`: Cancel current generation
- `sendMessage(message)`: Send JSON message
- `disconnect()`: Close connection
- `isConnectedToServer()`: Check status

**Event Types**:
- `connect`: Connection established
- `disconnect`: Connection lost
- `authenticate`: Authentication successful
- `error`: Error occurred
- `message`: Any message received
- `models`: Models list received
- `progress`: Progress update (0-100)
- `preview`: Preview image
- `result`: Final result

**Usage Example**:
```javascript
const client = new SDWebSocketClient();
client.on('result', (data) => console.log(data.image));
await client.connect('wss://example.com', 'password');
client.generateImage({prompt: 'a cat'});
```

---

### `app.js` (700+ lines)
**Purpose**: Main application logic and UI management

**Main Class**: `SDWebUI`

**Key Methods**:
- `init()`: Initialize application
- `setupEventListeners()`: Attach event handlers
- `setupWebSocketHandlers()`: Setup server handlers
- `handleConnect()`: Connection logic
- `handleGenerate()`: Generation logic
- `handleImageSelect()`: Image upload logic
- `showToast()`: Show notifications
- `downloadImage()`: Download result
- `useResultAsInput()`: Iterate generation
- `saveSettings()`: Persist to localStorage
- `loadSettings()`: Restore from localStorage

**DOM Element References** (in `this.els`):
- Connection: `endpoint`, `password`, `connectBtn`, `statusIndicator`
- Upload: `uploadArea`, `imageInput`, `previewImage`
- Prompts: `prompt`, `negativePrompt`
- Settings: `model`, `sampler`, `steps`, `cfg`, `denoising`, `width`, `height`, `seed`
- Controls: `generateBtn`, `stopBtn`, `progressBar`, `progressText`
- Results: `resultImage`, `downloadBtn`, `useAsInputBtn`, `metadataContent`

**State Management**:
- `isGenerating`: Current generation status
- `uploadedImage`: Base64 encoded image
- `lastResult`: Last generation result
- `generationMetadata`: Generation parameters

**Storage**:
- Uses `localStorage` for settings persistence
- Key: `sdWebUISettings`
- Saves: All settings and prompts

---

## Documentation Files

### `README.md`
**Purpose**: Main project documentation

**Sections**:
- Overview and features
- Quick start guide
- Local testing instructions
- Deployment methods (GitHub Pages, Vercel, Netlify, Firebase)
- Project structure
- Features list with details
- API protocol documentation
- Configuration guide
- Troubleshooting section
- Browser compatibility
- Performance tips
- Security considerations
- Advanced usage
- Contributing guidelines
- License information

**Audience**: General users and developers

---

### `QUICKSTART.md`
**Purpose**: Quick setup and basic usage guide

**Sections**:
- WebSocket endpoint setup from Colab
- Connection troubleshooting
- Common server messages
- Example prompts
- Generation tips (speed vs quality)
- Example workflow
- Mobile usage
- Performance metrics
- API reference

**Audience**: End users

---

### `DEVELOPMENT.md`
**Purpose**: Developer and advanced user guide

**Sections**:
- WebSocket message examples
- Complete generation workflow
- UI customization guides
- API integration examples
- Performance optimization
- Testing examples
- Theme implementation
- Server-side enhancements
- Database integration
- Debugging tips
- Custom features

**Audience**: Developers extending the application

---

### `DEPLOY_TO_GITHUB.md`
**Purpose**: Step-by-step GitHub Pages deployment

**Sections**:
- Three deployment methods
- Git setup and commands
- GitHub Pages configuration
- Custom domain setup
- HTTPS configuration
- Troubleshooting deployment
- CI/CD with GitHub Actions
- Monitoring and rollback
- Sharing your site
- Advanced deployment
- Performance optimization
- Maintenance checklist

**Audience**: Users deploying to GitHub Pages

---

### `PROJECT_SUMMARY.md`
**Purpose**: Project overview and status

**Sections**:
- Completed deliverables checklist
- Key features overview
- Project structure
- Getting started quick links
- Server connection requirements
- Browser support table
- Customization options
- Security features
- Performance metrics
- Troubleshooting quick reference
- Next steps

**Audience**: Project managers and stakeholders

---

## Configuration Files

### `package.json`
**Purpose**: Node.js project metadata

**Contains**:
- Project name and version
- Description
- Scripts (start, dev, build, deploy)
- Keywords
- Author
- License
- Repository info
- Dev dependencies (http-server)

**Usage**:
```bash
npm start          # Start dev server
npm run deploy     # Push to GitHub
npm install        # Install dependencies
```

---

### `.gitignore`
**Purpose**: Git ignore rules

**Ignores**:
- Node modules
- IDE files (.vscode, .idea)
- Build outputs
- Environment files
- OS files (Thumbs.db, .DS_Store)
- Logs

---

## File Organization

```
sd-web-ui/
│
├── 📄 index.html              Core HTML (300 lines)
├── 🎨 style.css               Full styling (1000 lines)
├── 🔌 websocket.js            WebSocket module (350 lines)
├── ⚙️  app.js                 Application logic (700 lines)
│
├── 📚 Documentation
│   ├── README.md              Main guide
│   ├── QUICKSTART.md          User guide
│   ├── DEVELOPMENT.md         Developer guide
│   ├── DEPLOY_TO_GITHUB.md    Deployment guide
│   └── PROJECT_SUMMARY.md     Project overview
│
├── ⚙️  Configuration
│   ├── package.json           npm metadata
│   └── .gitignore             Git rules
│
└── (Optional) GitHub Actions
    └── .github/workflows/deploy.yml
```

---

## File Dependencies

```
index.html
├── style.css (linked)
├── websocket.js (script)
├── app.js (script)
└── External:
    ├── Font Awesome (icons)
    └── Google Fonts (typography)

websocket.js
└── No dependencies
    (Pure JavaScript, no imports)

app.js
├── websocket.js (requires SDWebSocketClient)
└── index.html (requires DOM elements)
```

---

## Quick File Reference

| File | Size | Purpose | Edit For |
|------|------|---------|----------|
| index.html | ~300 lines | HTML structure | Layout changes, new controls |
| style.css | ~1000 lines | Styling | Colors, sizing, responsive design |
| websocket.js | ~350 lines | Server communication | Protocol changes, connection logic |
| app.js | ~700 lines | Application logic | UI behavior, generation workflow |
| README.md | ~400 lines | Documentation | General info, features, tips |
| QUICKSTART.md | ~200 lines | User guide | Setup instructions, examples |
| DEVELOPMENT.md | ~300 lines | Developer guide | Technical details, examples |
| DEPLOY_TO_GITHUB.md | ~300 lines | Deployment | GitHub Pages setup |
| package.json | ~25 lines | Project metadata | Name, version, scripts |
| .gitignore | ~20 lines | Git rules | Files to ignore |

---

## Total Project Size

**Code**: ~2500 lines
- HTML: 300 lines
- CSS: 1000 lines
- JavaScript: 1050 lines
- JSON: 25 lines

**Documentation**: ~1000 lines
- README: 400 lines
- QUICKSTART: 200 lines
- DEVELOPMENT: 300 lines
- DEPLOY: 300 lines
- PROJECT_SUMMARY: ~200 lines

**Total**: ~3500 lines of production-ready code and documentation

---

## Modification Guide

### To Change UI Colors
→ Edit `style.css` CSS variables section

### To Add New Control
→ Add HTML in `index.html` → Add JS in `app.js` → Add CSS in `style.css`

### To Change Generation Parameters
→ Edit `app.js` `handleGenerate()` method

### To Add New Event Handler
→ Edit `websocket.js` `handlers` object → Setup in `app.js`

### To Change Connection Logic
→ Edit `websocket.js` `connect()` method

### To Add Documentation
→ Create new `.md` file in project root

---

## File Access

All files are in:
```
c:\Users\Administrator\Downloads\Stable_Diffusion\poyo_test_sd\sd-web-ui\
```

Access in:
- Text editor: VS Code, Sublime, Notepad++
- Browser: Open `index.html` directly (for local testing)
- Terminal: `cd sd-web-ui` then run commands

---

**Last Updated**: 2025-11-22
**Version**: 1.0.0
