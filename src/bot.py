"""
Main trading bot implementation
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from typing import Optional, Dict, Any, List
import time

from .logger import setup_logger, log_order, log_api_request, log_api_response
from .validators import InputValidator, ValidationError
from .orders import OrderManager


class BinanceFuturesBot:
    """
    Binance Futures Trading Bot
    
    Supports multiple order types on Binance Futures Testnet
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize the trading bot
        
        Args:
            api_key (str): Binance API key
            api_secret (str): Binance API secret
            testnet (bool): Use testnet if True
        """
        self.logger = setup_logger()
        self.validator = InputValidator()
        self.order_manager = OrderManager()
        
        try:
            # Initialize Binance client
            self.client = Client(api_key, api_secret, testnet=testnet)
            
            if testnet:
                # Set testnet URL for futures
                self.client.API_URL = 'https://testnet.binancefuture.com'
                self.logger.info("Connected to Binance Futures TESTNET")
            else:
                self.logger.warning("Connected to Binance Futures MAINNET")
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {e}")
            raise
    
    def _test_connection(self):
        """Test API connection and log account info"""
        try:
            # Test connectivity
            self.client.futures_ping()
            self.logger.info("✓ API connection successful")
            
            # Get account info
            account = self.client.futures_account()
            balance = account.get('totalWalletBalance', 'N/A')
            self.logger.info(f"✓ Account Balance: {balance} USDT")
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            raise
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance information
        
        Returns:
            dict: Account balance details
        """
        try:
            log_api_request(self.logger, 'GET', '/fapi/v2/account')
            account = self.client.futures_account()
            log_api_response(self.logger, account)
            
            return {
                'totalWalletBalance': account.get('totalWalletBalance'),
                'availableBalance': account.get('availableBalance'),
                'totalUnrealizedProfit': account.get('totalUnrealizedProfit'),
            }
        except BinanceAPIException as e:
            self.logger.error(f"API Error getting balance: {e}")
            log_api_response(self.logger, str(e), is_error=True)
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            float: Current price
        """
        try:
            symbol = self.validator.validate_symbol(symbol)
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            self.logger.info(f"Current price for {symbol}: {price}")
            return price
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            raise
    
    def get_position_info(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current position information
        
        Args:
            symbol (str, optional): Trading symbol
            
        Returns:
            list: Position information
        """
        try:
            if symbol:
                symbol = self.validator.validate_symbol(symbol)
                positions = self.client.futures_position_information(symbol=symbol)
            else:
                positions = self.client.futures_position_information()
            
            # Filter out positions with zero amount
            active_positions = [p for p in positions if float(p['positionAmt']) != 0]
            
            return active_positions
        except Exception as e:
            self.logger.error(f"Error getting position info: {e}")
            raise
    
    def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """
        Set leverage for a symbol
        
        Args:
            symbol (str): Trading symbol
            leverage (int): Leverage value (1-125)
            
        Returns:
            dict: Response from API
        """
        try:
            symbol = self.validator.validate_symbol(symbol)
            leverage = self.validator.validate_leverage(leverage)
            
            response = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            
            self.logger.info(f"Leverage set to {leverage}x for {symbol}")
            return response
        except Exception as e:
            self.logger.error(f"Error setting leverage: {e}")
            raise
    
    def place_market_order(self, symbol: str, side: str, quantity: float,
                          reduce_only: bool = False) -> Dict[str, Any]:
        """
        Place a market order
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            reduce_only (bool): Reduce only flag
            
        Returns:
            dict: Order response
        """
        try:
            # Validate inputs
            symbol = self.validator.validate_symbol(symbol)
            side = self.validator.validate_side(side)
            quantity = self.validator.validate_quantity(quantity)
            
            # Create order parameters
            params = self.order_manager.create_market_order(
                symbol, side, quantity, reduce_only
            )
            
            # Log request
            log_api_request(self.logger, 'POST', '/fapi/v1/order', params)
            
            # Place order
            order = self.client.futures_create_order(**params)
            
            # Log response
            log_api_response(self.logger, order)
            formatted_order = self.order_manager.format_order_response(order)
            log_order(self.logger, formatted_order)
            
            return order
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            raise
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error: {e}")
            log_api_response(self.logger, str(e), is_error=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing market order: {e}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float,
                         price: float, time_in_force: str = 'GTC',
                         reduce_only: bool = False) -> Dict[str, Any]:
        """
        Place a limit order
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            price (float): Limit price
            time_in_force (str): Time in force (GTC/IOC/FOK)
            reduce_only (bool): Reduce only flag
            
        Returns:
            dict: Order response
        """
        try:
            # Validate inputs
            symbol = self.validator.validate_symbol(symbol)
            side = self.validator.validate_side(side)
            quantity = self.validator.validate_quantity(quantity)
            price = self.validator.validate_price(price)
            time_in_force = self.validator.validate_time_in_force(time_in_force)
            
            # Create order parameters
            params = self.order_manager.create_limit_order(
                symbol, side, quantity, price, time_in_force, reduce_only
            )
            
            # Log request
            log_api_request(self.logger, 'POST', '/fapi/v1/order', params)
            
            # Place order
            order = self.client.futures_create_order(**params)
            
            # Log response
            log_api_response(self.logger, order)
            formatted_order = self.order_manager.format_order_response(order)
            log_order(self.logger, formatted_order)
            
            return order
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            raise
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error: {e}")
            log_api_response(self.logger, str(e), is_error=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing limit order: {e}")
            raise
    
    def place_stop_market_order(self, symbol: str, side: str, quantity: float,
                               stop_price: float, 
                               reduce_only: bool = False) -> Dict[str, Any]:
        """
        Place a stop market order
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            stop_price (float): Stop trigger price
            reduce_only (bool): Reduce only flag
            
        Returns:
            dict: Order response
        """
        try:
            # Validate inputs
            symbol = self.validator.validate_symbol(symbol)
            side = self.validator.validate_side(side)
            quantity = self.validator.validate_quantity(quantity)
            stop_price = self.validator.validate_price(stop_price)
            
            # Create order parameters
            params = self.order_manager.create_stop_market_order(
                symbol, side, quantity, stop_price, reduce_only
            )
            
            # Log request
            log_api_request(self.logger, 'POST', '/fapi/v1/order', params)
            
            # Place order
            order = self.client.futures_create_order(**params)
            
            # Log response
            log_api_response(self.logger, order)
            formatted_order = self.order_manager.format_order_response(order)
            log_order(self.logger, formatted_order)
            
            return order
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            raise
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error: {e}")
            log_api_response(self.logger, str(e), is_error=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing stop market order: {e}")
            raise
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float,
                              price: float, stop_price: float,
                              time_in_force: str = 'GTC',
                              reduce_only: bool = False) -> Dict[str, Any]:
        """
        Place a stop limit order
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            price (float): Limit price
            stop_price (float): Stop trigger price
            time_in_force (str): Time in force (GTC/IOC/FOK)
            reduce_only (bool): Reduce only flag
            
        Returns:
            dict: Order response
        """
        try:
            # Validate inputs
            symbol = self.validator.validate_symbol(symbol)
            side = self.validator.validate_side(side)
            quantity = self.validator.validate_quantity(quantity)
            price = self.validator.validate_price(price)
            stop_price = self.validator.validate_price(stop_price)
            time_in_force = self.validator.validate_time_in_force(time_in_force)
            
            # Create order parameters
            params = self.order_manager.create_stop_limit_order(
                symbol, side, quantity, price, stop_price, time_in_force, reduce_only
            )
            
            # Log request
            log_api_request(self.logger, 'POST', '/fapi/v1/order', params)
            
            # Place order
            order = self.client.futures_create_order(**params)
            
            # Log response
            log_api_response(self.logger, order)
            formatted_order = self.order_manager.format_order_response(order)
            log_order(self.logger, formatted_order)
            
            return order
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            raise
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error: {e}")
            log_api_response(self.logger, str(e), is_error=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing stop limit order: {e}")
            raise
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        Args:
            symbol (str): Trading symbol
            order_id (int): Order ID to cancel
            
        Returns:
            dict: Cancellation response
        """
        try:
            symbol = self.validator.validate_symbol(symbol)
            
            response = self.client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            
            self.logger.info(f"Order {order_id} cancelled successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open orders
        
        Args:
            symbol (str, optional): Trading symbol
            
        Returns:
            list: Open orders
        """
        try:
            if symbol:
                symbol = self.validator.validate_symbol(symbol)
                orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                orders = self.client.futures_get_open_orders()
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            raise
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Close an open position
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            dict: Order response
        """
        try:
            symbol = self.validator.validate_symbol(symbol)
            
            # Get current position
            positions = self.get_position_info(symbol)
            
            if not positions:
                self.logger.warning(f"No open position for {symbol}")
                return {'status': 'NO_POSITION'}
            
            position = positions[0]
            position_amt = float(position['positionAmt'])
            
            if position_amt == 0:
                self.logger.warning(f"No open position for {symbol}")
                return {'status': 'NO_POSITION'}
            
            # Determine side (opposite of position)
            side = 'SELL' if position_amt > 0 else 'BUY'
            quantity = abs(position_amt)
            
            # Place market order to close
            order = self.place_market_order(symbol, side, quantity, reduce_only=True)
            
            self.logger.info(f"Position closed for {symbol}")
            return order
            
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            raise