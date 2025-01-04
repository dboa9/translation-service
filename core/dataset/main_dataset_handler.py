# File: main_dataset_handler.py
"""
Main Dataset Handler
Author: dboa9
Date: 11_11_24_00_20
"""

import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from core.dataset import (
    check_column_mapping_structure,
    check_dataset_integration,
    check_multiple_datasets,
    handle_dataset_errors,
    log_dataset_info,
    DatasetError
)

from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MainDatasetHandler:
    def __init__(self, column_mapping_path: Path):
        self.column_mapping_path = column_mapping_path

    @handle_dataset_errors
    def process_dataset(self, dataset_name: str, subset: str) -> Dict[str, Any]:
        """
        Process a single dataset by checking its structure, integration, and handling any errors.

        Args:
            dataset_name (str): Name of the dataset to process.
            subset (str): Subset of the dataset to process.

        Returns:
            Dict[str, Any]: A dictionary containing the processing results.
        """
        # Check column mapping structure
        structure_check = check_column_mapping_structure(self.column_mapping_path)
        if not structure_check["valid_structure"]:
            raise DatasetError(f"Invalid column mapping structure: {', '.join(structure_check['errors'])}")

        # Check dataset integration
        integration_result = check_dataset_integration(dataset_name, subset, self.column_mapping_path)
        
        if integration_result["errors"]:
            raise DatasetError(f"Dataset integration failed: {', '.join(integration_result['errors'])}")

        # Log dataset info
        log_dataset_info(dataset_name, subset, {
            "loaded": integration_result["dataset_loaded"],
            "mapping_applied": integration_result["mapping_applied"]
        })

        return integration_result

    def process_multiple_datasets(self, datasets: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
        """
        Process multiple datasets.

        Args:
            datasets (List[Dict[str, str]]): List of dictionaries containing dataset names and subsets.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary containing the processing results for all datasets.
        """
        results = {}
        for dataset_info in datasets:
            dataset_name = dataset_info["name"]
            subset = dataset_info["subset"]
            try:
                results[f"{dataset_name}/{subset}"] = self.process_dataset(dataset_name, subset)
            except DatasetError as e:
                logger.error(f"Error processing dataset {dataset_name}/{subset}: {str(e)}")
                results[f"{dataset_name}/{subset}"] = {"error": str(e)}
        return results

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current working directory: {Path.cwd()}")
    logger.info(f"Contents of current directory: {list(Path.cwd().glob('*'))}")
    logger.info(f"Contents of core directory: {list(Path.cwd().glob('core/*'))}")
    
    # Assuming the column_mapping.yaml file is in the config directory at the project root
    column_mapping_path = project_root / "config" / "column_mapping.yaml"
    handler = MainDatasetHandler(column_mapping_path)
    
    datasets_to_process = [
        {"name": "imomayiz/darija-english", "subset": "sentences"},
        {"name": "atlasia/darija_english", "subset": "web_data"}
    ]
    
    results = handler.process_multiple_datasets(datasets_to_process)
    
    for dataset, result in results.items():
        if "error" in result:
            logger.error(f"Failed to process {dataset}: {result['error']}")
        else:
            logger.info(f"Successfully processed {dataset}")
            logger.info(f"  Dataset loaded: {result['dataset_loaded']}")
            logger.info(f"  Mapping applied: {result['mapping_applied']}")
