# File: enhanced_hf_loader.py
"""
Enhanced HuggingFace Loader
Author: dboa9
Date: 10_11_24_22_23
Updated: 10_11_24_23_55
"""

from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import yaml

from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

from .hf_base_loader import HFBaseLoader

class EnhancedHFLoader(HFBaseLoader):
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        super().__init__(cache_dir=cache_dir)
        self.column_mapping = self._load_column_mapping()

    def _load_column_mapping(self) -> Dict:
        column_mapping_path = Path(__file__).resolve().parent.parent.parent / "config" / "column_mapping.yaml"
        try:
            with open(column_mapping_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading column mapping: {str(e)}")
            return {}

    def load_dataset(self, dataset_name: str, subset: Optional[str] = None, **kwargs) -> Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]:
        """
        Load a dataset from HuggingFace Hub or local cache with enhanced functionality.
        
        Args:
            dataset_name (str): Name of the dataset to load.
            subset (Optional[str]): Subset of the dataset to load, if applicable.
            **kwargs: Additional arguments to pass to load_dataset.
        
        Returns:
            Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]: Loaded dataset.
        """
        dataset = super().load_dataset(dataset_name, **kwargs)
        
        if dataset_name in self.column_mapping['datasets']:
            config = self.column_mapping['datasets'][dataset_name]
            if subset:
                if subset in config['columns']:
                    dataset = self._apply_column_mapping(dataset, config['columns'])
                else:
                    self.logger.warning(f"Subset '{subset}' not found in configuration for {dataset_name}")
            elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
                # If no subset is specified, apply mappings to all subsets
                for subset_name, subset_data in dataset.items():
                    dataset[subset_name] = self._apply_column_mapping(subset_data, config['columns'])
            else:
                dataset = self._apply_column_mapping(dataset, config['columns'])
        
        return dataset

    def _apply_column_mapping(self, dataset: Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict], columns: List[str]) -> Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]:
        """
        Apply column mapping to the dataset.
        
        Args:
            dataset (Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]): The dataset to apply mapping to.
            columns (List[str]): List of columns to keep in the dataset.
        
        Returns:
            Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]: Dataset with applied column mapping.
        """
        if isinstance(dataset, Dataset):
            return dataset.select_columns(columns)
        elif isinstance(dataset, DatasetDict):
            return DatasetDict({k: self._apply_column_mapping(v, columns) for k, v in dataset.items()})
        elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
            self.logger.warning(f"Column mapping not supported for {type(dataset).__name__}")
            return dataset
        else:
            raise ValueError(f"Unsupported dataset type: {type(dataset)}")

    def get_column_names(self, dataset: Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]) -> Union[List[str], Dict[str, List[str]]]:
        """
        Get column names from the dataset.
        
        Args:
            dataset (Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]): The dataset to get column names from.
        
        Returns:
            Union[List[str], Dict[str, List[str]]]: Column names of the dataset.
        """
        if isinstance(dataset, (Dataset, IterableDataset)):
            return dataset.column_names or []
        elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            return {k: v.column_names or [] for k, v in dataset.items()}
        else:
            raise ValueError(f"Unsupported dataset type: {type(dataset)}")

# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    loader = EnhancedHFLoader()
    
    try:
        dataset = loader.load_dataset("imomayiz/darija-english", subset="sentences")
        print(f"Loaded dataset: {type(dataset)}")
        print(f"Columns: {loader.get_column_names(dataset)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
