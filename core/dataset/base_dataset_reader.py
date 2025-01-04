# File: base_dataset_reader.py
import logging
from pathlib import Path
from typing import Optional, Union

from datasets import (
    Dataset,
    DatasetDict,
    IterableDataset,
    IterableDatasetDict,
    load_dataset,
)


class BaseDatasetReader:
    def __init__(self, cache_dir: str = "./dataset_cache"):
        self.cache_dir = Path(cache_dir)
        self.logger = logging.getLogger(__name__)

    def load_dataset(
        self, dataset_name: str
    ) -> Optional[Union[Dataset, IterableDataset, DatasetDict,
                        IterableDatasetDict]]:
        """Load a dataset from Hugging Face"""
        try:
            self.logger.info("Loading dataset: %s", dataset_name)
            dataset = load_dataset(dataset_name, cache_dir=str(self.cache_dir))
            
            self.logger.info("Successfully loaded dataset %s", dataset_name)
            self._log_dataset_info(dataset)
            return dataset
            
        except Exception as e:
            self.logger.error("Error loading dataset %s: %s", dataset_name, e)
            return None

    def _log_dataset_info(
        self, dataset: Union[Dataset, IterableDataset, DatasetDict,
                             IterableDatasetDict]
    ):
        """Log basic information about the dataset"""
        self.logger.debug("Dataset type: %s", type(dataset).__name__)
        if isinstance(dataset, (Dataset, DatasetDict)):
            self._log_dataset_size(dataset)

    def _log_dataset_size(self, dataset: Union[Dataset, DatasetDict]):
        """Log the size of the dataset"""
        if isinstance(dataset, Dataset):
            self.logger.debug("Number of rows: %d", len(dataset))
        elif isinstance(dataset, DatasetDict):
            for split_name, split_dataset in dataset.items():
                self.logger.debug("Split: %s, Number of rows: %d",
                                  split_name, len(split_dataset))

# The file ends here
