from typing import Dict, Any, Union
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
import logging
from core.config_analysis.column_mapping_analyzer import ColumnMappingAnalyzer, initialize_analyzer

logger = logging.getLogger(__name__)

def perform_extended_column_analysis(dataset_name: str, dataset: Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]) -> Dict[str, Any]:
    """
    Performs extended analysis on the column mapping of a dataset.
    """
    logger.info(f"Performing extended column analysis for dataset: {dataset_name}")
    # Add your extended analysis logic here
    # Example: Check for specific column combinations, data types, etc.
    extended_results = {}
    if isinstance(dataset, (DatasetDict, IterableDatasetDict)):
        for split_name, split_dataset in dataset.items():
            if isinstance(split_dataset, IterableDataset):
                split_dataset = Dataset.from_dict(next(iter(split_dataset)))
            # Example: Check if 'source_text' and 'target_text' columns exist
            if 'source_text' not in split_dataset.column_names or 'target_text' not in split_dataset.column_names:
                logger.error(f"Missing 'source_text' or 'target_text' columns in split: {split_name} of dataset: {dataset_name}")
                extended_results[split_name] = False
            else:
                extended_results[split_name] = True
    elif isinstance(dataset, (Dataset, IterableDataset)):
        if isinstance(dataset, IterableDataset):
            dataset = Dataset.from_dict(next(iter(dataset)))
        # Example: Check if 'source_text' and 'target_text' columns exist
        if 'source_text' not in dataset.column_names or 'target_text' not in dataset.column_names:
            logger.error(f"Missing 'source_text' or 'target_text' columns in dataset: {dataset_name}")
            extended_results["full_dataset"] = False
        else:
            extended_results["full_dataset"] = True
    return extended_results
