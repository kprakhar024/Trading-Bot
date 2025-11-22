"""
Flask Web UI for Binance Futures Trading Bot
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.bot import BinanceFuturesBot
from src.validators import ValidationError

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global bot instance
bot = None


def init_bot():
    """Initialize the trading bot"""
    global bot
    
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    testnet = os.getenv('TESTNET', 'True').lower() == 'true'
    
    if not api_key or not api_secret:
        raise ValueError("API credentials not found in .env file")
    
    bot = BinanceFuturesBot(api_key, api_secret, testnet=testnet)
    return bot


# Initialize bot on startup
try:
    init_bot()
    print("✓ Trading bot initialized successfully")
except Exception as e:
    print(f"✗ Error initializing bot: {e}")
    print("Please check your .env file and API credentials")


# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/balance')
def get_balance():
    """Get account balance"""
    try:
        balance = bot.get_account_balance()
        return jsonify({
            'success': True,
            'data': balance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/price/<symbol>')
def get_price(symbol):
    """Get current price for symbol"""
    try:
        price = bot.get_current_price(symbol)
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol.upper(),
                'price': price
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/positions')
def get_positions():
    """Get current positions"""
    try:
        symbol = request.args.get('symbol')
        positions = bot.get_position_info(symbol)
        return jsonify({
            'success': True,
            'data': positions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/orders')
def get_orders():
    """Get open orders"""
    try:
        symbol = request.args.get('symbol')
        orders = bot.get_open_orders(symbol)
        return jsonify({
            'success': True,
            'data': orders
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/leverage', methods=['POST'])
def set_leverage():
    """Set leverage for symbol"""
    try:
        data = request.json
        symbol = data.get('symbol')
        leverage = int(data.get('leverage'))
        
        response = bot.set_leverage(symbol, leverage)
        
        return jsonify({
            'success': True,
            'message': f'Leverage set to {leverage}x for {symbol}',
            'data': response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/order/market', methods=['POST'])
def place_market_order():
    """Place market order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        side = data.get('side')
        quantity = float(data.get('quantity'))
        reduce_only = data.get('reduceOnly', False)
        
        order = bot.place_market_order(symbol, side, quantity, reduce_only)
        
        return jsonify({
            'success': True,
            'message': 'Market order placed successfully',
            'data': order
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/order/limit', methods=['POST'])
def place_limit_order():
    """Place limit order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        side = data.get('side')
        quantity = float(data.get('quantity'))
        price = float(data.get('price'))
        time_in_force = data.get('timeInForce', 'GTC')
        reduce_only = data.get('reduceOnly', False)
        
        order = bot.place_limit_order(
            symbol, side, quantity, price, time_in_force, reduce_only
        )
        
        return jsonify({
            'success': True,
            'message': 'Limit order placed successfully',
            'data': order
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/order/stop-market', methods=['POST'])
def place_stop_market_order():
    """Place stop market order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        side = data.get('side')
        quantity = float(data.get('quantity'))
        stop_price = float(data.get('stopPrice'))
        reduce_only = data.get('reduceOnly', False)
        
        order = bot.place_stop_market_order(
            symbol, side, quantity, stop_price, reduce_only
        )
        
        return jsonify({
            'success': True,
            'message': 'Stop market order placed successfully',
            'data': order
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/order/stop-limit', methods=['POST'])
def place_stop_limit_order():
    """Place stop limit order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        side = data.get('side')
        quantity = float(data.get('quantity'))
        price = float(data.get('price'))
        stop_price = float(data.get('stopPrice'))
        time_in_force = data.get('timeInForce', 'GTC')
        reduce_only = data.get('reduceOnly', False)
        
        order = bot.place_stop_limit_order(
            symbol, side, quantity, price, stop_price, time_in_force, reduce_only
        )
        
        return jsonify({
            'success': True,
            'message': 'Stop limit order placed successfully',
            'data': order
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/order/cancel', methods=['POST'])
def cancel_order():
    """Cancel an order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        order_id = int(data.get('orderId'))
        
        response = bot.cancel_order(symbol, order_id)
        
        return jsonify({
            'success': True,
            'message': 'Order cancelled successfully',
            'data': response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/position/close', methods=['POST'])
def close_position():
    """Close a position"""
    try:
        data = request.json
        symbol = data.get('symbol')
        
        response = bot.close_position(symbol)
        
        if response.get('status') == 'NO_POSITION':
            return jsonify({
                'success': False,
                'error': f'No open position for {symbol}'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Position closed successfully',
            'data': response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'data': 'Connected to trading bot'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)