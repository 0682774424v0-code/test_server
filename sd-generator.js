/**
 * Stable Diffusion Generator UI Controller
 * Handles all UI interactions for image generation
 */

// Global function to switch channels and tabs
function switchChannel(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
        tab.style.display = 'none';
    });

    // Show selected tab
    const tab = document.getElementById(tabName + '-tab');
    if (tab) {
        tab.classList.remove('hidden');
        tab.style.display = 'block';
    }

    // Update active channels
    document.querySelectorAll('.channel').forEach(ch => {
        ch.classList.remove('active');
    });
    
    // Find and activate the clicked channel
    const channels = document.querySelectorAll('.channel');
    for (let ch of channels) {
        if (ch.textContent.toLowerCase().includes(tabName.replace('sd-', '')) || 
            ch.getAttribute('onclick')?.includes(tabName)) {
            ch.classList.add('active');
        }
    }
}

class SDGenerator {
    constructor() {
        this.uploadedImage = null;
        this.isGenerating = false;
        this.init();
    }

    init() {
        this.setupServerButton();
        this.setupConnectionTab();
        this.setupTxt2imgTab();
        this.setupImg2imgTab();
        this.setupModelsTab();
        this.setupWebSocketHandlers();
    }

    setupServerButton() {
        const metadataBtn = document.querySelector('[title="Metadata Image"]');
        const sdBtn = document.getElementById('sd-server-btn');
        
        if (metadataBtn) {
            metadataBtn.addEventListener('click', () => {
                const metaList = document.getElementById('metadata-channel-list');
                const sdList = document.getElementById('sd-channel-list');
                
                metaList.classList.add('active');
                metaList.style.display = 'flex';
                sdList.classList.remove('active');
                sdList.style.display = 'none';
                
                metadataBtn.classList.add('active');
                sdBtn.classList.remove('active');
                
                // Switch to first metadata tab
                switchChannel('view');
            });
        }
        
        if (sdBtn) {
            sdBtn.addEventListener('click', () => {
                const metaList = document.getElementById('metadata-channel-list');
                const sdList = document.getElementById('sd-channel-list');
                
                metaList.classList.remove('active');
                metaList.style.display = 'none';
                sdList.classList.add('active');
                sdList.style.display = 'flex';
                
                sdBtn.classList.add('active');
                metadataBtn.classList.remove('active');
                
                // Switch to connection tab
                switchChannel('sd-connect');
            });
        }
    }

    setupConnectionTab() {
        const connectBtn = document.getElementById('sd-connect-btn');
        const endpointInput = document.getElementById('sd-endpoint');
        const passwordInput = document.getElementById('sd-password');

        connectBtn?.addEventListener('click', async () => {
            const endpoint = endpointInput?.value.trim();
            const password = passwordInput?.value;

            if (!endpoint || !password) {
                alert('Please enter both endpoint and password');
                return;
            }

            connectBtn.disabled = true;
            connectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';

            try {
                await sdWebSocket.connect(endpoint, password);
            } catch (error) {
                alert('Connection failed: ' + error.message);
                connectBtn.disabled = false;
                connectBtn.innerHTML = '<i class="fas fa-link"></i> Connect';
            }
        });
    }

    setupTxt2imgTab() {
        const generateBtn = document.getElementById('sd-generate');
        const stopBtn = document.getElementById('sd-stop');
        const stepsSlider = document.getElementById('sd-steps');
        const cfgSlider = document.getElementById('sd-cfg');
        const randomSeedBtn = document.getElementById('sd-random-seed');

        stepsSlider?.addEventListener('input', (e) => {
            document.getElementById('steps-val').textContent = e.target.value;
        });

        cfgSlider?.addEventListener('input', (e) => {
            document.getElementById('cfg-val').textContent = parseFloat(e.target.value).toFixed(1);
        });

        randomSeedBtn?.addEventListener('click', () => {
            document.getElementById('sd-seed').value = '';
        });

        generateBtn?.addEventListener('click', () => {
            this.generateTxt2img();
        });

        stopBtn?.addEventListener('click', () => {
            sdWebSocket.cancel();
            generateBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            this.isGenerating = false;
        });
    }

    setupImg2imgTab() {
        const dropArea = document.getElementById('sd-img2img-drop');
        const input = document.getElementById('sd-img2img-input');
        const generateBtn = document.getElementById('sd-img2img-generate');
        const stopBtn = document.getElementById('sd-img2img-stop');
        const denoisingSlider = document.getElementById('sd-img2img-denoising');
        const stepsSlider = document.getElementById('sd-img2img-steps');
        const cfgSlider = document.getElementById('sd-img2img-cfg');

        // Drag and drop
        dropArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.style.opacity = '0.7';
        });

        dropArea?.addEventListener('dragleave', () => {
            dropArea.style.opacity = '1';
        });

        dropArea?.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.style.opacity = '1';
            const files = e.dataTransfer.files;
            if (files.length) {
                this.loadImg2imgImage(files[0]);
            }
        });

        dropArea?.addEventListener('click', () => {
            input?.click();
        });

        input?.addEventListener('change', (e) => {
            if (e.target.files.length) {
                this.loadImg2imgImage(e.target.files[0]);
            }
        });

        denoisingSlider?.addEventListener('input', (e) => {
            document.getElementById('denoising-val').textContent = parseFloat(e.target.value).toFixed(2);
        });

        stepsSlider?.addEventListener('input', (e) => {
            document.getElementById('img2img-steps-val').textContent = e.target.value;
        });

        cfgSlider?.addEventListener('input', (e) => {
            document.getElementById('img2img-cfg-val').textContent = parseFloat(e.target.value).toFixed(1);
        });

        generateBtn?.addEventListener('click', () => {
            this.generateImg2img();
        });

        stopBtn?.addEventListener('click', () => {
            sdWebSocket.cancel();
            generateBtn.style.display = 'block';
            stopBtn.style.display = 'none';
            this.isGenerating = false;
        });
    }

    setupModelsTab() {
        // Load API keys from localStorage
        const civitaiToken = localStorage.getItem('sd-civitai-token');
        const huggingfaceToken = localStorage.getItem('sd-huggingface-token');
        
        if (civitaiToken) document.getElementById('sd-civitai-key').value = civitaiToken;
        if (huggingfaceToken) document.getElementById('sd-huggingface-token').value = huggingfaceToken;

        // Save API Keys button
        document.getElementById('sd-save-keys')?.addEventListener('click', () => {
            const civitaiKey = document.getElementById('sd-civitai-key').value;
            const huggingfaceToken = document.getElementById('sd-huggingface-token').value;
            
            localStorage.setItem('sd-civitai-token', civitaiKey);
            localStorage.setItem('sd-huggingface-token', huggingfaceToken);
            
            alert('✅ API Keys saved!');
        });

        // Model type selector
        const modelTypeSelect = document.getElementById('sd-model-type');
        const downloadHint = document.getElementById('sd-download-hint');
        const downloadLabel = document.getElementById('sd-download-label');

        modelTypeSelect?.addEventListener('change', (e) => {
            const type = e.target.value;
            const typeNames = {
                'checkpoint': '🤖 Checkpoint (Model)',
                'lora': '🎨 LoRA',
                'upscaler': '📈 Upscaler'
            };
            downloadLabel.textContent = `Download ${typeNames[type]}`;
        });

        // Universal download button
        document.getElementById('sd-download-btn')?.addEventListener('click', () => {
            const url = document.getElementById('sd-download-url').value.trim();
            const modelType = document.getElementById('sd-model-type').value;

            if (!url) {
                alert('Please enter a download link');
                return;
            }

            this.handleUniversalDownload(url, modelType);
        });
    }

    handleUniversalDownload(url, modelType) {
        // Determine source from URL
        let source = 'direct';
        let processedUrl = url;

        if (url.includes('civitai.com')) {
            source = 'civitai';
        } else if (url.includes('huggingface.co')) {
            source = 'huggingface';
            // Extract model ID from HuggingFace URL
            const match = url.match(/huggingface\.co\/models\/([^\/]+\/[^\/]+)/);
            if (match) {
                processedUrl = match[1];
            }
        } else if (url.includes('drive.google.com')) {
            source = 'google_drive';
            // Extract file ID from Google Drive URL
            const fileId = this.extractGoogleDriveFileId(url);
            if (!fileId) {
                alert('❌ Invalid Google Drive URL');
                return;
            }
            processedUrl = fileId;
        } else if (url.match(/^https?:\/\//)) {
            source = 'direct';
        } else if (url.match(/^[a-zA-Z0-9_\-]+\/[a-zA-Z0-9_\-]+$/)) {
            // Looks like a HuggingFace model ID (username/model-name)
            source = 'huggingface';
            processedUrl = url;
        }

        this.startDownload(processedUrl, source, modelType);
    }

    startDownload(url, source, modelType) {
        const progressSection = document.getElementById('sd-download-progress-section');
        const progressFill = document.getElementById('sd-download-progress-fill');
        const progressText = document.getElementById('sd-download-progress-text');
        const statusText = document.getElementById('sd-download-status');

        if (!progressSection || !progressFill || !progressText || !statusText) {
            console.error('Download progress elements not found');
            alert('❌ Download UI elements not found');
            return;
        }

        progressSection.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = '0%';
        
        const modelTypeLabel = {
            'checkpoint': '🤖 Model',
            'lora': '🎨 LoRA',
            'upscaler': '📈 Upscaler'
        }[modelType] || 'File';

        statusText.textContent = `📥 Downloading ${modelTypeLabel} from ${source}...`;
        console.log('Starting download:', { url, source, modelType });

        // Check connection first
        if (!sdWebSocket.isConnected) {
            alert('❌ Not connected to server. Please connect first.');
            statusText.textContent = '❌ Not connected to server';
            progressSection.style.display = 'none';
            return;
        }

        const payload = {
            action: 'download',
            source: source,
            url: url,
            model_type: modelType,
            token: localStorage.getItem('sd-huggingface-token') || ''
        };

        console.log('Sending WebSocket payload:', JSON.stringify(payload));
        const success = sdWebSocket.send(payload);

        if (!success) {
            alert('❌ Failed to send download request. Check console for details.');
            statusText.textContent = '❌ Failed to send request';
            progressSection.style.display = 'none';
            console.error('WebSocket send failed');
        } else {
            console.log('Download request sent successfully');
        }
    }

    loadImg2imgImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.uploadedImage = e.target.result;
            const preview = document.getElementById('sd-img2img-preview');
            preview.innerHTML = `<img src="${this.uploadedImage}" style="max-width: 100%; max-height: 300px; border-radius: 4px;">`;
        };
        reader.readAsDataURL(file);
    }

    generateTxt2img() {
        if (!sdWebSocket.isConnected) {
            alert('Not connected to server');
            return;
        }

        if (this.isGenerating) {
            alert('Generation in progress');
            return;
        }

        const prompt = document.getElementById('sd-prompt')?.value;
        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }

        this.isGenerating = true;
        document.getElementById('sd-generate').style.display = 'none';
        document.getElementById('sd-stop').style.display = 'block';
        document.getElementById('sd-progress-section').style.display = 'block';

        const params = {
            prompt: prompt,
            negative_prompt: document.getElementById('sd-negative-prompt')?.value || '',
            model: document.getElementById('sd-model')?.value || '',
            sampler: document.getElementById('sd-sampler')?.value || 'DPM++ 2M Karras',
            steps: parseInt(document.getElementById('sd-steps')?.value || 20),
            cfg_scale: parseFloat(document.getElementById('sd-cfg')?.value || 7.5),
            width: parseInt(document.getElementById('sd-width')?.value || 512),
            height: parseInt(document.getElementById('sd-height')?.value || 512),
            seed: document.getElementById('sd-seed')?.value || '-1'
        };

        sdWebSocket.generate(params);
    }

    generateImg2img() {
        if (!sdWebSocket.isConnected) {
            alert('Not connected to server');
            return;
        }

        if (!this.uploadedImage) {
            alert('Please upload an image first');
            return;
        }

        this.isGenerating = true;
        document.getElementById('sd-img2img-generate').style.display = 'none';
        document.getElementById('sd-img2img-stop').style.display = 'block';
        document.getElementById('sd-img2img-progress-section').style.display = 'block';

        const params = {
            prompt: document.getElementById('sd-img2img-prompt')?.value || '',
            negative_prompt: document.getElementById('sd-img2img-negative')?.value || '',
            image: this.uploadedImage,
            denoising_strength: parseFloat(document.getElementById('sd-img2img-denoising')?.value || 0.75),
            sampler: document.getElementById('sd-img2img-sampler')?.value || 'DPM++ 2M Karras',
            steps: parseInt(document.getElementById('sd-img2img-steps')?.value || 20),
            cfg_scale: parseFloat(document.getElementById('sd-img2img-cfg')?.value || 7.5)
        };

        sdWebSocket.generate(params);
    }

    setupWebSocketHandlers() {
        sdWebSocket.on('connect', () => {
            console.log('Connected to SD server');
            document.getElementById('sd-status-indicator').style.backgroundColor = '#3ba55c';
            document.getElementById('sd-status-text').textContent = 'Connected';
            document.getElementById('sd-connect-btn').disabled = false;
            document.getElementById('sd-connect-btn').innerHTML = '<i class="fas fa-link"></i> Connect';
            // Request models
            sdWebSocket.requestModels();
        });

        sdWebSocket.on('disconnect', () => {
            document.getElementById('sd-status-indicator').style.backgroundColor = '#ed4245';
            document.getElementById('sd-status-text').textContent = 'Disconnected';
        });

        sdWebSocket.on('error', (error) => {
            console.error('SD Error:', error);
            alert('Error: ' + error);
        });

        sdWebSocket.on('models', (models) => {
            const select = document.getElementById('sd-model');
            if (select && models.length > 0) {
                select.innerHTML = models.map(m => `<option value="${m}">${m}</option>`).join('');
            }
        });

        sdWebSocket.on('progress', (progress) => {
            const percent = Math.round(progress * 100);
            document.getElementById('sd-progress-fill').style.width = percent + '%';
            document.getElementById('sd-progress-text').textContent = percent + '%';
            
            const img2imgFill = document.getElementById('sd-img2img-progress-fill');
            if (img2imgFill) {
                img2imgFill.style.width = percent + '%';
                document.getElementById('sd-img2img-progress-text').textContent = percent + '%';
            }
        });

        sdWebSocket.on('download_progress', (progress) => {
            const percent = Math.round(progress * 100);
            const progressFill = document.getElementById('sd-download-progress-fill');
            const progressText = document.getElementById('sd-download-progress-text');
            const statusText = document.getElementById('sd-download-status');
            
            if (progressFill) {
                progressFill.style.width = percent + '%';
            }
            if (progressText) {
                progressText.textContent = percent + '%';
            }
            if (statusText && percent < 100) {
                statusText.textContent = `📥 Downloading... ${percent}%`;
            }
        });

        sdWebSocket.on('download_complete', (data) => {
            console.log('[SDGenerator] Download complete event received:', data);
            const statusText = document.getElementById('sd-download-status');
            const progressSection = document.getElementById('sd-download-progress-section');
            
            if (statusText) {
                if (data && data.error) {
                    statusText.textContent = `❌ Download error: ${data.error}`;
                } else {
                    statusText.textContent = `✅ Download complete! Model saved as: ${data?.filename || data?.path || 'model'}`;
                }
            }
            
            // Hide progress after a delay
            setTimeout(() => {
                if (progressSection) {
                    progressSection.style.display = 'none';
                }
            }, 3000);
            
            // Refresh models list
            setTimeout(() => {
                sdWebSocket.requestModels();
            }, 1000);
        });

        sdWebSocket.on('preview', (image) => {
            if (image) {
                const img = document.getElementById('sd-result-image');
                if (img) {
                    // Image is already a complete data URL from WebSocket
                    // Don't wrap it again - just use it directly
                    img.src = image;
                    console.log('[SDGenerator] Preview image set');
                }
            }
        });

        sdWebSocket.on('result', (data) => {
            this.isGenerating = false;
            document.getElementById('sd-generate').style.display = 'block';
            document.getElementById('sd-stop').style.display = 'none';
            document.getElementById('sd-progress-section').style.display = 'none';

            document.getElementById('sd-img2img-generate').style.display = 'block';
            document.getElementById('sd-img2img-stop').style.display = 'none';
            document.getElementById('sd-img2img-progress-section').style.display = 'none';

            if (data.image) {
                const img = document.getElementById('sd-result-image');
                if (img) {
                    img.src = 'data:image/png;base64,' + data.image;
                    document.getElementById('sd-results-section').style.display = 'block';
                }

                const img2imgImg = document.getElementById('sd-img2img-result-image');
                if (img2imgImg) {
                    img2imgImg.src = 'data:image/png;base64,' + data.image;
                    document.getElementById('sd-img2img-results-section').style.display = 'block';
                }

                // Setup download buttons
                document.getElementById('sd-download')?.addEventListener('click', () => {
                    this.downloadImage(data.image);
                }, { once: true });

                document.getElementById('sd-img2img-download')?.addEventListener('click', () => {
                    this.downloadImage(data.image);
                }, { once: true });

                document.getElementById('sd-use-as-input')?.addEventListener('click', () => {
                    this.uploadedImage = 'data:image/png;base64,' + data.image;
                    this.switchTab('sd-img2img');
                    const preview = document.getElementById('sd-img2img-preview');
                    preview.innerHTML = `<img src="${this.uploadedImage}" style="max-width: 100%; max-height: 300px; border-radius: 4px;">`;
                }, { once: true });
            }
        });
    }

    downloadImage(base64) {
        const link = document.createElement('a');
        link.href = 'data:image/png;base64,' + base64;
        link.download = 'sd-' + Date.now() + '.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    startDownload(url, source, modelType) {
        const progressSection = document.getElementById('sd-download-progress-section');
        const progressFill = document.getElementById('sd-download-progress-fill');
        const progressText = document.getElementById('sd-download-progress-text');
        const statusText = document.getElementById('sd-download-status');

        if (!progressSection || !progressFill || !progressText || !statusText) {
            console.error('Download progress elements not found');
            alert('❌ Download UI elements not found');
            return;
        }

        progressSection.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = '0%';
        
        const modelTypeLabel = {
            'checkpoint': '🤖 Model',
            'lora': '🎨 LoRA',
            'upscaler': '📈 Upscaler'
        }[modelType] || 'File';

        statusText.textContent = `📥 Downloading ${modelTypeLabel} from ${source}...`;
        console.log('[SDGenerator] Starting download:', { url, source, modelType });

        // Send download request via WebSocket
        if (!sdWebSocket.isConnected) {
            console.error('[SDGenerator] Not connected to server');
            alert('❌ Not connected to server. Please connect first.');
            progressSection.style.display = 'none';
            return;
        }

        // Server expects: { type: "download", data: { type: "...", url: "...", civitai_token: "...", hf_token: "..." } }
        const payload = {
            type: 'download',
            data: {
                type: modelType,  // 'checkpoint', 'lora', 'upscaler'
                url: url,
                civitai_token: localStorage.getItem('sd-civitai-token') || '',
                hf_token: localStorage.getItem('sd-huggingface-token') || ''
            }
        };
        
        console.log('[SDGenerator] Sending download payload:', payload);
        const success = sdWebSocket.send(payload);

        if (!success) {
            console.error('[SDGenerator] Failed to send download request');
            alert('❌ Failed to send download request');
            progressSection.style.display = 'none';
        }
    }

    extractGoogleDriveFileId(url) {
        const match = url.match(/\/d\/([a-zA-Z0-9-_]+)/);
        return match ? match[1] : null;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sdGenerator = new SDGenerator();
});
