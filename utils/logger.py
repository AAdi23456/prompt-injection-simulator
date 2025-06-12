"""
Logging module for Prompt Defense Simulator.

This module provides functions for setting up and configuring logging.
"""

import os
import logging
import colorlog
from datetime import datetime

def setup_logger(log_level=logging.INFO):
    """
    Set up and configure the logger
    
    Args:
        log_level: The logging level (default: INFO)
        
    Returns:
        Logger: The configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Get current timestamp for log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/simulator_{timestamp}.log'
    
    # Create formatter
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console formatter with colors
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Create logger
    logger = logging.getLogger('prompt_defense')
    logger.setLevel(log_level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger 