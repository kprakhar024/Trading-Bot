// Global variables
let currentSide = 'BUY';
let socket = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeSideButtons();
    loadBalance();
    loadPositions();
    loadOrders();
    updatePrice();
    initializeWebSocket();
    
    // Auto-refresh data every 10 seconds
    setInterval(() => {
        loadBalance();
        loadPositions();
        loadOrders();
    }, 10000);
    
    // Update price every 2 seconds
    setInterval(updatePrice, 2000);
});

// WebSocket initialization
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to WebSocket');
        showToast('Connected to server', 'success');
    });
    
    socket.on('price_update', function(data) {
        if (data.symbol === getCurrentSymbol()) {
            document.getElementById('currentPrice').textContent = 
                `$${parseFloat(data.price).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
    });
}

// Tab functionality
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            document.getElementById(tabName + 'Form').classList.add('active');
        });
    });
}

// Side button functionality
function initializeSideButtons() {
    const sideButtons = document.querySelectorAll('.btn-side');
    sideButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const parent = this.parentElement;
            parent.querySelectorAll('.btn-side').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentSide = this.dataset.side;
        });
    });
}

// Get current symbol from active form
function getCurrentSymbol() {
    const activeForm = document.querySelector('.tab-content.active');
    const symbolInput = activeForm.querySelector('input[id$="Symbol"]');
    return symbolInput ? symbolInput.value.toUpperCase() : 'BTCUSDT';
}

// API Functions
async function loadBalance() {
    try {
        const response = await fetch('/api/balance');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalBalance').textContent = 
                parseFloat(data.data.totalWalletBalance).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('availableBalance').textContent = 
                parseFloat(data.data.availableBalance).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            
            const pnl = parseFloat(data.data.totalUnrealizedProfit);
            const pnlElement = document.getElementById('unrealizedPnL');
            pnlElement.textContent = pnl.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            pnlElement.style.color = pnl >= 0 ? 'var(--success-color)' : 'var(--danger-color)';
        }
    } catch (error) {
        console.error('Error loading balance:', error);
    }
}

async function updatePrice() {
    const symbol = getCurrentSymbol();
    try {
        const response = await fetch(`/api/price/${symbol}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('currentPrice').textContent = 
                `$${parseFloat(data.data.price).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
    } catch (error) {
        console.error('Error updating price:', error);
    }
}

async function loadPositions() {
    try {
        const response = await fetch('/api/positions');
        const data = await response.json();
        
        const tbody = document.getElementById('positionsBody');
        
        if (data.success && data.data.length > 0) {
            tbody.innerHTML = data.data.map(pos => {
                const pnl = parseFloat(pos.unRealizedProfit);
                const pnlColor = pnl >= 0 ? 'var(--success-color)' : 'var(--danger-color)';
                
                return `
                    <tr>
                        <td><strong>${pos.symbol}</strong></td>
                        <td>${parseFloat(pos.positionAmt).toFixed(3)}</td>
                        <td>$${parseFloat(pos.entryPrice).toLocaleString()}</td>
                        <td>$${parseFloat(pos.markPrice).toLocaleString()}</td>
                        <td style="color: ${pnlColor}">${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="closePosition('${pos.symbol}')">
                                <i class="fas fa-times"></i> Close
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No open positions</td></tr>';
        }
    } catch (error) {
        console.error('Error loading positions:', error);
    }
}

async function loadOrders() {
    try {
        const response = await fetch('/api/orders');
        const data = await response.json();
        
        const tbody = document.getElementById('ordersBody');
        
        if (data.success && data.data.length > 0) {
            tbody.innerHTML = data.data.map(order => `
                <tr>
                    <td><strong>${order.symbol}</strong></td>
                    <td><span class="badge badge-warning">${order.type}</span></td>
                    <td class="${order.side === 'BUY' ? 'text-success' : 'text-danger'}">${order.side}</td>
                    <td>$${parseFloat(order.price || 0).toLocaleString()}</td>
                    <td>${parseFloat(order.origQty).toFixed(3)}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="cancelOrder('${order.symbol}', ${order.orderId})">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No open orders</td></tr>';
        }
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

// Order placement functions
async function placeMarketOrder() {
    const symbol = document.getElementById('marketSymbol').value;
    const quantity = document.getElementById('marketQuantity').value;
    const reduceOnly = document.getElementById('marketReduceOnly').checked;
    const side = document.querySelector('#marketForm .btn-side.active').dataset.side;
    
    if (!quantity) {
        showToast('Please enter quantity', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/order/market', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, side, quantity, reduceOnly })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Market ${side} order placed successfully!`, 'success');
            document.getElementById('marketQuantity').value = '';
            loadBalance();
            loadPositions();
            loadOrders();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Error placing order: ' + error.message, 'error');
    }
}

async function placeLimitOrder() {
    const symbol = document.getElementById('limitSymbol').value;
    const quantity = document.getElementById('limitQuantity').value;
    const price = document.getElementById('limitPrice').value;
    const timeInForce = document.getElementById('limitTIF').value;
    const side = document.querySelector('#limitForm .btn-side.active').dataset.side;
    
    if (!quantity || !price) {
        showToast('Please enter quantity and price', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/order/limit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, side, quantity, price, timeInForce })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Limit ${side} order placed successfully!`, 'success');
            document.getElementById('limitQuantity').value = '';
            document.getElementById('limitPrice').value = '';
            loadOrders();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Error placing order: ' + error.message, 'error');
    }
}

async function placeStopMarketOrder() {
    const symbol = document.getElementById('stopMarketSymbol').value;
    const quantity = document.getElementById('stopMarketQuantity').value;
    const stopPrice = document.getElementById('stopMarketStopPrice').value;
    const reduceOnly = document.getElementById('stopMarketReduceOnly').checked;
    const side = document.querySelector('#stop-marketForm .btn-side.active').dataset.side;
    
    if (!quantity || !stopPrice) {
        showToast('Please enter quantity and stop price', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/order/stop-market', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, side, quantity, stopPrice, reduceOnly })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Stop Market ${side} order placed successfully!`, 'success');
            document.getElementById('stopMarketQuantity').value = '';
            document.getElementById('stopMarketStopPrice').value = '';
            loadOrders();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Error placing order: ' + error.message, 'error');
    }
}

async function placeStopLimitOrder() {
    const symbol = document.getElementById('stopLimitSymbol').value;
    const quantity = document.getElementById('stopLimitQuantity').value;
    const price = document.getElementById('stopLimitPrice').value;
    const stopPrice = document.getElementById('stopLimitStopPrice').value;
    const side = document.querySelector('#stop-limitForm .btn-side.active').dataset.side;
    
    if (!quantity || !price || !stopPrice) {
        showToast('Please enter all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/order/stop-limit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, side, quantity, price, stopPrice, timeInForce: 'GTC' })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Stop Limit ${side} order placed successfully!`, 'success');
            document.getElementById('stopLimitQuantity').value = '';
            document.getElementById('stopLimitPrice').value = '';
            document.getElementById('stopLimitStopPrice').value = '';
            loadOrders();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Error placing order: ' + error.message, 'error');
    }
}

async function setLeverage() {
    const symbol = document.getElementById('leverageSymbol').value;
    const leverage = document.getElementById('leverageValue').value;
    
    if (!leverage) {
        showToast('Please enter leverage value', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/leverage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, leverage })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Error setting leverage: ' + error.message, 'error');
    }
}

async function cancelOrder(symbol, orderId) {
    if (!confirm(`Cancel order ${orderId} for ${symbol}?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/order/cancel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, orderId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Order cancelled successfully!', 'success');
            loadOrders();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Error cancelling order: ' + error.message, 'error');
    }
}

async function closePosition(symbol) {
    if (!confirm(`Close position for ${symbol}?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/position/close', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Position closed successfully!', 'success');
            loadBalance();
            loadPositions();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Error closing position: ' + error.message, 'error');
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 'info-circle';
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="fas fa-${icon}" style="font-size: 1.25rem;"></i>
            <div>${message}</div>
        </div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}