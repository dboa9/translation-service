import logging
import os
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
import yaml

from datasets import (
    Dataset,
    DatasetDict,
    IterableDataset,
    IterableDatasetDict,
    load_dataset,
    load_from_disk,
)

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict, Dict[str, IterableDataset]]

def ensure_dataset(data: Any) -> Dataset:
    """Convert various dataset types to Dataset."""
    if isinstance(data, IterableDataset):
        return Dataset.from_dict(dict(next(iter(data))))
    if isinstance(data, IterableDatasetDict):
        first_split = next(iter(data.values()))
        return Dataset.from_dict(dict(next(iter(first_split))))
    if isinstance(data, DatasetDict):
        first_split = next(iter(data.values()))
        if isinstance(first_split, Dataset):
            return first_split
        raise ValueError("Invalid dataset format")
    if isinstance(data, Dataset):
        return data
    if isinstance(data, dict):
        return Dataset.from_dict(data)
    raise ValueError("Invalid dataset format")

class DataPaths:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.test_data_dir = self.base_dir / "test_data_sample"
        self.cache_dir = self.base_dir / "datasets_cache"

    def get_dataset_test_path(self, dataset_name: str) -> Path:
        return self.test_data_dir / dataset_name.replace("/", "_")

    def get_dataset_cache_path(self, dataset_name: str) -> Path:
        return self.cache_dir / dataset_name.replace("/", "___")

class HFBaseLoader:
    def __init__(self, data_paths: DataPaths, config_path: str = 'config/column_mapping.yaml'):
        self.paths = data_paths
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(Path(config_path), 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading configuration from {config_path}: {e}")
            raise

    def load_dataset(
        self,
        dataset_name: str,
        subset: str,
        use_test_data: bool = True
    ) -> Optional[DatasetType]:
        """Load dataset from test data or cache, fallback to HuggingFace"""
        try:
            if use_test_data:
                dataset = self._load_test_dataset(dataset_name, subset)
                if dataset is not None:
                    return dataset
            
            return self._load_cache_dataset(dataset_name, subset)
        except Exception as e:
            self.logger.error(f"Error loading dataset {dataset_name}: {e}")
            return None
            
    def _load_test_dataset(
        self,
        dataset_name: str,
        subset: str
    ) -> Optional[DatasetType]:
        """Load from test data directory"""
        try:
            file_path = (
                self.paths.get_dataset_test_path(dataset_name) /
                f"{subset}_sample.csv"
            )
            if file_path.exists():
                self.logger.info(f"Loading test dataset from {file_path}")
                return Dataset.from_csv(str(file_path))
            return None
        except Exception as e:
            self.logger.warning(f"Could not load test dataset: {e}")
            return None
            
    def _load_cache_dataset(
        self,
        dataset_name: str,
        subset: str
    ) -> Optional[DatasetType]:
        """Load from cache or download from HuggingFace"""
        try:
            cache_path = self.paths.get_dataset_cache_path(dataset_name)
            
            # Try loading from cache first
            if cache_path.exists():
                try:
                    self.logger.info(f"Loading dataset from cache: {cache_path}")
                    cached = load_from_disk(str(cache_path))
                    return cached
                except Exception as e:
                    self.logger.warning(f"Could not load from cache: {e}")
                    
            # Download from HuggingFace
            self.logger.info(f"Downloading dataset from HuggingFace: {dataset_name}/{subset}")
            dataset = load_dataset(
                dataset_name,
                subset,
                cache_dir=str(self.paths.cache_dir)
            )
            
            # Save to cache if it's a Dataset or DatasetDict
            if isinstance(dataset, (Dataset, DatasetDict)):
                os.makedirs(str(cache_path), exist_ok=True)
                self.logger.info(f"Saving dataset to cache: {cache_path}")
                dataset.save_to_disk(str(cache_path))
            return dataset
        except Exception as e:
            self.logger.error(f"Error downloading dataset: {e}")
            return None

    def get_column_mapping(self, dataset_name: str, subset: str) -> Dict[str, str]:
        try:
            return {col: col for col in self.config['datasets'][dataset_name]['required_columns'][subset]}
        except KeyError:
            error_msg = f"Column mapping not found for dataset '{dataset_name}' and subset '{subset}'"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

def get_dataset_columns(dataset: Optional[DatasetType]) -> List[str]:
    if dataset is None:
        return []
    if isinstance(dataset, (Dataset, DatasetDict)):
        columns = dataset.column_names
        if isinstance(columns, dict):
            return list(set().union(*columns.values()))
        return columns or []
    if isinstance(dataset, IterableDataset):
        return list(dataset.features.keys()) if dataset.features is not None else []
    if isinstance(dataset, IterableDatasetDict):
        first_split = next(iter(dataset.values()))
        return list(first_split.features.keys()) if first_split.features is not None else []
    if isinstance(dataset, dict):
        return list(dataset.keys())
    return []

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    base_dir = Path(
        "/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/"
        "daija_dataset_tests_project"
    )
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
        if dataset is not None:
            print(
                f"Successfully loaded dataset: {dataset_name} "
                f"(subset: {subset})"
            )
            columns = get_dataset_columns(dataset)
            print(f"Columns: {columns}")
            try:
                print(f"Column mapping: {loader.get_column_mapping(dataset_name, subset)}")
            except ValueError as e:
                print(f"Error getting column mapping: {str(e)}")
        else:
            print(
                f"Failed to load dataset: {dataset_name} "
                f"(subset: {subset})"
            )
