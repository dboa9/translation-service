from typing import Dict, Any, Optional, Union
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from core.dataset.config.data_paths import DataPaths
from .config_loader import initialize_config_loader
from .column_validator import validate_columns
from .dataset_preprocessor import preprocess_dataset
from ..utils.cache_manager import initialize_cache_manager
import logging
import yaml

logger = logging.getLogger(__name__)

class ColumnMappingAnalyzer:
    def __init__(self, data_paths: DataPaths):
        self.data_paths = data_paths
        config_loader = initialize_config_loader(str(data_paths.base_dir))
        self.config = config_loader.load_config()
        self.cache_manager = initialize_cache_manager()

    def analyze_column_mapping(self, dataset_name: str, dataset: Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict], config: Optional[str] = None) -> Dict[str, Any]:
        cache_key = f"{dataset_name}_{config}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        if isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            # Assuming we want to validate the first split
            split_name, split_dataset = next(iter(dataset.items()))
        else:
            split_name, split_dataset = None, dataset

        if isinstance(split_dataset, IterableDataset):
            # Convert IterableDataset to Dataset for validation
            split_dataset = Dataset.from_dict(next(iter(split_dataset)))

        result = validate_columns(split_dataset, dataset_name, config, split_name)
        self.cache_manager.set(cache_key, result)
        return result

    def preprocess_dataset(self, dataset: Union[Dataset, IterableDataset], dataset_name: str, config: Optional[str] = None) -> Union[Dataset, IterableDataset]:
        dataset_config = self.config.get('datasets', {}).get(dataset_name, {})
        config_to_use = config if config else 'default'
        if config_to_use not in dataset_config:
            logger.warning(f"Config '{config_to_use}' not found for dataset '{dataset_name}'. Using default preprocessing.")
            return dataset
        if isinstance(dataset, IterableDataset):
            # Convert IterableDataset to Dataset for preprocessing
            dataset = Dataset.from_dict(next(iter(dataset)))
        return preprocess_dataset(dataset, dataset_name, config_to_use, dataset_config)

def initialize_analyzer(base_dir: str) -> ColumnMappingAnalyzer:
    data_paths = DataPaths(base_dir)
    return ColumnMappingAnalyzer(data_paths)

def load_yaml_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
