"""
CLI interface for Binance Futures Trading Bot
"""

import click
import os
import sys
from dotenv import load_dotenv
from tabulate import tabulate
from colorama import Fore, Style

from src.bot import BinanceFuturesBot
from src.validators import ValidationError

# Load environment variables
load_dotenv()


def get_bot():
    """Initialize and return bot instance"""
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    testnet = os.getenv('TESTNET', 'True').lower() == 'true'
    
    if not api_key or not api_secret:
        click.echo(Fore.RED + "Error: API credentials not found in .env file" + Style.RESET_ALL)
        sys.exit(1)
    
    return BinanceFuturesBot(api_key, api_secret, testnet=testnet)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Binance Futures Trading Bot CLI
    
    A comprehensive trading bot for Binance Futures Testnet
    """
    pass


@cli.command()
def balance():
    """Get account balance"""
    try:
        bot = get_bot()
        balance_info = bot.get_account_balance()
        
        data = [
            ['Total Wallet Balance', f"{balance_info['totalWalletBalance']} USDT"],
            ['Available Balance', f"{balance_info['availableBalance']} USDT"],
            ['Unrealized Profit', f"{balance_info['totalUnrealizedProfit']} USDT"],
        ]
        
        click.echo(Fore.CYAN + "\n=== Account Balance ===" + Style.RESET_ALL)
        click.echo(tabulate(data, tablefmt='grid'))
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.argument('symbol')
def price(symbol):
    """Get current price for a symbol"""
    try:
        bot = get_bot()
        current_price = bot.get_current_price(symbol)
        
        click.echo(Fore.GREEN + f"\n{symbol.upper()}: ${current_price:,.2f}" + Style.RESET_ALL)
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.option('--symbol', '-s', help='Trading symbol (optional)')
def positions(symbol):
    """Get current positions"""
    try:
        bot = get_bot()
        positions_list = bot.get_position_info(symbol)
        
        if not positions_list:
            click.echo(Fore.YELLOW + "\nNo open positions" + Style.RESET_ALL)
            return
        
        data = []
        for pos in positions_list:
            data.append([
                pos['symbol'],
                pos['positionSide'],
                pos['positionAmt'],
                pos['entryPrice'],
                pos['markPrice'],
                pos['unRealizedProfit'],
                pos['leverage'],
            ])
        
        headers = ['Symbol', 'Side', 'Amount', 'Entry Price', 'Mark Price', 'PnL', 'Leverage']
        
        click.echo(Fore.CYAN + "\n=== Open Positions ===" + Style.RESET_ALL)
        click.echo(tabulate(data, headers=headers, tablefmt='grid'))
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.argument('symbol')
@click.argument('leverage', type=int)
def set_leverage(symbol, leverage):
    """Set leverage for a symbol"""
    try:
        bot = get_bot()
        response = bot.set_leverage(symbol, leverage)
        
        click.echo(Fore.GREEN + f"\n✓ Leverage set to {leverage}x for {symbol.upper()}" + Style.RESET_ALL)
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.argument('symbol')
@click.argument('side', type=click.Choice(['BUY', 'SELL'], case_sensitive=False))
@click.argument('quantity', type=float)
@click.option('--reduce-only', is_flag=True, help='Reduce only flag')
def market(symbol, side, quantity, reduce_only):
    """Place a market order"""
    try:
        bot = get_bot()
        
        # Confirm order
        click.echo(Fore.YELLOW + "\n=== Order Confirmation ===" + Style.RESET_ALL)
        click.echo(f"Type: MARKET")
        click.echo(f"Symbol: {symbol.upper()}")
        click.echo(f"Side: {side.upper()}")
        click.echo(f"Quantity: {quantity}")
        click.echo(f"Reduce Only: {reduce_only}")
        
        if not click.confirm('\nDo you want to place this order?'):
            click.echo(Fore.YELLOW + "Order cancelled" + Style.RESET_ALL)
            return
        
        order = bot.place_market_order(symbol, side, quantity, reduce_only)
        
        click.echo(Fore.GREEN + f"\n✓ Market order placed successfully!" + Style.RESET_ALL)
        click.echo(f"Order ID: {order['orderId']}")
        click.echo(f"Status: {order['status']}")
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.argument('symbol')
@click.argument('side', type=click.Choice(['BUY', 'SELL'], case_sensitive=False))
@click.argument('quantity', type=float)
@click.argument('price', type=float)
@click.option('--tif', default='GTC', type=click.Choice(['GTC', 'IOC', 'FOK']), 
              help='Time in force')
@click.option('--reduce-only', is_flag=True, help='Reduce only flag')
def limit(symbol, side, quantity, price, tif, reduce_only):
    """Place a limit order"""
    try:
        bot = get_bot()
        
        # Confirm order
        click.echo(Fore.YELLOW + "\n=== Order Confirmation ===" + Style.RESET_ALL)
        click.echo(f"Type: LIMIT")
        click.echo(f"Symbol: {symbol.upper()}")
        click.echo(f"Side: {side.upper()}")
        click.echo(f"Quantity: {quantity}")
        click.echo(f"Price: ${price}")
        click.echo(f"Time in Force: {tif}")
        click.echo(f"Reduce Only: {reduce_only}")
        
        if not click.confirm('\nDo you want to place this order?'):
            click.echo(Fore.YELLOW + "Order cancelled" + Style.RESET_ALL)
            return
        
        order = bot.place_limit_order(symbol, side, quantity, price, tif, reduce_only)
        
        click.echo(Fore.GREEN + f"\n✓ Limit order placed successfully!" + Style.RESET_ALL)
        click.echo(f"Order ID: {order['orderId']}")
        click.echo(f"Status: {order['status']}")
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.argument('symbol')
@click.argument('side', type=click.Choice(['BUY', 'SELL'], case_sensitive=False))
@click.argument('quantity', type=float)
@click.argument('stop_price', type=float)
@click.option('--reduce-only', is_flag=True, help='Reduce only flag')
def stop_market(symbol, side, quantity, stop_price, reduce_only):
    """Place a stop market order"""
    try:
        bot = get_bot()
        
        # Confirm order
        click.echo(Fore.YELLOW + "\n=== Order Confirmation ===" + Style.RESET_ALL)
        click.echo(f"Type: STOP MARKET")
        click.echo(f"Symbol: {symbol.upper()}")
        click.echo(f"Side: {side.upper()}")
        click.echo(f"Quantity: {quantity}")
        click.echo(f"Stop Price: ${stop_price}")
        click.echo(f"Reduce Only: {reduce_only}")
        
        if not click.confirm('\nDo you want to place this order?'):
            click.echo(Fore.YELLOW + "Order cancelled" + Style.RESET_ALL)
            return
        
        order = bot.place_stop_market_order(symbol, side, quantity, stop_price, reduce_only)
        
        click.echo(Fore.GREEN + f"\n✓ Stop market order placed successfully!" + Style.RESET_ALL)
        click.echo(f"Order ID: {order['orderId']}")
        click.echo(f"Status: {order['status']}")
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.argument('symbol')
@click.argument('side', type=click.Choice(['BUY', 'SELL'], case_sensitive=False))
@click.argument('quantity', type=float)
@click.argument('price', type=float)
@click.argument('stop_price', type=float)
@click.option('--tif', default='GTC', type=click.Choice(['GTC', 'IOC', 'FOK']), 
              help='Time in force')
@click.option('--reduce-only', is_flag=True, help='Reduce only flag')
def stop_limit(symbol, side, quantity, price, stop_price, tif, reduce_only):
    """Place a stop limit order"""
    try:
        bot = get_bot()
        
        # Confirm order
        click.echo(Fore.YELLOW + "\n=== Order Confirmation ===" + Style.RESET_ALL)
        click.echo(f"Type: STOP LIMIT")
        click.echo(f"Symbol: {symbol.upper()}")
        click.echo(f"Side: {side.upper()}")
        click.echo(f"Quantity: {quantity}")
        click.echo(f"Price: ${price}")
        click.echo(f"Stop Price: ${stop_price}")
        click.echo(f"Time in Force: {tif}")
        click.echo(f"Reduce Only: {reduce_only}")
        
        if not click.confirm('\nDo you want to place this order?'):
            click.echo(Fore.YELLOW + "Order cancelled" + Style.RESET_ALL)
            return
        
        order = bot.place_stop_limit_order(
            symbol, side, quantity, price, stop_price, tif, reduce_only
        )
        
        click.echo(Fore.GREEN + f"\n✓ Stop limit order placed successfully!" + Style.RESET_ALL)
        click.echo(f"Order ID: {order['orderId']}")
        click.echo(f"Status: {order['status']}")
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.option('--symbol', '-s', help='Trading symbol (optional)')
def orders(symbol):
    """Get open orders"""
    try:
        bot = get_bot()
        orders_list = bot.get_open_orders(symbol)
        
        if not orders_list:
            click.echo(Fore.YELLOW + "\nNo open orders" + Style.RESET_ALL)
            return
        
        data = []
        for order in orders_list:
            data.append([
                order['orderId'],
                order['symbol'],
                order['type'],
                order['side'],
                order['price'],
                order['origQty'],
                order['status'],
            ])
        
        headers = ['Order ID', 'Symbol', 'Type', 'Side', 'Price', 'Quantity', 'Status']
        
        click.echo(Fore.CYAN + "\n=== Open Orders ===" + Style.RESET_ALL)
        click.echo(tabulate(data, headers=headers, tablefmt='grid'))
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.argument('symbol')
@click.argument('order_id', type=int)
def cancel(symbol, order_id):
    """Cancel an order"""
    try:
        bot = get_bot()
        
        if click.confirm(f'\nCancel order {order_id} for {symbol}?'):
            response = bot.cancel_order(symbol, order_id)
            click.echo(Fore.GREEN + f"\n✓ Order cancelled successfully!" + Style.RESET_ALL)
        else:
            click.echo(Fore.YELLOW + "Cancellation aborted" + Style.RESET_ALL)
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


@cli.command()
@click.argument('symbol')
def close(symbol):
    """Close position for a symbol"""
    try:
        bot = get_bot()
        
        if click.confirm(f'\nClose position for {symbol}?'):
            response = bot.close_position(symbol)
            
            if response.get('status') == 'NO_POSITION':
                click.echo(Fore.YELLOW + f"\nNo open position for {symbol}" + Style.RESET_ALL)
            else:
                click.echo(Fore.GREEN + f"\n✓ Position closed successfully!" + Style.RESET_ALL)
        else:
            click.echo(Fore.YELLOW + "Close position aborted" + Style.RESET_ALL)
        
    except Exception as e:
        click.echo(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


if __name__ == '__main__':
    cli()