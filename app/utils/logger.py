"""
Logging configuration for the dropshipping application.
Separates technical logs from user-facing output.
"""
import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Technical logger - writes to file for debugging and technical details
def get_technical_logger(name):
    """
    Get a logger for technical details that should not clutter user output.
    Logs to file only.
    """
    logger = logging.getLogger(f"technical.{name}")
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        # File handler for technical logs
        file_handler = logging.FileHandler(LOG_DIR / 'app.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger

# User-facing logger - minimal output to console
def get_user_logger(name):
    """
    Get a logger for user-facing messages.
    Shows minimal, clean output to console.
    """
    logger = logging.getLogger(f"user.{name}")
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Console handler for user messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger

# Configure root logger to write to file by default
def configure_root_logger():
    """Configure the root logger to write to file."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # File handler for root logger
    file_handler = logging.FileHandler(LOG_DIR / 'app.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

# Initialize on import
configure_root_logger()
