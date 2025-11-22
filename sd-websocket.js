/**
 * Stable Diffusion WebSocket Client
 * Handles connection and communication with sd-inference-server
 */

class SDWebSocketClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.endpoint = null;
        this.password = null;
        this.handlers = {
            connect: [],
            disconnect: [],
            error: [],
            models: [],
            progress: [],
            download_progress: [],
            preview: [],
            result: [],
            download_complete: []
        };
    }

    on(event, callback) {
        if (this.handlers[event]) {
            this.handlers[event].push(callback);
        }
    }

    emit(event, data) {
        if (this.handlers[event]) {
            this.handlers[event].forEach(cb => {
                try {
                    cb(data);
                } catch (e) {
                    console.error(`Error in ${event} handler:`, e);
                }
            });
        }
    }

    connect(endpoint, password) {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(endpoint);
                this.endpoint = endpoint;
                this.password = password;

                this.ws.onopen = () => {
                    this.isConnected = true;
                    // Send authentication
                    this.ws.send(JSON.stringify({ password: password }));
                    // Wait a bit for server response, then resolve
                    setTimeout(() => {
                        this.emit('connect');
                        resolve();
                    }, 500);
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.emit('error', 'WebSocket connection error');
                    reject(error);
                };

                this.ws.onclose = () => {
                    this.isConnected = false;
                    this.emit('disconnect');
                };
            } catch (error) {
                reject(error);
            }

            // Timeout
            setTimeout(() => {
                if (!this.isConnected) {
                    reject(new Error('Connection timeout'));
                }
            }, 15000);
        });
    }

    handleMessage(data) {
        try {
            // Handle binary data (Blob/ArrayBuffer) - likely image preview
            if (data instanceof Blob) {
                console.log('[WebSocket] Received binary Blob, converting to data URL...');
                const reader = new FileReader();
                reader.onload = () => {
                    // reader.result is like "data:application/octet-stream;base64,xxx"
                    // Extract just the base64 part and create proper PNG data URL
                    const result = reader.result;
                    const base64Match = result.match(/,(.+)$/);
                    if (base64Match) {
                        const base64Data = base64Match[1];
                        const imageDataUrl = `data:image/png;base64,${base64Data}`;
                        console.log('[WebSocket] Preview data URL ready:', imageDataUrl.substring(0, 50) + '...');
                        this.emit('preview', imageDataUrl);
                    } else {
                        console.warn('[WebSocket] Could not extract base64 from blob');
                    }
                };
                reader.onerror = () => {
                    console.error('[WebSocket] Error reading Blob');
                };
                reader.readAsDataURL(data);
                return;
            }

            if (data instanceof ArrayBuffer) {
                console.log('[WebSocket] Received binary ArrayBuffer');
                // Convert ArrayBuffer to Blob then to data URL
                const blob = new Blob([data], { type: 'application/octet-stream' });
                const reader = new FileReader();
                reader.onload = () => {
                    const result = reader.result;
                    const base64Match = result.match(/,(.+)$/);
                    if (base64Match) {
                        const base64Data = base64Match[1];
                        const imageDataUrl = `data:image/png;base64,${base64Data}`;
                        this.emit('preview', imageDataUrl);
                    }
                };
                reader.readAsDataURL(blob);
                return;
            }

            // Handle text data (JSON)
            console.log('[WebSocket] Received text:', data.substring ? data.substring(0, 100) : data);
            const message = JSON.parse(data);
            console.log('[WebSocket] Parsed message type:', message.type);

            if (message.type === 'models') {
                this.emit('models', message.models || []);
            } else if (message.type === 'progress') {
                this.emit('progress', message.value || 0);
            } else if (message.type === 'download') {
                // Server sends: { type: "download", data: { status: "started|progress|success|error", ... } }
                const downloadData = message.data || {};
                console.log('[WebSocket] Download event:', downloadData.status, downloadData);
                
                if (downloadData.status === 'progress') {
                    // Progress: { status: "progress", progress: 0.5, rate: 10.5, eta: 120 }
                    this.emit('download_progress', downloadData.progress || 0);
                } else if (downloadData.status === 'started') {
                    // Started: { status: "started", label: "filename.safetensors" }
                    console.log('[WebSocket] Download started:', downloadData.label);
                } else if (downloadData.status === 'success') {
                    // Success: { status: "success", label: "filename.safetensors" }
                    console.log('[WebSocket] Download success:', downloadData.label);
                    this.emit('download_complete', { filename: downloadData.label });
                } else if (downloadData.status === 'error') {
                    // Error: { status: "error", message: "...", trace: "..." }
                    console.error('[WebSocket] Download error:', downloadData.message);
                    this.emit('error', downloadData.message);
                }
            } else if (message.type === 'preview') {
                this.emit('preview', message.image);
            } else if (message.type === 'result') {
                this.emit('result', message);
            } else if (message.type === 'error') {
                console.error('[WebSocket] Error from server:', message.data?.message || message.error);
                this.emit('error', message.data?.message || message.error);
            } else if (message.models) {
                this.emit('models', message.models);
            } else {
                console.warn('[WebSocket] Unknown message type:', message);
            }
        } catch (e) {
            console.error('[WebSocket] Error parsing message:', e, 'Data type:', data.constructor.name);
        }
    }

    requestModels() {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ action: 'list_models' }));
        }
    }

    generate(params) {
        if (this.isConnected) {
            params.action = 'generate';
            this.ws.send(JSON.stringify(params));
        }
    }

    cancel() {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ action: 'cancel' }));
        }
    }

    send(message) {
        if (this.isConnected && this.ws) {
            try {
                let payload;
                if (typeof message === 'string') {
                    payload = message;
                } else {
                    payload = JSON.stringify(message);
                }
                console.log('[WebSocket] Sending:', payload);
                this.ws.send(payload);
                return true;
            } catch (e) {
                console.error('[WebSocket] Error sending message:', e);
                return false;
            }
        } else {
            console.error('[WebSocket] Not connected or ws is null. Connected:', this.isConnected, 'WS:', !!this.ws);
            return false;
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }
}

// Global instance
const sdWebSocket = new SDWebSocketClient();
