🤖 Binance Futures Trading Bot

A professional trading bot for Binance Futures Testnet with Web UI and CLI support.
## ✨ Features

- ✅ **Multiple Order Types**: Market, Limit, Stop Market, Stop Limit
- ✅ **Dual Interface**: Modern Web UI + Powerful CLI
- ✅ **Real-time Dashboard**: Live balance, positions, and PnL tracking
- ✅ **Position Management**: Track and close positions with one click
- ✅ **Leverage Control**: Adjust leverage (1-125x)
- ✅ **Comprehensive Logging**: All API requests and errors logged
- ✅ **Safe Testing**: Built for Binance Testnet only

---

## 🚀 Quick Start

### 1. Installation


# Clone repository
git clone https://github.com/yourusername/binance-trading-bot.git
cd binance-trading-bot

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt


### 2. Get API Keys

1. Register at [Binance Futures Testnet](https://testnet.binancefuture.com/)
2. Generate API Key and Secret
3. Copy `.env.example` to `.env`
4. Add your credentials to `.env`

env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
TESTNET=True


### 3. Run the Bot

**Web UI:**

python run_ui.py
# Open browser to http://localhost:5000


**CLI:**

python main.py balance


---

## 💻 Usage

### Web Interface

python run_ui.py

Features:
- Real-time account overview
- Interactive trading panel with tabs
- Live positions and orders
- One-click position closing
- Leverage management

### Command Line

#### Basic Commands

# Check balance
python main.py balance

# Get current price
python main.py price BTCUSDT

# View positions
python main.py positions

# Set leverage
python main.py set-leverage BTCUSDT 10


#### Trading


# Market order
python main.py market BTCUSDT BUY 0.001

# Limit order
python main.py limit BTCUSDT BUY 0.001 50000

# Stop market order
python main.py stop-market BTCUSDT SELL 0.001 45000 --reduce-only

# Stop limit order
python main.py stop-limit BTCUSDT SELL 0.001 44500 45000

#### Order Management


# View open orders
python main.py orders

# Cancel order
python main.py cancel BTCUSDT 123456789

# Close position
python main.py close BTCUSDT
```

---

## 📁 Project Structure

```
binance-trading-bot/
├── src/                    # Core bot logic
│   ├── bot.py             # Main bot implementation
│   ├── orders.py          # Order management
│   ├── validators.py      # Input validation
│   └── logger.py          # Logging system
│
├── ui/                     # Web interface
│   ├── app.py             # Flask application
│   ├── templates/         # HTML templates
│   └── static/            # CSS & JavaScript
│
├── main.py                # CLI entry point
├── run_ui.py              # Web UI launcher
├── requirements.txt       # Dependencies
└── .env                   # Configuration (create from .env.example)


---

## 📚 Examples

### Example 1: Quick Trade


# Set leverage
python main.py set-leverage BTCUSDT 5

# Buy
python main.py market BTCUSDT BUY 0.001

# Check position
python main.py positions

# Close position
python main.py close BTCUSDT


### Example 2: Programmatic Usage

python
from src.bot import BinanceFuturesBot
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize bot
bot = BinanceFuturesBot(
    api_key=os.getenv('BINANCE_API_KEY'),
    api_secret=os.getenv('BINANCE_API_SECRET'),
    testnet=True
)

# Get balance
balance = bot.get_account_balance()
print(f"Balance: {balance['totalWalletBalance']} USDT")

# Place order
order = bot.place_market_order('BTCUSDT', 'BUY', 0.001)
print(f"Order ID: {order['orderId']}")

# Close position
bot.close_position('BTCUSDT')


---

## 🔧 Troubleshooting

### Common Issues

**"API credentials not found"**

# Create .env file from example
cp .env.example .env
# Add your API keys


**"Module not found"**

pip install -r requirements.txt


**"Port 5000 already in use"**
python
# In run_ui.py, change port:
socketio.run(app, debug=True, host='0.0.0.0', port=5001)


**Orders not executing**

# Check balance
python main.py balance

# Verify minimum quantity (BTC: 0.001, ETH: 0.01)

---

## 🛡️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/balance` | GET | Get account balance |
| `/api/price/<symbol>` | GET | Get current price |
| `/api/positions` | GET | Get open positions |
| `/api/orders` | GET | Get open orders |
| `/api/order/market` | POST | Place market order |
| `/api/order/limit` | POST | Place limit order |
| `/api/order/stop-market` | POST | Place stop market order |
| `/api/order/stop-limit` | POST | Place stop limit order |
| `/api/order/cancel` | POST | Cancel order |
| `/api/position/close` | POST | Close position |
| `/api/leverage` | POST | Set leverage |

---

## 🗺️ Roadmap

- [ ] OCO (One-Cancels-Other) orders
- [ ] TWAP orders
- [ ] Grid trading strategy
- [ ] WebSocket real-time updates
- [ ] Backtesting functionality
- [ ] Telegram notifications

---

## ⚠️ Disclaimer

**Important:** This software is for educational purposes only.

- ⚠️ NOT financial advice
- ⚠️ Use at your own risk
- ⚠️ Trading involves substantial risk of loss
- ⚠️ Designed for TESTNET only
- ⚠️ No warranty provided

Always test thoroughly on testnet before considering real trading.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request


