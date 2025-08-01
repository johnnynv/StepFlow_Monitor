/**
 * Dashboard functionality
 */

class Dashboard {
    constructor() {
        this.refreshInterval = 30000; // 30 seconds
        this.refreshTimer = null;
        
        this.init();
    }
    
    init() {
        this.loadDashboardData();
        this.setupEventListeners();
        this.startAutoRefresh();
        this.setupWebSocketListeners();
    }
    
    setupEventListeners() {
        // New execution form
        const form = document.getElementById('newExecutionForm');
        if (form) {
            form.addEventListener('submit', this.handleNewExecution.bind(this));
        }
    }
    
    setupWebSocketListeners() {
        if (window.wsClient) {
            // Listen for execution updates
            wsClient.on('execution_update', (data) => {
                this.handleExecutionUpdate(data);
            });
            
            wsClient.on('execution_started', (data) => {
                this.handleExecutionStarted(data);
            });
            
            wsClient.on('execution_completed', (data) => {
                this.handleExecutionCompleted(data);
            });
            
            // Refresh data when connected
            wsClient.on('connected', () => {
                this.loadDashboardData();
            });
        }
    }
    
    async loadDashboardData() {
        try {
            // Load all dashboard data in parallel
            const [statistics, recentExecutions, activeExecutions] = await Promise.all([
                API.loadStatistics(),
                API.loadExecutions({ limit: 10 }),
                API.loadActiveExecutions()
            ]);
            
            this.updateStatistics(statistics);
            this.updateRecentExecutions(recentExecutions);
            this.updateActiveExecutions(activeExecutions);
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    updateStatistics(stats) {
        // Update stat cards
        document.getElementById('totalExecutions').textContent = 
            stats.total_executions || 0;
        
        document.getElementById('activeExecutions').textContent = 
            stats.active_count || 0;
        
        document.getElementById('successRate').textContent = 
            Formatters.percentage(stats.success_rate || 0);
        
        document.getElementById('avgDuration').textContent = 
            Formatters.duration(stats.avg_duration || 0);
    }
    
    updateRecentExecutions(executions) {
        const tbody = document.getElementById('recentExecutionsBody');
        if (!tbody) return;
        
        if (executions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No executions found</td></tr>';
            return;
        }
        
        tbody.innerHTML = executions.map(execution => `
            <tr class="execution-row">
                <td>
                    <div class="execution-name">${execution.name || 'Unnamed'}</div>
                    <div class="execution-command">${execution.command}</div>
                </td>
                <td>${Formatters.statusBadge(execution.status)}</td>
                <td>${Formatters.duration(execution.duration_seconds)}</td>
                <td>${Formatters.timestamp(execution.started_at)}</td>
                <td>
                    <div class="execution-actions">
                        <button onclick="viewExecution('${execution.id}')" class="btn btn-sm btn-secondary">
                            View
                        </button>
                        ${execution.status === 'running' ? 
                            `<button onclick="cancelExecution('${execution.id}')" class="btn btn-sm btn-danger">
                                Cancel
                            </button>` : ''
                        }
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    updateActiveExecutions(executions) {
        const section = document.getElementById('activeExecutionsSection');
        const list = document.getElementById('activeExecutionsList');
        
        if (!section || !list) return;
        
        if (executions.length === 0) {
            section.style.display = 'none';
            return;
        }
        
        section.style.display = 'block';
        
        list.innerHTML = executions.map(execution => `
            <div class="active-execution">
                <div class="active-execution-header">
                    <div class="active-execution-name">${execution.name || 'Unnamed'}</div>
                    <div class="active-execution-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${execution.progress_percentage}%"></div>
                        </div>
                        <span class="progress-text">
                            ${execution.completed_steps}/${execution.total_steps}
                        </span>
                    </div>
                </div>
                <div class="execution-command">${execution.command}</div>
            </div>
        `).join('');
    }
    
    async handleNewExecution(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const executionData = {
            name: formData.get('executionName') || undefined,
            command: formData.get('command'),
            working_directory: formData.get('workingDirectory') || '.',
            timeout: formData.get('timeout') ? parseInt(formData.get('timeout')) : undefined
        };
        
        try {
            const execution = await API.startExecution(executionData);
            console.log('Execution started:', execution);
            
            // Hide dialog
            hideNewExecutionDialog();
            
            // Refresh dashboard
            this.loadDashboardData();
            
            // Show success message
            this.showSuccess(`Execution "${execution.name || execution.id}" started successfully`);
            
            // Optionally redirect to execution view
            // window.location.href = `/execution?id=${execution.id}`;
            
        } catch (error) {
            console.error('Failed to start execution:', error);
            this.showError('Failed to start execution: ' + error.message);
        }
    }
    
    handleExecutionUpdate(execution) {
        // Update statistics if this affects counts
        this.loadDashboardData();
    }
    
    handleExecutionStarted(execution) {
        console.log('New execution started:', execution);
        this.loadDashboardData();
        this.showInfo(`New execution "${execution.name || execution.id}" started`);
    }
    
    handleExecutionCompleted(execution) {
        console.log('Execution completed:', execution);
        this.loadDashboardData();
        
        const message = execution.status === 'completed' 
            ? `Execution "${execution.name || execution.id}" completed successfully`
            : `Execution "${execution.name || execution.id}" failed`;
        
        execution.status === 'completed' 
            ? this.showSuccess(message)
            : this.showError(message);
    }
    
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.loadDashboardData();
        }, this.refreshInterval);
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showInfo(message) {
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 1001;
            max-width: 400px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            info: '#17a2b8',
            warning: '#ffc107'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
}

// Global functions for UI interactions
function showNewExecutionDialog() {
    const dialog = document.getElementById('newExecutionDialog');
    if (dialog) {
        dialog.style.display = 'flex';
    }
}

function hideNewExecutionDialog() {
    const dialog = document.getElementById('newExecutionDialog');
    if (dialog) {
        dialog.style.display = 'none';
        // Reset form
        const form = document.getElementById('newExecutionForm');
        if (form) {
            form.reset();
        }
    }
}

function goToLive() {
    window.location.href = '/execution';
}

function goToHistory() {
    window.location.href = '/history';
}

function viewExecution(executionId) {
    window.location.href = `/execution?id=${executionId}`;
}

async function cancelExecution(executionId) {
    if (confirm('Are you sure you want to cancel this execution?')) {
        try {
            await API.stopExecution(executionId);
            console.log('Execution cancelled:', executionId);
            // Refresh dashboard
            if (window.dashboard) {
                window.dashboard.loadDashboardData();
            }
        } catch (error) {
            console.error('Failed to cancel execution:', error);
            alert('Failed to cancel execution: ' + error.message);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});