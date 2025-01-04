# File: dataset_error_handler.py
"""
Dataset Error Handler
Author: dboa9
Date: 11_11_24_00_15
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class DatasetError(Exception):
    """Base class for dataset-related errors."""
    pass

class DatasetLoadError(DatasetError):
    """Error raised when loading a dataset fails."""
    pass

class ColumnMappingError(DatasetError):
    """Error raised when applying column mapping fails."""
    pass

def log_and_raise(error_type: type, message: str, **kwargs):
    """
    Log an error message and raise the corresponding exception.
    
    Args:
        error_type (type): The type of exception to raise.
        message (str): The error message.
        **kwargs: Additional keyword arguments to include in the log.
    
    Raises:
        The specified error_type with the given message.
    """
    logger.error(message, extra=kwargs)
    raise error_type(message)

def handle_dataset_errors(func):
    """
    Decorator to handle dataset-related errors.
    
    Args:
        func: The function to wrap.
    
    Returns:
        A wrapper function that catches and handles dataset-related errors.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatasetLoadError as e:
            logger.error(f"Failed to load dataset: {str(e)}")
        except ColumnMappingError as e:
            logger.error(f"Failed to apply column mapping: {str(e)}")
        except DatasetError as e:
            logger.error(f"Dataset error occurred: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {str(e)}")
    return wrapper

def log_dataset_info(dataset_name: str, subset: str, info: Dict[str, Any]):
    """
    Log information about a dataset.
    
    Args:
        dataset_name (str): Name of the dataset.
        subset (str): Subset of the dataset.
        info (Dict[str, Any]): Information about the dataset.
    """
    logger.info(f"Dataset: {dataset_name}/{subset}")
    for key, value in info.items():
        logger.info(f"  {key}: {value}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    @handle_dataset_errors
    def example_dataset_operation(dataset_name: str, subset: str):
        # Simulating a dataset operation that might raise an error
        if dataset_name == "invalid_dataset":
            log_and_raise(DatasetLoadError, f"Failed to load dataset: {dataset_name}/{subset}")
        
        # Simulating successful dataset operation
        dataset_info = {
            "num_samples": 1000,
            "features": ["text", "label"],
            "language": "en"
        }
        log_dataset_info(dataset_name, subset, dataset_info)
    
    # Test with a valid dataset
    example_dataset_operation("valid_dataset", "train")
    
    # Test with an invalid dataset
    example_dataset_operation("invalid_dataset", "test")
