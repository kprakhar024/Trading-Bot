"""
Order management for trading bot
"""

from typing import Optional, Dict, Any
from enum import Enum


class OrderType(Enum):
    """Order types enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"


class OrderSide(Enum):
    """Order sides enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class TimeInForce(Enum):
    """Time in force enumeration"""
    GTC = "GTC"  # Good Till Cancel
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill


class OrderBuilder:
    """Builder pattern for creating order parameters"""
    
    def __init__(self, symbol: str, side: str, order_type: str):
        self.params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
        }
    
    def quantity(self, qty: float) -> 'OrderBuilder':
        """Set order quantity"""
        self.params['quantity'] = qty
        return self
    
    def price(self, price: float) -> 'OrderBuilder':
        """Set limit price"""
        self.params['price'] = price
        return self
    
    def stop_price(self, stop_price: float) -> 'OrderBuilder':
        """Set stop price"""
        self.params['stopPrice'] = stop_price
        return self
    
    def time_in_force(self, tif: str) -> 'OrderBuilder':
        """Set time in force"""
        self.params['timeInForce'] = tif
        return self
    
    def reduce_only(self, reduce: bool = True) -> 'OrderBuilder':
        """Set reduce only flag"""
        self.params['reduceOnly'] = reduce
        return self
    
    def close_position(self, close: bool = True) -> 'OrderBuilder':
        """Set close position flag"""
        self.params['closePosition'] = close
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return order parameters"""
        return self.params


class OrderManager:
    """Manages order creation and execution"""
    
    @staticmethod
    def create_market_order(symbol: str, side: str, quantity: float, 
                          reduce_only: bool = False) -> Dict[str, Any]:
        """
        Create market order parameters
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            reduce_only (bool): Reduce only flag
            
        Returns:
            dict: Order parameters
        """
        builder = OrderBuilder(symbol, side, OrderType.MARKET.value)
        builder.quantity(quantity)
        
        if reduce_only:
            builder.reduce_only(True)
        
        return builder.build()
    
    @staticmethod
    def create_limit_order(symbol: str, side: str, quantity: float, 
                          price: float, time_in_force: str = 'GTC',
                          reduce_only: bool = False) -> Dict[str, Any]:
        """
        Create limit order parameters
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            price (float): Limit price
            time_in_force (str): Time in force
            reduce_only (bool): Reduce only flag
            
        Returns:
            dict: Order parameters
        """
        builder = OrderBuilder(symbol, side, OrderType.LIMIT.value)
        builder.quantity(quantity).price(price).time_in_force(time_in_force)
        
        if reduce_only:
            builder.reduce_only(True)
        
        return builder.build()
    
    @staticmethod
    def create_stop_market_order(symbol: str, side: str, quantity: float,
                                stop_price: float, 
                                reduce_only: bool = False) -> Dict[str, Any]:
        """
        Create stop market order parameters
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            stop_price (float): Stop trigger price
            reduce_only (bool): Reduce only flag
            
        Returns:
            dict: Order parameters
        """
        builder = OrderBuilder(symbol, side, OrderType.STOP_MARKET.value)
        builder.quantity(quantity).stop_price(stop_price)
        
        if reduce_only:
            builder.reduce_only(True)
        
        return builder.build()
    
    @staticmethod
    def create_stop_limit_order(symbol: str, side: str, quantity: float,
                               price: float, stop_price: float,
                               time_in_force: str = 'GTC',
                               reduce_only: bool = False) -> Dict[str, Any]:
        """
        Create stop limit order parameters
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side (BUY/SELL)
            quantity (float): Order quantity
            price (float): Limit price
            stop_price (float): Stop trigger price
            time_in_force (str): Time in force
            reduce_only (bool): Reduce only flag
            
        Returns:
            dict: Order parameters
        """
        builder = OrderBuilder(symbol, side, OrderType.STOP_LIMIT.value)
        builder.quantity(quantity).price(price).stop_price(stop_price)
        builder.time_in_force(time_in_force)
        
        if reduce_only:
            builder.reduce_only(True)
        
        return builder.build()
    
    @staticmethod
    def format_order_response(order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format order response for display
        
        Args:
            order (dict): Raw order response
            
        Returns:
            dict: Formatted order information
        """
        return {
            'Order ID': order.get('orderId', 'N/A'),
            'Client Order ID': order.get('clientOrderId', 'N/A'),
            'Symbol': order.get('symbol', 'N/A'),
            'Side': order.get('side', 'N/A'),
            'Type': order.get('type', 'N/A'),
            'Status': order.get('status', 'N/A'),
            'Quantity': order.get('origQty', 'N/A'),
            'Price': order.get('price', 'N/A'),
            'Stop Price': order.get('stopPrice', 'N/A'),
            'Executed Qty': order.get('executedQty', 'N/A'),
            'Avg Price': order.get('avgPrice', 'N/A'),
            'Time': order.get('updateTime', 'N/A'),
        }