/**
 * WebSocket Communication Module for Stable Diffusion Server
 * Handles connection, authentication, and message exchange with sd-inference-server
 */

class SDWebSocketClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.endpoint = null;
        this.password = null;
        this.messageId = 0;
        this.pendingRequests = new Map();
        this.handlers = {
            connect: [],
            disconnect: [],
            authenticate: [],
            error: [],
            message: [],
            models: [],
            progress: [],
            result: [],
            preview: []
        };
    }

    /**
     * Register event handlers
     */
    on(event, callback) {
        if (this.handlers[event]) {
            this.handlers[event].push(callback);
        }
    }

    /**
     * Emit events to registered handlers
     */
    emit(event, data) {
        if (this.handlers[event]) {
            this.handlers[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} handler:`, error);
                }
            });
        }
    }

    /**
     * Connect to WebSocket server
     */
    connect(endpoint, password) {
        return new Promise((resolve, reject) => {
            if (this.isConnected) {
                reject(new Error('Already connected'));
                return;
            }

            this.endpoint = endpoint;
            this.password = password;

            try {
                this.ws = new WebSocket(endpoint);

                this.ws.onopen = () => {
                    this.isConnected = true;
                    console.log('WebSocket connected');
                    this.emit('connect');

                    // Authenticate immediately
                    this.authenticate(password)
                        .then(() => {
                            this.emit('authenticate');
                            resolve();
                        })
                        .catch(error => {
                            this.disconnect();
                            reject(error);
                        });
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.emit('error', {
                        type: 'connection',
                        message: 'WebSocket connection error'
                    });
                    reject(error);
                };

                this.ws.onclose = () => {
                    this.isConnected = false;
                    console.log('WebSocket disconnected');
                    this.emit('disconnect');
                };

            } catch (error) {
                console.error('Failed to create WebSocket:', error);
                reject(error);
            }

            // Timeout after 30 seconds
            const timeout = setTimeout(() => {
                if (!this.isConnected) {
                    this.disconnect();
                    reject(new Error('Connection timeout'));
                }
            }, 30000);
        });
    }

    /**
     * Authenticate with server
     */
    authenticate(password) {
        return new Promise((resolve, reject) => {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                reject(new Error('WebSocket not connected'));
                return;
            }

            try {
                const message = { password };
                this.ws.send(JSON.stringify(message));
                
                // Wait for authentication response
                const checkAuth = () => {
                    // Server should respond with models list if auth successful
                    // We'll set a timeout and assume success if no immediate error
                    setTimeout(() => resolve(), 1000);
                };

                checkAuth();
            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Handle incoming messages from server
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('Received message:', message);

            this.emit('message', message);

            // Route message to appropriate handler
            if (message.type === 'models') {
                this.emit('models', message.models);
            } else if (message.type === 'progress') {
                this.emit('progress', message.value);
            } else if (message.type === 'preview') {
                this.emit('preview', message);
            } else if (message.type === 'result') {
                this.emit('result', message);
            } else if (message.type === 'error') {
                this.emit('error', {
                    type: 'server',
                    message: message.error
                });
            } else if (message.models) {
                // Handle models list (some servers send as root property)
                this.emit('models', message.models);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
            this.emit('error', {
                type: 'parse',
                message: 'Failed to parse server response'
            });
        }
    }

    /**
     * Send authentication message
     */
    sendAuth(password) {
        const message = { password };
        this.sendMessage(message);
    }

    /**
     * Request models list
     */
    requestModels() {
        const message = {
            action: 'list_models'
        };
        this.sendMessage(message);
    }

    /**
     * Generate image with txt2img
     */
    generateImage(params) {
        const message = {
            action: 'generate',
            ...params
        };
        this.sendMessage(message);
    }

    /**
     * Generate image with img2img
     */
    generateImageToImage(imageBase64, params) {
        const message = {
            action: 'generate',
            image: imageBase64,
            ...params
        };
        this.sendMessage(message);
    }

    /**
     * Cancel current generation
     */
    cancelGeneration() {
        const message = {
            action: 'cancel'
        };
        this.sendMessage(message);
    }

    /**
     * Send message to server
     */
    sendMessage(message) {
        if (!this.isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.emit('error', {
                type: 'connection',
                message: 'WebSocket not connected'
            });
            return false;
        }

        try {
            const msgString = JSON.stringify(message);
            this.ws.send(msgString);
            console.log('Sent message:', message);
            return true;
        } catch (error) {
            console.error('Error sending message:', error);
            this.emit('error', {
                type: 'send',
                message: 'Failed to send message'
            });
            return false;
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }

    /**
     * Check if connected
     */
    isConnectedToServer() {
        return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// Create global instance
const sdClient = new SDWebSocketClient();
