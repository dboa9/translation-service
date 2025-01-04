from typing import Optional, Union
from datasets import load_dataset, Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from core.dataset.config.data_paths import DataPaths
import logging

logger = logging.getLogger(__name__)

class ParallelLoader:
    def __init__(self, data_paths: DataPaths):
        self.data_paths = data_paths

    def load_dataset(self, dataset_name: str, config: Optional[str] = None) -> Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict, None]:
        try:
            return load_dataset(dataset_name, config)
        except Exception as e:
            logger.error(f"Error loading dataset {dataset_name}: {str(e)}")
            return None

def initialize_parallel_loader(base_dir: str) -> ParallelLoader:
    data_paths = DataPaths(base_dir)
    return ParallelLoader(data_paths)
