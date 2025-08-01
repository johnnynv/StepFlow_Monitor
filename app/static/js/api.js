/**
 * API client for ContainerFlow Visualizer
 */

class APIClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }
    
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseUrl}/api${endpoint}`;
        
        const config = {
            method: method.toUpperCase(),
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        if (data && (method.toUpperCase() === 'POST' || method.toUpperCase() === 'PUT')) {
            config.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error(`API request failed: ${method} ${endpoint}`, error);
            throw error;
        }
    }
    
    // Execution endpoints
    async getExecutions(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const endpoint = `/executions${queryParams ? `?${queryParams}` : ''}`;
        return this.request('GET', endpoint);
    }
    
    async getExecution(executionId) {
        return this.request('GET', `/executions/${executionId}`);
    }
    
    async createExecution(executionData) {
        return this.request('POST', '/executions', executionData);
    }
    
    async cancelExecution(executionId) {
        return this.request('POST', `/executions/${executionId}/cancel`);
    }
    
    async getExecutionLogs(executionId, stepId = null) {
        const endpoint = stepId 
            ? `/executions/${executionId}/logs?step_id=${stepId}`
            : `/executions/${executionId}/logs`;
        return this.request('GET', endpoint);
    }
    
    async getActiveExecutions() {
        return this.request('GET', '/executions/active');
    }
    
    async getExecutionStatistics() {
        return this.request('GET', '/executions/statistics');
    }
    
    // Artifact endpoints
    async getArtifact(artifactId) {
        return this.request('GET', `/artifacts/${artifactId}`);
    }
    
    async downloadArtifact(artifactId) {
        const url = `${this.baseUrl}/api/artifacts/${artifactId}/download`;
        window.open(url, '_blank');
    }
    
    async getExecutionArtifacts(executionId) {
        return this.request('GET', `/artifacts/execution/${executionId}`);
    }
    
    // Health endpoints
    async healthCheck() {
        return this.request('GET', '/health');
    }
    
    async getSystemStatus() {
        return this.request('GET', '/health/status');
    }
}

// Global API client instance
const apiClient = new APIClient();

// Utility functions for common API operations
const API = {
    // Executions
    async loadExecutions(filters = {}) {
        try {
            const response = await apiClient.getExecutions(filters);
            return response.executions || [];
        } catch (error) {
            console.error('Failed to load executions:', error);
            return [];
        }
    },
    
    async loadExecution(executionId) {
        try {
            const response = await apiClient.getExecution(executionId);
            return response;
        } catch (error) {
            console.error(`Failed to load execution ${executionId}:`, error);
            return null;
        }
    },
    
    async startExecution(executionData) {
        try {
            const response = await apiClient.createExecution(executionData);
            return response.execution;
        } catch (error) {
            console.error('Failed to start execution:', error);
            throw error;
        }
    },
    
    async stopExecution(executionId) {
        try {
            await apiClient.cancelExecution(executionId);
            return true;
        } catch (error) {
            console.error(`Failed to cancel execution ${executionId}:`, error);
            return false;
        }
    },
    
    async loadActiveExecutions() {
        try {
            const response = await apiClient.getActiveExecutions();
            return response.executions || [];
        } catch (error) {
            console.error('Failed to load active executions:', error);
            return [];
        }
    },
    
    async loadStatistics() {
        try {
            const response = await apiClient.getExecutionStatistics();
            return response.statistics || {};
        } catch (error) {
            console.error('Failed to load statistics:', error);
            return {};
        }
    },
    
    // Artifacts
    async loadExecutionArtifacts(executionId) {
        try {
            const response = await apiClient.getExecutionArtifacts(executionId);
            return response.artifacts || [];
        } catch (error) {
            console.error(`Failed to load artifacts for execution ${executionId}:`, error);
            return [];
        }
    },
    
    // Health
    async checkHealth() {
        try {
            const response = await apiClient.healthCheck();
            return response;
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'unhealthy', error: error.message };
        }
    },
    
    async loadSystemStatus() {
        try {
            const response = await apiClient.getSystemStatus();
            return response;
        } catch (error) {
            console.error('Failed to load system status:', error);
            return {};
        }
    }
};

// Utility functions for data formatting
const Formatters = {
    duration(seconds) {
        if (!seconds || seconds < 0) return '-';
        
        if (seconds < 60) {
            return `${seconds.toFixed(1)}s`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${minutes}m ${remainingSeconds}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    },
    
    timestamp(isoString) {
        if (!isoString) return '-';
        
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        
        if (diffMinutes < 1) {
            return 'Just now';
        } else if (diffMinutes < 60) {
            return `${diffMinutes}m ago`;
        } else if (diffMinutes < 1440) {
            const hours = Math.floor(diffMinutes / 60);
            return `${hours}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    },
    
    percentage(value) {
        if (typeof value !== 'number') return '-';
        return `${value.toFixed(1)}%`;
    },
    
    fileSize(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    },
    
    statusBadge(status) {
        const badges = {
            pending: { class: 'status-pending', text: 'Pending' },
            running: { class: 'status-running', text: 'Running' },
            completed: { class: 'status-completed', text: 'Completed' },
            failed: { class: 'status-failed', text: 'Failed' },
            cancelled: { class: 'status-cancelled', text: 'Cancelled' }
        };
        
        const badge = badges[status] || badges.pending;
        return `<span class="status-badge ${badge.class}">${badge.text}</span>`;
    }
};

// Make available globally
window.API = API;
window.Formatters = Formatters;
window.apiClient = apiClient;