/**
 * Stable Diffusion Web UI - Main Application
 * Handles UI interactions and generation workflow
 */

class SDWebUI {
    constructor() {
        // State
        this.isGenerating = false;
        this.uploadedImage = null;
        this.lastResult = null;
        this.generationMetadata = null;

        // DOM Elements
        this.els = {
            // Connection panel
            endpoint: document.getElementById('endpoint'),
            password: document.getElementById('password'),
            connectBtn: document.getElementById('connectBtn'),
            connectionPanel: document.getElementById('connectionPanel'),
            mainPanel: document.getElementById('mainPanel'),
            statusIndicator: document.getElementById('statusIndicator'),
            statusText: document.getElementById('statusText'),

            // Upload
            uploadArea: document.getElementById('uploadArea'),
            imageInput: document.getElementById('imageInput'),
            uploadedImageDiv: document.getElementById('uploadedImage'),
            previewImage: document.getElementById('previewImage'),
            removeImageBtn: document.getElementById('removeImageBtn'),

            // Prompts
            prompt: document.getElementById('prompt'),
            negativePrompt: document.getElementById('negativePrompt'),

            // Settings
            model: document.getElementById('model'),
            sampler: document.getElementById('sampler'),
            steps: document.getElementById('steps'),
            stepsValue: document.getElementById('stepsValue'),
            cfg: document.getElementById('cfg'),
            cfgValue: document.getElementById('cfgValue'),
            denoising: document.getElementById('denoising'),
            denoisingValue: document.getElementById('denoisingValue'),
            width: document.getElementById('width'),
            height: document.getElementById('height'),
            seed: document.getElementById('seed'),
            randomSeedBtn: document.getElementById('randomSeedBtn'),

            // Generation
            generateBtn: document.getElementById('generateBtn'),
            stopBtn: document.getElementById('stopBtn'),
            progressContainer: document.getElementById('progressContainer'),
            progressBar: document.getElementById('progressBar'),
            progressText: document.getElementById('progressText'),
            errorMessage: document.getElementById('errorMessage'),
            generationButtons: document.getElementById('generationButtons'),

            // Results
            resultsSection: document.getElementById('resultsSection'),
            resultImage: document.getElementById('resultImage'),
            downloadBtn: document.getElementById('downloadBtn'),
            useAsInputBtn: document.getElementById('useAsInputBtn'),
            shareBtn: document.getElementById('shareBtn'),
            metadataSection: document.getElementById('metadataSection'),
            metadataContent: document.getElementById('metadataContent'),
            emptyState: document.getElementById('emptyState'),

            // Loading
            loadingOverlay: document.getElementById('loadingOverlay'),
            loadingText: document.getElementById('loadingText'),

            // Toast
            toastContainer: document.getElementById('toastContainer')
        };

        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.setupWebSocketHandlers();
        this.loadSettings();
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Connection
        this.els.connectBtn.addEventListener('click', () => this.handleConnect());

        // Upload
        this.els.uploadArea.addEventListener('click', () => this.els.imageInput.click());
        this.els.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.els.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        this.els.imageInput.addEventListener('change', (e) => this.handleImageSelect(e));
        this.els.removeImageBtn.addEventListener('click', () => this.removeImage());

        // Settings
        this.els.steps.addEventListener('input', (e) => {
            this.els.stepsValue.textContent = e.target.value;
        });

        this.els.cfg.addEventListener('input', (e) => {
            this.els.cfgValue.textContent = parseFloat(e.target.value).toFixed(1);
        });

        this.els.denoising.addEventListener('input', (e) => {
            this.els.denoisingValue.textContent = parseFloat(e.target.value).toFixed(2);
        });

        this.els.randomSeedBtn.addEventListener('click', () => {
            this.els.seed.value = '';
            this.showToast('Seed cleared - will use random seed', 'info');
        });

        // Generation
        this.els.generateBtn.addEventListener('click', () => this.handleGenerate());
        this.els.stopBtn.addEventListener('click', () => this.handleStop());

        // Results
        this.els.downloadBtn.addEventListener('click', () => this.downloadImage());
        this.els.useAsInputBtn.addEventListener('click', () => this.useResultAsInput());
        this.els.shareBtn.addEventListener('click', () => this.shareResult());

        // Enter key in prompts
        this.els.prompt.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.handleGenerate();
            }
        });
    }

    /**
     * Setup WebSocket handlers
     */
    setupWebSocketHandlers() {
        sdClient.on('connect', () => {
            this.updateConnectionStatus(true);
            this.showToast('Connected to server', 'success');
        });

        sdClient.on('disconnect', () => {
            this.updateConnectionStatus(false);
            this.showToast('Disconnected from server', 'error');
        });

        sdClient.on('authenticate', () => {
            this.showToast('Authentication successful', 'success');
            this.requestModels();
            this.switchToMainPanel();
        });

        sdClient.on('error', (error) => {
            console.error('Server error:', error);
            this.showToast(error.message || 'An error occurred', 'error');
            this.showError(error.message || 'An error occurred');
        });

        sdClient.on('models', (models) => {
            this.populateModels(models);
        });

        sdClient.on('progress', (progress) => {
            this.updateProgress(progress);
        });

        sdClient.on('preview', (data) => {
            this.updatePreview(data);
        });

        sdClient.on('result', (data) => {
            this.handleGenerationResult(data);
        });
    }

    /**
     * Handle connection button click
     */
    async handleConnect() {
        const endpoint = this.els.endpoint.value.trim();
        const password = this.els.password.value;

        if (!endpoint) {
            this.showToast('Please enter WebSocket endpoint', 'error');
            return;
        }

        if (!password) {
            this.showToast('Please enter password', 'error');
            return;
        }

        // Validate endpoint format
        if (!endpoint.startsWith('wss://') && !endpoint.startsWith('ws://')) {
            this.showToast('Endpoint must start with wss:// or ws://', 'error');
            return;
        }

        this.showLoading('Connecting to server...');
        this.els.connectBtn.disabled = true;

        try {
            await sdClient.connect(endpoint, password);
            this.saveSettings();
        } catch (error) {
            this.hideLoading();
            this.els.connectBtn.disabled = false;
            this.showToast(error.message || 'Failed to connect', 'error');
            console.error('Connection failed:', error);
        }
    }

    /**
     * Request models from server
     */
    requestModels() {
        this.showLoading('Fetching available models...');
        sdClient.requestModels();
        setTimeout(() => this.hideLoading(), 2000);
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(connected) {
        if (connected) {
            this.els.statusIndicator.classList.add('connected');
            this.els.statusText.textContent = 'Connected';
        } else {
            this.els.statusIndicator.classList.remove('connected');
            this.els.statusText.textContent = 'Disconnected';
        }
    }

    /**
     * Switch to main panel
     */
    switchToMainPanel() {
        this.hideLoading();
        this.els.connectionPanel.style.display = 'none';
        this.els.mainPanel.style.display = 'flex';
        this.els.connectBtn.disabled = false;
    }

    /**
     * Populate models dropdown
     */
    populateModels(models) {
        this.els.model.innerHTML = '';

        if (Array.isArray(models)) {
            models.forEach((model, index) => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                this.els.model.appendChild(option);
            });
        } else if (typeof models === 'object') {
            Object.keys(models).forEach(key => {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = models[key];
                this.els.model.appendChild(option);
            });
        }

        this.showToast(`Loaded ${this.els.model.options.length} models`, 'info');
    }

    /**
     * Handle image upload
     */
    handleImageSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showToast('Image size must be less than 10MB', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.uploadedImage = e.target.result;
            this.showUploadedImage();
            this.showToast('Image uploaded successfully', 'success');
        };
        reader.onerror = () => {
            this.showToast('Failed to read image file', 'error');
        };
        reader.readAsDataURL(file);
    }

    /**
     * Handle drag over
     */
    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        this.els.uploadArea.style.backgroundColor = 'rgba(99, 102, 241, 0.15)';
    }

    /**
     * Handle drop
     */
    handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        this.els.uploadArea.style.backgroundColor = '';

        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.els.imageInput.files = files;
            this.handleImageSelect({ target: { files } });
        }
    }

    /**
     * Show uploaded image preview
     */
    showUploadedImage() {
        this.els.previewImage.src = this.uploadedImage;
        this.els.uploadArea.style.display = 'none';
        this.els.uploadedImageDiv.style.display = 'block';
    }

    /**
     * Remove uploaded image
     */
    removeImage() {
        this.uploadedImage = null;
        this.els.imageInput.value = '';
        this.els.uploadArea.style.display = 'block';
        this.els.uploadedImageDiv.style.display = 'none';
        this.showToast('Image removed', 'info');
    }

    /**
     * Handle generate button click
     */
    async handleGenerate() {
        if (!sdClient.isConnectedToServer()) {
            this.showToast('Not connected to server', 'error');
            return;
        }

        if (this.isGenerating) {
            this.showToast('Generation already in progress', 'info');
            return;
        }

        const prompt = this.els.prompt.value.trim();
        if (!prompt) {
            this.showToast('Please enter a prompt', 'error');
            return;
        }

        this.isGenerating = true;
        this.updateGenerationUI(true);

        const params = {
            prompt: prompt,
            negative_prompt: this.els.negativePrompt.value,
            model: this.els.model.value,
            sampler: this.els.sampler.value,
            steps: parseInt(this.els.steps.value),
            cfg_scale: parseFloat(this.els.cfg.value),
            width: parseInt(this.els.width.value),
            height: parseInt(this.els.height.value),
            seed: this.els.seed.value || -1
        };

        // Store metadata for later display
        this.generationMetadata = {
            ...params,
            timestamp: new Date().toLocaleString()
        };

        try {
            if (this.uploadedImage) {
                // Use img2img
                params.denoising_strength = parseFloat(this.els.denoising.value);
                sdClient.generateImageToImage(this.uploadedImage, params);
                this.showToast('Starting image-to-image generation...', 'info');
            } else {
                // Use txt2img
                sdClient.generateImage(params);
                this.showToast('Starting image generation...', 'info');
            }

            this.showProgress();
        } catch (error) {
            this.isGenerating = false;
            this.updateGenerationUI(false);
            this.showToast(error.message, 'error');
        }
    }

    /**
     * Handle stop button click
     */
    handleStop() {
        sdClient.cancelGeneration();
        this.showToast('Cancellation requested...', 'info');
    }

    /**
     * Update progress
     */
    updateProgress(progress) {
        const percent = Math.min(100, Math.max(0, progress * 100));
        this.els.progressBar.style.setProperty('--progress', percent + '%');
        this.els.progressText.textContent = `Progress: ${Math.round(percent)}%`;
    }

    /**
     * Update preview image
     */
    updatePreview(data) {
        if (data.image) {
            this.els.resultImage.src = 'data:image/png;base64,' + data.image;
            this.els.resultsSection.style.display = 'flex';
            this.els.emptyState.style.display = 'none';
        }
    }

    /**
     * Handle generation result
     */
    handleGenerationResult(data) {
        this.isGenerating = false;
        this.updateGenerationUI(false);
        this.hideProgress();

        if (data.image) {
            this.lastResult = data;
            this.els.resultImage.src = 'data:image/png;base64,' + data.image;
            this.els.resultsSection.style.display = 'flex';
            this.els.emptyState.style.display = 'none';

            this.showToast('Image generated successfully!', 'success');

            // Display metadata
            if (data.metadata) {
                this.displayMetadata(data.metadata);
            } else if (this.generationMetadata) {
                this.displayMetadata(this.generationMetadata);
            }
        } else {
            this.showError('No image generated');
        }
    }

    /**
     * Show progress section
     */
    showProgress() {
        this.els.progressContainer.style.display = 'block';
        this.els.generationButtons.style.display = 'flex';
        this.els.generateBtn.style.display = 'none';
        this.els.stopBtn.style.display = 'block';
        this.els.progressText.textContent = 'Progress: 0%';
        this.els.progressBar.style.setProperty('--progress', '0%');
    }

    /**
     * Hide progress section
     */
    hideProgress() {
        this.els.progressContainer.style.display = 'none';
        this.els.generateBtn.style.display = 'block';
        this.els.stopBtn.style.display = 'none';
    }

    /**
     * Update generation UI state
     */
    updateGenerationUI(generating) {
        this.els.generateBtn.disabled = generating;
        this.els.prompt.disabled = generating;
        this.els.model.disabled = generating;
        this.els.sampler.disabled = generating;
        this.els.steps.disabled = generating;
        this.els.cfg.disabled = generating;

        if (generating) {
            this.els.generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        } else {
            this.els.generateBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Generate';
        }
    }

    /**
     * Display generation metadata
     */
    displayMetadata(metadata) {
        const metadataHTML = Object.entries(metadata)
            .map(([key, value]) => {
                const label = key.replace(/_/g, ' ').toUpperCase();
                const displayValue = Array.isArray(value) ? value.join(', ') : value;
                return `
                    <div class="metadata-item">
                        <div class="metadata-label">${label}</div>
                        <div class="metadata-value">${displayValue}</div>
                    </div>
                `;
            })
            .join('');

        this.els.metadataContent.innerHTML = metadataHTML;
        this.els.metadataSection.style.display = 'block';
    }

    /**
     * Download image
     */
    downloadImage() {
        if (!this.lastResult || !this.lastResult.image) {
            this.showToast('No image to download', 'error');
            return;
        }

        const link = document.createElement('a');
        link.href = 'data:image/png;base64,' + this.lastResult.image;
        link.download = `sd-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.showToast('Image downloaded successfully', 'success');
    }

    /**
     * Use result as input
     */
    useResultAsInput() {
        if (!this.lastResult || !this.lastResult.image) {
            this.showToast('No image to use', 'error');
            return;
        }

        this.uploadedImage = 'data:image/png;base64,' + this.lastResult.image;
        this.showUploadedImage();
        this.showToast('Result set as base image. Adjust settings and generate again.', 'success');

        // Scroll to top
        this.els.prompt.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Share result
     */
    shareResult() {
        if (!this.lastResult || !this.lastResult.image) {
            this.showToast('No image to share', 'error');
            return;
        }

        const shareText = `I generated this image with Stable Diffusion!\n\nPrompt: ${this.els.prompt.value}`;

        if (navigator.share) {
            navigator.share({
                title: 'Generated Image',
                text: shareText
            }).catch(error => console.log('Share cancelled:', error));
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(shareText);
            this.showToast('Share text copied to clipboard', 'success');
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        this.els.errorMessage.textContent = message;
        this.els.errorMessage.style.display = 'block';
        setTimeout(() => {
            this.els.errorMessage.style.display = 'none';
        }, 5000);
    }

    /**
     * Show loading overlay
     */
    showLoading(text = 'Loading...') {
        this.els.loadingText.textContent = text;
        this.els.loadingOverlay.style.display = 'flex';
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        this.els.loadingOverlay.style.display = 'none';
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };

        toast.innerHTML = `
            <i class="fas ${iconMap[type]}"></i>
            <span>${message}</span>
        `;

        this.els.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('removing');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    /**
     * Save settings to localStorage
     */
    saveSettings() {
        const settings = {
            endpoint: this.els.endpoint.value,
            model: this.els.model.value,
            sampler: this.els.sampler.value,
            steps: this.els.steps.value,
            cfg: this.els.cfg.value,
            denoising: this.els.denoising.value,
            width: this.els.width.value,
            height: this.els.height.value,
            prompt: this.els.prompt.value,
            negativePrompt: this.els.negativePrompt.value
        };

        localStorage.setItem('sdWebUISettings', JSON.stringify(settings));
    }

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        const saved = localStorage.getItem('sdWebUISettings');
        if (saved) {
            const settings = JSON.parse(saved);

            if (settings.endpoint) this.els.endpoint.value = settings.endpoint;
            if (settings.model) this.els.model.value = settings.model;
            if (settings.sampler) this.els.sampler.value = settings.sampler;
            if (settings.steps) this.els.steps.value = settings.steps;
            if (settings.cfg) this.els.cfg.value = settings.cfg;
            if (settings.denoising) this.els.denoising.value = settings.denoising;
            if (settings.width) this.els.width.value = settings.width;
            if (settings.height) this.els.height.value = settings.height;
            if (settings.prompt) this.els.prompt.value = settings.prompt;
            if (settings.negativePrompt) this.els.negativePrompt.value = settings.negativePrompt;

            // Update slider displays
            this.els.stepsValue.textContent = this.els.steps.value;
            this.els.cfgValue.textContent = parseFloat(this.els.cfg.value).toFixed(1);
            this.els.denoisingValue.textContent = parseFloat(this.els.denoising.value).toFixed(2);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.ui = new SDWebUI();
});
