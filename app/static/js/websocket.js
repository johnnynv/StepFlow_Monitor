/**
 * WebSocket client for real-time communication
 */

class WebSocketClient {
    constructor(url = 'ws://localhost:8765') {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.listeners = new Map();
        this.connected = false;
        
        this.connect();
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = (event) => {
                console.log('🔗 WebSocket connected');
                this.connected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                this.emit('connected', event);
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('🔌 WebSocket disconnected');
                this.connected = false;
                this.updateConnectionStatus(false);
                this.emit('disconnected', event);
                
                // Attempt to reconnect
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.emit('error', error);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.attemptReconnect();
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.emit('max_reconnect_attempts');
        }
    }
    
    handleMessage(data) {
        const { type, data: messageData, timestamp } = data;
        
        // Emit specific event for message type
        this.emit(type, messageData, timestamp);
        
        // Emit general message event
        this.emit('message', data);
    }
    
    send(type, data = {}) {
        if (this.connected && this.ws.readyState === WebSocket.OPEN) {
            const message = {
                type,
                data,
                timestamp: new Date().toISOString()
            };
            
            this.ws.send(JSON.stringify(message));
            return true;
        } else {
            console.warn('WebSocket is not connected. Cannot send message.');
            return false;
        }
    }
    
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    emit(event, ...args) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(...args);
                } catch (error) {
                    console.error(`Error in ${event} listener:`, error);
                }
            });
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            if (connected) {
                statusElement.textContent = '🟢 Connected';
                statusElement.className = 'connection-status connected';
            } else {
                statusElement.textContent = '🔴 Disconnected';
                statusElement.className = 'connection-status disconnected';
            }
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
    
    // Convenience methods for common message types
    ping() {
        return this.send('ping');
    }
    
    subscribeToExecution(executionId) {
        return this.send('subscribe_execution', { execution_id: executionId });
    }
    
    getStatus() {
        return this.send('get_status');
    }
}

// Global WebSocket instance
let wsClient = null;

// Initialize WebSocket when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    wsClient = new WebSocketClient();
    
    // Make it globally available
    window.wsClient = wsClient;
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketClient;
}