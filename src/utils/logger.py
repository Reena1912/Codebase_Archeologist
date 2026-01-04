"""
Logger Module
Configures logging with colors and file output
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Try to import colorlog for colored output
try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

# Global logger instance
logger = logging.getLogger('codebase_archaeologist')

def setup_logger(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Configure and setup the logger
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        log_format: Optional custom log format
        
    Returns:
        Configured logger instance
    """
    global logger
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Default format
    if log_format is None:
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        color_format = '%(log_color)s%(asctime)s - %(levelname)s - %(message)s%(reset)s'
    else:
        color_format = f'%(log_color)s{log_format}%(reset)s'
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if HAS_COLORLOG:
        console_formatter = colorlog.ColoredFormatter(
            color_format,
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    else:
        console_formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file: {e}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Optional logger name (creates child logger)
        
    Returns:
        Logger instance
    """
    if name:
        return logger.getChild(name)
    return logger

class LogContext:
    """Context manager for temporary log level changes"""
    
    def __init__(self, level: str):
        self.new_level = getattr(logging, level.upper(), logging.INFO)
        self.old_level = None
    
    def __enter__(self):
        self.old_level = logger.level
        logger.setLevel(self.new_level)
        return logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.setLevel(self.old_level)
        return False

# Initialize with default settings
setup_logger()

# Example usage
if __name__ == "__main__":
    # Test logging
    setup_logger(level='DEBUG', log_file='test.log')
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test context manager
    with LogContext('ERROR'):
        logger.info("This won't show")
        logger.error("This will show")
    
    logger.info("Back to normal level")
