// WebSocket Connection
class GamblingWebSocket {
    constructor() {
        this.connect();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    connect() {
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        this.socket = new WebSocket(
            `${wsScheme}://${window.location.host}/ws/gambling/`
        );

        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            
            // Watch current game if on game detail page
            const gameId = document.querySelector('[data-game-id]')?.dataset.gameId;
            if (gameId) {
                this.watchGame(gameId);
            }
        };

        this.socket.onclose = (e) => {
            console.log('WebSocket disconnected');
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.connect();
                }, this.reconnectDelay * this.reconnectAttempts);
            }
        };

        this.socket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleMessage(data);
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    watchGame(gameId) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'watch_game',
                game_id: gameId
            }));
        }
    }

    unwatchGame(gameId) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'unwatch_game',
                game_id: gameId
            }));
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'game_update':
                this.handleGameUpdate(data);
                break;
            case 'bet_placed':
                this.handleBetPlaced(data);
                break;
            case 'game_completed':
                this.handleGameCompleted(data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    handleGameUpdate(data) {
        const gameCard = document.querySelector(`[data-game-id="${data.game_id}"]`);
        if (gameCard) {
            // Update game stats
            if (data.data.total_pool) {
                gameCard.querySelector('.total-pool').textContent = data.data.total_pool;
            }
            if (data.data.total_bets) {
                gameCard.querySelector('.total-bets').textContent = data.data.total_bets;
            }
        }
    }

    handleBetPlaced(data) {
        const gameCard = document.querySelector(`[data-game-id="${data.game_id}"]`);
        if (gameCard) {
            // Update total pool
            const poolElement = gameCard.querySelector('.total-pool');
            if (poolElement) {
                poolElement.textContent = data.data.total_pool;
            }
            
            // Add bet to list if on game detail page
            const betList = document.querySelector('.bet-list');
            if (betList && data.data.bet_html) {
                betList.insertAdjacentHTML('afterbegin', data.data.bet_html);
            }
        }
    }

    handleGameCompleted(data) {
        const gameCard = document.querySelector(`[data-game-id="${data.game_id}"]`);
        if (gameCard) {
            // Update game status
            const statusBadge = gameCard.querySelector('.game-status');
            if (statusBadge) {
                statusBadge.className = 'badge badge-completed';
                statusBadge.textContent = 'Completed';
            }
            
            // Show result if available
            if (data.data.result_html) {
                const resultContainer = gameCard.querySelector('.game-result');
                if (resultContainer) {
                    resultContainer.innerHTML = data.data.result_html;
                }
            }
            
            // Reload page after short delay if on game detail page
            if (window.location.pathname.includes(`/game/${data.game_id}/`)) {
                setTimeout(() => window.location.reload(), 2000);
            }
        }
    }
}

// Game Countdown Timer
class GameCountdown {
    constructor(element) {
        this.element = element;
        this.endTime = new Date(element.dataset.endTime);
        this.updateInterval = null;
        this.start();
    }

    start() {
        this.update();
        this.updateInterval = setInterval(() => this.update(), 1000);
    }

    stop() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }

    update() {
        const now = new Date();
        const diff = this.endTime - now;
        
        if (diff <= 0) {
            this.element.querySelector('.countdown').textContent = 'Ended';
            this.stop();
            setTimeout(() => window.location.reload(), 1000);
            return;
        }
        
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        this.element.querySelector('.countdown').textContent = 
            `${minutes}m ${seconds}s`;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize WebSocket
    window.gamblingSocket = new GamblingWebSocket();
    
    // Initialize countdowns
    document.querySelectorAll('.time-remaining').forEach(el => {
        new GameCountdown(el);
    });
    
    // Initialize bet form handlers
    const betForm = document.getElementById('betForm');
    if (betForm) {
        const amountInput = betForm.querySelector('#id_amount');
        const feePercentage = parseFloat(betForm.dataset.feePercentage);
        
        if (amountInput && feePercentage) {
            amountInput.addEventListener('input', () => {
                const amount = parseFloat(amountInput.value) || 0;
                const fee = amount * (feePercentage / 100);
                document.getElementById('feeAmount').textContent = 
                    fee.toFixed(8);
            });
        }
    }
}); 