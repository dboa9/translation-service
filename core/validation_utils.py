import logging
import pandas as pd
import yaml
from typing import Dict, Any

logger = logging.getLogger(__name__)

def validate_dataset(df: pd.DataFrame, dataset_name: str, config: str):
    logger.info(f"Validating dataset: {dataset_name} (config: {config})")
    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Dataset columns: {df.columns.tolist()}")
    logger.info(f"Dataset info:\n{df.info(verbose=True, show_counts=True)}")
    logger.info(f"First few rows:\n{df.head().to_string()}")

def check_column_mapping(mapping_file: str) -> Dict[str, Any]:
    logger.info(f"Checking column mapping file: {mapping_file}")
    try:
        with open(mapping_file, 'r') as f:
            mapping = yaml.safe_load(f)
        
        # Validate the structure of the mapping
        if not isinstance(mapping, dict):
            raise ValueError("Column mapping should be a dictionary")
        
        for dataset, config in mapping.items():
            if not isinstance(config, dict):
                raise ValueError(f"Configuration for dataset '{dataset}' should be a dictionary")
            
            if 'columns' not in config:
                raise ValueError(f"Missing 'columns' key in configuration for dataset '{dataset}'")
            
            if not isinstance(config['columns'], dict):
                raise ValueError(f"'columns' for dataset '{dataset}' should be a dictionary")
        
        logger.info("Column mapping structure is valid")
        return mapping
    except Exception as e:
        logger.error(f"Error checking column mapping: {str(e)}")
        raise
