from typing import Dict, Any, Optional, List, Set
from datasets import Dataset
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

def validate_columns(
    dataset: Dataset,
    dataset_name: str,
    config: Optional[str] = None,
    split_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extended validation of dataset columns against configuration.
    
    Args:
        dataset (Dataset): The dataset to validate
        dataset_name (str): Name of the dataset
        config (Optional[str]): Configuration name to use
        split_name (Optional[str]): Name of the dataset split being validated
        
    Returns:
        Dict[str, Any]: Validation results including detailed column analysis
    """
    try:
        # Load column mapping configuration
        config_path = Path(__file__).parent.parent.parent / "config" / "column_mapping.yaml"
        with open(config_path) as f:
            mapping_config = yaml.safe_load(f)
        
        # Get actual columns from dataset
        actual_columns = set(dataset.column_names)
        
        # Get expected columns from config
        dataset_config = mapping_config.get("datasets", {}).get(dataset_name, {})
        if not dataset_config:
            return {
                "status": False,
                "message": f"No configuration found for dataset: {dataset_name}",
                "dataset": dataset_name,
                "split": split_name,
                "config": config
            }
            
        required_columns = set()
        if "required_columns" in dataset_config:
            subset = split_name or "default"
            if subset in dataset_config["required_columns"]:
                required_columns = set(dataset_config["required_columns"][subset])
        
        # Validate columns
        missing_columns = required_columns - actual_columns
        extra_columns = actual_columns - required_columns
        
        result = {
            "status": len(missing_columns) == 0,
            "message": "",
            "dataset": dataset_name,
            "split": split_name,
            "config": config,
            "actual_columns": list(actual_columns),
            "required_columns": list(required_columns),
            "missing_columns": list(missing_columns),
            "extra_columns": list(extra_columns)
        }
        
        if missing_columns:
            result["message"] = f"Missing required columns: {', '.join(missing_columns)}"
        elif extra_columns:
            result["message"] = f"Found extra columns: {', '.join(extra_columns)}"
        else:
            result["message"] = "All required columns present"
            
        logger.info(f"Validated columns for {dataset_name} (split: {split_name})")
        return result
        
    except Exception as e:
        error_msg = f"Error validating columns for {dataset_name}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": False,
            "message": error_msg,
            "dataset": dataset_name,
            "split": split_name,
            "config": config
        }
