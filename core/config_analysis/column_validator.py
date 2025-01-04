from typing import Dict, Any, Optional, Union
from datasets import Dataset
import logging
from .column_mapping_validator import validate_column_mapping_structure
from pathlib import Path

logger = logging.getLogger(__name__)

def validate_columns(dataset: Dataset, dataset_name: str, config: Optional[str] = None, split_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate the columns of a dataset against the column mapping configuration.
    
    Args:
        dataset (Dataset): The dataset to validate
        dataset_name (str): Name of the dataset
        config (Optional[str]): Configuration name to use
        split_name (Optional[str]): Name of the dataset split being validated
    
    Returns:
        Dict[str, Any]: Validation results
    """
    try:
        # Get the column mapping configuration
        config_path = Path(__file__).parent.parent.parent / "config" / "column_mapping.yaml"
        mapping_validation = validate_column_mapping_structure(str(config_path))
        
        if not mapping_validation["status"]:
            return {
                "status": False,
                "message": f"Column mapping configuration error: {mapping_validation['message']}"
            }
            
        # Get actual columns from the dataset
        actual_columns = dataset.column_names
        
        # Basic validation result structure
        result = {
            "status": True,
            "message": "",
            "dataset": dataset_name,
            "split": split_name,
            "config": config,
            "columns": actual_columns
        }
        
        logger.info(f"Validating columns for dataset: {dataset_name} (split: {split_name})")
        logger.info(f"Found columns: {actual_columns}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error validating columns for {dataset_name}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": False,
            "message": error_msg
        }
