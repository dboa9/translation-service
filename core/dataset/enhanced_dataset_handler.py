# File: enhanced_dataset_handler.py
import logging
from typing import Dict, Any, Union, List

from datasets import Dataset, IterableDataset, DatasetDict, IterableDatasetDict

class EnhancedDatasetHandler:
    def __init__(self):
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return logger

    def handle_dataset(self, dataset: Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]) -> Dict[str, Any]:
        """
        Handle the dataset based on its type.
        
        Args:
            dataset (Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]): The loaded dataset.
        
        Returns:
            Dict[str, Any]: Processed information about the dataset.
        """
        dataset_type = self._get_dataset_type(dataset)
        self.logger.info(f"Handling dataset of type: {dataset_type}")
        
        processed_info = {
            'type': dataset_type,
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

    def _get_dataset_sample(self, dataset: Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict]) -> Dict[str, Any]:
        if isinstance(dataset, Dataset):
            return {'sample': dataset[:5] if len(dataset) > 5 else dataset[:]}
        elif isinstance(dataset, IterableDataset):
            return {'sample': list(dataset.take(5))}
        elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            sample = {}
            for split, ds in dataset.items():
                if isinstance(ds, Dataset):
                    sample[split] = ds[:5] if len(ds) > 5 else ds[:]
                elif isinstance(ds, IterableDataset):
                    sample[split] = list(ds.take(5))
            return {'sample': sample}
        else:
            return {'sample': None}

# Example usage
if __name__ == "__main__":
    from hf_base_loader import HFBaseLoader
    
    logging.basicConfig(level=logging.INFO)
    loader = HFBaseLoader()
    handler = EnhancedDatasetHandler()
    
    try:
        dataset = loader.load_dataset("imomayiz/darija-english")
        processed_info = handler.handle_dataset(dataset)
        print("Processed Dataset Info:")
        print(f"Type: {processed_info['type']}")
        print(f"Sample: {processed_info['sample']}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
