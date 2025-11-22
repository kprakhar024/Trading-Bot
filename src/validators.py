"""
Input validation for trading bot
"""

import re
from typing import Union, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Validator for trading bot inputs"""
    
    VALID_ORDER_TYPES = ['MARKET', 'LIMIT', 'STOP_MARKET', 'STOP_LIMIT', 'TAKE_PROFIT_MARKET']
    VALID_SIDES = ['BUY', 'SELL']
    VALID_TIME_IN_FORCE = ['GTC', 'IOC', 'FOK']
    
    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """
        Validate trading symbol
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            str: Validated symbol in uppercase
            
        Raises:
            ValidationError: If symbol is invalid
        """
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("Symbol must be a non-empty string")
        
        # Remove whitespace and convert to uppercase
        symbol = symbol.strip().upper()
        
        # Basic pattern check (alphanumeric)
        if not re.match(r'^[A-Z0-9]+$', symbol):
            raise ValidationError(f"Invalid symbol format: {symbol}")
        
        # Must end with USDT for futures
        if not symbol.endswith('USDT'):
            symbol += 'USDT'
        
        return symbol
    
    @staticmethod
    def validate_quantity(quantity: Union[str, float], min_qty: float = 0.001, 
                         max_qty: float = 1000.0) -> float:
        """
        Validate order quantity
        
        Args:
            quantity: Order quantity
            min_qty (float): Minimum allowed quantity
            max_qty (float): Maximum allowed quantity
            
        Returns:
            float: Validated quantity
            
        Raises:
            ValidationError: If quantity is invalid
        """
        try:
            qty = float(quantity)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid quantity: {quantity}")
        
        if qty <= 0:
            raise ValidationError(f"Quantity must be positive: {qty}")
        
        if qty < min_qty:
            raise ValidationError(f"Quantity below minimum ({min_qty}): {qty}")
        
        if qty > max_qty:
            raise ValidationError(f"Quantity above maximum ({max_qty}): {qty}")
        
        return qty
    
    @staticmethod
    def validate_price(price: Union[str, float]) -> float:
        """
        Validate price
        
        Args:
            price: Price value
            
        Returns:
            float: Validated price
            
        Raises:
            ValidationError: If price is invalid
        """
        try:
            price_val = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid price: {price}")
        
        if price_val <= 0:
            raise ValidationError(f"Price must be positive: {price_val}")
        
        return price_val
    
    @staticmethod
    def validate_order_type(order_type: str) -> str:
        """
        Validate order type
        
        Args:
            order_type (str): Order type
            
        Returns:
            str: Validated order type
            
        Raises:
            ValidationError: If order type is invalid
        """
        order_type = order_type.strip().upper()
        
        if order_type not in InputValidator.VALID_ORDER_TYPES:
            raise ValidationError(
                f"Invalid order type: {order_type}. "
                f"Must be one of {InputValidator.VALID_ORDER_TYPES}"
            )
        
        return order_type
    
    @staticmethod
    def validate_side(side: str) -> str:
        """
        Validate order side
        
        Args:
            side (str): Order side (BUY/SELL)
            
        Returns:
            str: Validated side
            
        Raises:
            ValidationError: If side is invalid
        """
        side = side.strip().upper()
        
        if side not in InputValidator.VALID_SIDES:
            raise ValidationError(
                f"Invalid order side: {side}. "
                f"Must be one of {InputValidator.VALID_SIDES}"
            )
        
        return side
    
    @staticmethod
    def validate_time_in_force(tif: str) -> str:
        """
        Validate time in force
        
        Args:
            tif (str): Time in force
            
        Returns:
            str: Validated time in force
            
        Raises:
            ValidationError: If time in force is invalid
        """
        tif = tif.strip().upper()
        
        if tif not in InputValidator.VALID_TIME_IN_FORCE:
            raise ValidationError(
                f"Invalid time in force: {tif}. "
                f"Must be one of {InputValidator.VALID_TIME_IN_FORCE}"
            )
        
        return tif
    
    @staticmethod
    def validate_leverage(leverage: Union[str, int]) -> int:
        """
        Validate leverage
        
        Args:
            leverage: Leverage value
            
        Returns:
            int: Validated leverage
            
        Raises:
            ValidationError: If leverage is invalid
        """
        try:
            lev = int(leverage)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid leverage: {leverage}")
        
        if lev < 1 or lev > 125:
            raise ValidationError(f"Leverage must be between 1 and 125: {lev}")
        
        return lev