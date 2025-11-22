"""
Logging configuration for the trading bot
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name='TradingBot', log_dir='logs', log_level='INFO'):
    """
    Set up logger with both file and console handlers
    
    Args:
        name (str): Logger name
        log_dir (str): Directory for log files
        log_level (str): Logging level
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with rotation
    log_file = os.path.join(
        log_dir, 
        f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_order(logger, order_data):
    """
    Log order details in a structured format
    
    Args:
        logger: Logger instance
        order_data (dict): Order information
    """
    logger.info("=" * 60)
    logger.info("ORDER DETAILS")
    logger.info("=" * 60)
    for key, value in order_data.items():
        logger.info(f"{key:20s}: {value}")
    logger.info("=" * 60)


def log_api_request(logger, method, endpoint, params=None):
    """
    Log API request details
    
    Args:
        logger: Logger instance
        method (str): HTTP method
        endpoint (str): API endpoint
        params (dict): Request parameters
    """
    logger.debug(f"API Request - Method: {method}, Endpoint: {endpoint}")
    if params:
        logger.debug(f"Parameters: {params}")


def log_api_response(logger, response, is_error=False):
    """
    Log API response
    
    Args:
        logger: Logger instance
        response: Response data
        is_error (bool): Whether this is an error response
    """
    if is_error:
        logger.error(f"API Error Response: {response}")
    else:
        logger.debug(f"API Response: {response}")