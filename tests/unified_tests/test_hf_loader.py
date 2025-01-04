# File: test_hf_loader.py
import logging
import os
from pathlib import Path
from typing import Optional

from datasets import (
    Dataset,
    DatasetDict,
    IterableDataset,
    IterableDatasetDict,
    load_dataset,
    load_from_disk,
)


class DatasetReader:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir

    def load_dataset(self, dataset_name: str) -> Optional[Dataset]:
        try:
            cache_path = os.path.join(
                self.cache_dir, dataset_name.replace('/', '___')
            )
            if os.path.exists(cache_path):
                return Dataset.load_from_disk(cache_path)
            
            dataset = load_dataset(dataset_name)
            
            # Check if the dataset is an IterableDataset or IterableDatasetDict
            if isinstance(dataset, (IterableDataset, IterableDatasetDict)):
                # Convert IterableDataset to Dataset
                dataset = Dataset.from_dict(next(iter(dataset)))
            
            # Check if the dataset is a DatasetDict
            if isinstance(dataset, DatasetDict):
                # Convert DatasetDict to Dataset
                dataset = next(iter(dataset.values()))
            
            os.makedirs(cache_path, exist_ok=True)
            dataset.save_to_disk(cache_path)
            return dataset
        except Exception as e:
            print(f"Error loading dataset {dataset_name}: {str(e)}")
            return None

class DataPaths:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.test_data_dir = base_dir / "test_data_sample"
        self.cache_dir = base_dir / "datasets_cache"

    def get_dataset_test_path(self, dataset_name: str) -> Path:
        return self.test_data_dir / dataset_name.replace("/", "_")

    def get_dataset_cache_path(self, dataset_name: str) -> Path:
        return self.cache_dir / dataset_name.replace("/", "___")

class HFBaseLoader:
    def __init__(self, data_paths: DataPaths):
        self.paths = data_paths
        self.logger = logging.getLogger(__name__)

    def load_dataset(
        self,
        dataset_name: str,
        subset: Optional[str] = None,
        use_test_data: bool = True
    ) -> Optional[Dataset]:
        """Load dataset from test data or cache, fallback to HuggingFace"""
        try:
            if use_test_data:
                dataset = self._load_test_dataset(dataset_name, subset)
                if dataset:
                    return dataset
            
            return self._load_cache_dataset(dataset_name, subset)
        except Exception as e:
            self.logger.error(f"Error loading dataset {dataset_name}: {e}")
            return None
            
    def _load_test_dataset(
        self,
        dataset_name: str,
        subset: Optional[str] = None
    ) -> Optional[Dataset]:
        """Load from test data directory"""
        file_path = self.paths.get_dataset_test_path(dataset_name) / f"{subset}_sample.csv"
        if file_path.exists():
            return Dataset.from_csv(str(file_path))
        
        return None
            
    def _load_cache_dataset(
        self,
        dataset_name: str,
        subset: Optional[str] = None
    ) -> Optional[Dataset]:
        """Load from cache or download from HuggingFace"""
        cache_path = self.paths.get_dataset_cache_path(dataset_name)
        
        # Try loading from cache first
        if cache_path.exists():
            try:
                return load_from_disk(str(cache_path))
            except Exception as e:
                self.logger.warning(f"Could not load from cache: {e}")
                
        # Download from HuggingFace
        try:
            dataset = load_dataset(dataset_name, subset, cache_dir=str(self.paths.cache_dir))
            
            # Check if the dataset is an IterableDataset or IterableDatasetDict
            if isinstance(dataset, (IterableDataset, IterableDatasetDict)):
                # Convert IterableDataset to Dataset
                dataset = Dataset.from_dict(next(iter(dataset)))
            
            # Check if the dataset is a DatasetDict
            if isinstance(dataset, DatasetDict):
                # Convert DatasetDict to Dataset
                dataset = next(iter(dataset.values()))
            
            # Save to cache
            os.makedirs(cache_path, exist_ok=True)
            dataset.save_to_disk(cache_path)
            return dataset
        except Exception as e:
            self.logger.error(f"Error downloading dataset: {e}")
            return None

# Example usage
if __name__ == "__main__":
    base_dir = Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project")
    data_paths = DataPaths(base_dir)
    loader = HFBaseLoader(data_paths)
    
    datasets_to_load = [
        ("atlasia/darija_english", "comments"),
        ("imomayiz/darija-english", "sentences"),
        ("M-A-D/DarijaBridge", "default"),
        ("BounharAbdelaziz/English-to-Moroccan-Darija", "default")
    ]
    
    for dataset_name, subset in datasets_to_load:
        dataset = loader.load_dataset(dataset_name, subset)
        if dataset:
            print(f"Successfully loaded dataset: {dataset_name} (subset: {subset})")
            print(f"Columns: {dataset.column_names}")
        else:
            print(f"Failed to load dataset: {dataset_name} (subset: {subset})")