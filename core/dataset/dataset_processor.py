# File: dataset_processor.py
"""
Dataset Processor
Author: dboa9
Date: 10_11_24_23_55
"""

import logging
from typing import Dict, Any, Union, List

from datasets import Dataset, IterableDataset, DatasetDict, IterableDatasetDict

class DatasetProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_dataset(self, dataset: Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]) -> Dict[str, Any]:
        """
        Process the dataset based on its type.
        
        Args:
            dataset (Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]): The loaded dataset.
        
        Returns:
            Dict[str, Any]: Processed information about the dataset.
        """
        processed_info = {
            'type': self._get_dataset_type(dataset),
            'sample': self._get_dataset_sample(dataset)
        }
        return processed_info

    def _get_dataset_type(self, dataset: Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]) -> str:
        if isinstance(dataset, Dataset):
            return 'Dataset'
        elif isinstance(dataset, IterableDataset):
            return 'IterableDataset'
        elif isinstance(dataset, DatasetDict):
            return 'DatasetDict'
        elif isinstance(dataset, IterableDatasetDict):
            return 'IterableDatasetDict'
        else:
            return 'Unknown'

    def _get_dataset_sample(self, dataset: Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        if isinstance(dataset, Dataset):
            return dataset[:5] if len(dataset) > 5 else dataset[:]
        elif isinstance(dataset, IterableDataset):
            return list(dataset.take(5))
        elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            sample = {}
            for split, ds in dataset.items():
                if isinstance(ds, Dataset):
                    sample[split] = ds[:5] if len(ds) > 5 else ds[:]
                elif isinstance(ds, IterableDataset):
                    sample[split] = list(ds.take(5))
            return sample
        else:
            return []

# Example usage
if __name__ == "__main__":
    from hf_base_loader import HFBaseLoader
    
    logging.basicConfig(level=logging.INFO)
    loader = HFBaseLoader()
    processor = DatasetProcessor()
    
    try:
        dataset = loader.load_dataset("imomayiz/darija-english")
        processed_info = processor.process_dataset(dataset)
        print("Processed Dataset Info:")
        print(f"Type: {processed_info['type']}")
        print(f"Sample: {processed_info['sample']}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
