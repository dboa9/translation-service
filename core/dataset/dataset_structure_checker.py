# File: dataset_structure_checker.py
"""
Dataset Structure Checker
Author: dboa9
Date: 10_11_24_23_59
"""

import logging
from pathlib import Path
from typing import Dict, Any, Union

import yaml

logger = logging.getLogger(__name__)

def check_column_mapping_structure(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Verify the structure of the column_mapping.yaml file.
    
    Args:
        file_path (Union[str, Path]): Path to the column_mapping.yaml file.
    
    Returns:
        Dict[str, Any]: A dictionary containing the validation results.
    """
    result = {
        "exists": False,
        "valid_structure": False,
        "datasets": [],
        "errors": []
    }
    
    try:
        path = Path(file_path)
        if not path.exists():
            result["errors"].append(f"File not found: {path}")
            return result
        
        result["exists"] = True
        
        with path.open('r') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            result["errors"].append("Root element is not a dictionary")
            return result

        if "datasets" not in data:
            result["errors"].append("Missing 'datasets' section")
            return result

        if "language_codes" not in data:
            result["errors"].append("Missing 'language_codes' section")
            return result

        language_codes = data["language_codes"]
        if not isinstance(language_codes, list):
            result["errors"].append("'language_codes' is not a list")
            return result

        for dataset_name, dataset_info in data["datasets"].items():
            if not isinstance(dataset_info, dict):
                result["errors"].append(f"Dataset '{dataset_name}' is not a dictionary")
                continue
            
            if "subsets" not in dataset_info or "required_columns" not in dataset_info:
                result["errors"].append(f"Dataset '{dataset_name}' is missing 'subsets' or 'required_columns'")
                continue

            for subset_name, columns in dataset_info["required_columns"].items():
                if not isinstance(columns, list):
                    result["errors"].append(f"Required columns for dataset '{dataset_name}', subset '{subset_name}' is not a list")
                    continue
                for col in columns:
                    if col in language_codes:
                        continue
                    # Check if the column name (potentially a language code) is in the valid language codes
                    is_language_code = any(code == col for code in language_codes)
                    if not is_language_code:
                        result["errors"].append(f"Invalid language code '{col}' found in dataset '{dataset_name}', subset '{subset_name}'")
            
            result["datasets"].append(dataset_name)
        
        result["valid_structure"] = len(result["errors"]) == 0
    
    except Exception as e:
        result["errors"].append(f"Error checking file structure: {str(e)}")
    
    return result

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config_path = Path("config/column_mapping.yaml")
    check_result = check_column_mapping_structure(config_path)
    
    if check_result["exists"]:
        logger.info(f"Column mapping file found: {config_path}")
        if check_result["valid_structure"]:
            logger.info("Column mapping structure is valid")
            logger.info(f"Datasets found: {', '.join(check_result['datasets'])}")
        else:
            logger.error("Column mapping structure is invalid")
            for error in check_result["errors"]:
                logger.error(f"- {error}")
    else:
        logger.error(f"Column mapping file not found: {config_path}")
