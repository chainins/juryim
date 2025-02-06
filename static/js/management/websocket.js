class ManagementWebSocket {
    constructor() {
        this.connect();
        this.handlers = new Map();
    }

    connect() {
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        this.socket = new WebSocket(
            `${wsScheme}://${window.location.host}/ws/management/`
        );

        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.heartbeat();
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            setTimeout(() => this.connect(), 5000);
        };
    }

    handleMessage(data) {
        const handlers = this.handlers.get(data.type) || [];
        handlers.forEach(handler => handler(data));
    }

    subscribe(type, handler) {
        if (!this.handlers.has(type)) {
            this.handlers.set(type, []);
        }
        this.handlers.get(type).push(handler);
    }

    subscribeToWithdrawal(withdrawalId) {
        this.socket.send(JSON.stringify({
            type: 'subscribe_withdrawal',
            withdrawal_id: withdrawalId
        }));
    }

    heartbeat() {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ type: 'heartbeat' }));
            setTimeout(() => this.heartbeat(), 30000);
        }
    }
}

// Initialize WebSocket connection
const managementWS = new ManagementWebSocket();

// Example usage in withdrawal list page
document.addEventListener('DOMContentLoaded', function() {
    const withdrawalRows = document.querySelectorAll('[data-withdrawal-id]');
    
    withdrawalRows.forEach(row => {
        const withdrawalId = row.dataset.withdrawalId;
        managementWS.subscribeToWithdrawal(withdrawalId);
    });

    managementWS.subscribe('withdrawal_update', (data) => {
        const row = document.querySelector(
            `[data-withdrawal-id="${data.withdrawal_id}"]`
        );
        if (row) {
            const statusEl = row.querySelector('.status');
            if (statusEl) {
                statusEl.textContent = data.status;
                statusEl.className = `status status-${data.status.toLowerCase()}`;
            }
        }
    });

    managementWS.subscribe('notification', (data) => {
        // Show notification using your preferred notification system
        showNotification(data.message, data.level);
    });
}); 