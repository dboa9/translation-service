# File: dataset_integration_checker.py
"""
Dataset Integration Checker
Author: dboa9
Date: 11_11_24_00_05
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

import yaml
from datasets import load_dataset

logger = logging.getLogger(__name__)

def check_column_mapping_structure(file_path: Path) -> Dict[str, Any]:
    """
    Verify the structure of the column_mapping.yaml file.
    
    Args:
        file_path (Path): Path to the column_mapping.yaml file.
    
    Returns:
        Dict[str, Any]: A dictionary containing the validation results.
    """
    result = {
        "exists": False,
        "valid_structure": False,
        "datasets": [],
        "column_mappings": {},
        "errors": []
    }
    
    try:
        if not file_path.exists():
            result["errors"].append(f"File not found: {file_path}")
            return result
        
        result["exists"] = True
        
        with file_path.open('r') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            result["errors"].append("Root element is not a dictionary")
            return result
        
        for dataset_name, dataset_info in data.items():
            if not isinstance(dataset_info, dict):
                result["errors"].append(f"Dataset '{dataset_name}' is not a dictionary")
                continue
            
            if "subsets" not in dataset_info or "column_mappings" not in dataset_info:
                result["errors"].append(f"Dataset '{dataset_name}' is missing 'subsets' or 'column_mappings'")
                continue
            
            result["datasets"].append(dataset_name)
            result["column_mappings"][dataset_name] = dataset_info["column_mappings"]
        
        result["valid_structure"] = len(result["errors"]) == 0
    
    except Exception as e:
        result["errors"].append(f"Error checking file structure: {str(e)}")
    
    return result

def check_dataset_integration(dataset_name: str, subset: str, column_mapping_path: Path) -> Dict[str, Any]:
    """
    Check the integration of a dataset by attempting to load it and apply column mappings.
    
    Args:
        dataset_name (str): Name of the dataset to check.
        subset (str): Subset of the dataset to check.
        column_mapping_path (Path): Path to the column mapping YAML file.
    
    Returns:
        Dict[str, Any]: A dictionary containing the integration check results.
    """
    result = {
        "dataset_loaded": False,
        "mapping_applied": False,
        "errors": []
    }

    try:
        logger.info(f"Checking integration for dataset: {dataset_name}, subset: {subset}")
        
        # Check column mapping structure
        logger.info(f"Checking column mapping structure: {column_mapping_path}")
        structure_check = check_column_mapping_structure(column_mapping_path)
        if not structure_check["valid_structure"]:
            logger.error(f"Invalid column mapping structure: {structure_check['errors']}")
            result["errors"].extend(structure_check["errors"])
            return result

        # Attempt to load the dataset
        try:
            logger.info(f"Attempting to load dataset: {dataset_name}/{subset}")
            dataset = load_dataset(dataset_name, subset)
            result["dataset_loaded"] = True
            logger.info(f"Successfully loaded dataset: {dataset_name}/{subset}")
        except Exception as e:
            logger.error(f"Failed to load dataset {dataset_name}/{subset}: {str(e)}")
            result["errors"].append(f"Failed to load dataset {dataset_name}/{subset}: {str(e)}")
            return result

        # Apply column mapping
        if dataset_name in structure_check["datasets"]:
            logger.info(f"Applying column mapping for {dataset_name}/{subset}")
            column_mapping = structure_check["column_mappings"][dataset_name][subset]
            logger.info(f"Column mapping: {column_mapping}")
            try:
                dataset = dataset.rename_columns(column_mapping)
                result["mapping_applied"] = True
                logger.info(f"Successfully applied column mapping for {dataset_name}/{subset}")
            except Exception as e:
                logger.error(f"Failed to apply column mapping: {str(e)}")
                result["errors"].append(f"Failed to apply column mapping: {str(e)}")
        else:
            logger.warning(f"No column mapping found for {dataset_name}/{subset}")

    except Exception as e:
        logger.error(f"Unexpected error during integration check: {str(e)}")
        result["errors"].append(f"Unexpected error during integration check: {str(e)}")

    return result

def check_multiple_datasets(datasets: List[Dict[str, str]], column_mapping_path: Path) -> Dict[str, Any]:
    """
    Check the integration of multiple datasets.
    
    Args:
        datasets (List[Dict[str, str]]): List of dictionaries containing dataset names and subsets.
        column_mapping_path (Path): Path to the column mapping YAML file.
    
    Returns:
        Dict[str, Any]: A dictionary containing the integration check results for all datasets.
    """
    results = {}
    for dataset_info in datasets:
        dataset_name = dataset_info["name"]
        subset = dataset_info["subset"]
        results[f"{dataset_name}/{subset}"] = check_dataset_integration(dataset_name, subset, column_mapping_path)
    return results

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    column_mapping_path = Path("../../config/column_mapping.yaml")
    datasets_to_check = [
        {"name": "imomayiz/darija-english", "subset": "sentences"},
        {"name": "atlasia/darija_english", "subset": "web_data"}
    ]
    
    integration_results = check_multiple_datasets(datasets_to_check, column_mapping_path)
    
    for dataset, result in integration_results.items():
        logger.info(f"Integration check for {dataset}:")
        logger.info(f"  Dataset loaded: {result['dataset_loaded']}")
        logger.info(f"  Mapping applied: {result['mapping_applied']}")
        if result["errors"]:
            logger.error("  Errors:")
            for error in result["errors"]:
                logger.error(f"    - {error}")
        logger.info("---")
