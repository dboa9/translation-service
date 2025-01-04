# File: tests/core/utils.py

import logging
import sys
from pathlib import Path

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('translation_service.log')
        ]
    )
    return logging.getLogger('tests.core.utils')

def log_debug(message):
    """Log debug message."""
    logger = logging.getLogger('tests.core.utils')
    logger.debug(message)

def log_info(message):
    """Log info message."""
    logger = logging.getLogger('tests.core.utils')
    logger.info(message)

def log_warning(message):
    """Log warning message."""
    logger = logging.getLogger('tests.core.utils')
    logger.warning(message)

def log_error(message):
    """Log error message."""
    logger = logging.getLogger('tests.core.utils')
    logger.error(message)