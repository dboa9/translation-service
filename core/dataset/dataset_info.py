# File: dataset_info.py
"""
Dataset Information Retrieval
Author: dboa9
Date: 10_11_24_23_55
"""

import logging
from typing import Dict, Any, Union

from datasets import Dataset, IterableDataset, DatasetDict, IterableDatasetDict

class DatasetInfo:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_dataset_info(self, dataset: Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]) -> Dict[str, Any]:
        """
        Get information about the loaded dataset.
        
        Args:
            dataset (Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]): The loaded dataset.
        
        Returns:
            Dict[str, Any]: Information about the dataset.
        """
        info = {}
        
        if isinstance(dataset, (Dataset, IterableDataset)):
            info['type'] = 'Dataset' if isinstance(dataset, Dataset) else 'IterableDataset'
            info['num_rows'] = dataset.num_rows if isinstance(dataset, Dataset) else 'Unknown (IterableDataset)'
            info['features'] = dataset.features
        elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            info['type'] = 'DatasetDict' if isinstance(dataset, DatasetDict) else 'IterableDatasetDict'
            info['splits'] = list(dataset.keys())
            info['features'] = {split: ds.features for split, ds in dataset.items()}
            if isinstance(dataset, DatasetDict):
                info['num_rows'] = {split: ds.num_rows for split, ds in dataset.items()}
            else:
                info['num_rows'] = {split: 'Unknown (IterableDataset)' for split in dataset.keys()}
        
        return info

# Example usage
if __name__ == "__main__":
    from hf_base_loader import HFBaseLoader
    
    logging.basicConfig(level=logging.INFO)
    loader = HFBaseLoader()
    info_retriever = DatasetInfo()
    
    try:
        dataset = loader.load_dataset("imomayiz/darija-english")
        info = info_retriever.get_dataset_info(dataset)
        print("Dataset Info:", info)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
