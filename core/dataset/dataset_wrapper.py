import logging
import os
import shutil
from typing import Optional, Union

from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

from core.dataset.data_reader import DataReader
from core.dataset.dataset_validator import DatasetValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

class DatasetWrapper:
    def __init__(self, base_dir: str):
        # Update the base_dir to point to the correct location
        self.base_dir = "/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project"
        self.data_reader = DataReader(self.base_dir)
        self.validator = DatasetValidator(self.data_reader.config)
        self.cache_dir = os.path.join(self.base_dir, 'datasets_cache')

    def load_and_validate_dataset(self, dataset_name: str, subset: str) -> Optional[DatasetType]:
        logger.info(f"Loading dataset: {dataset_name}, subset: {subset}")
        
        try:
            # Clear cache only if previous load attempts failed
            if self._should_clear_cache(dataset_name, subset):
                self._clear_cache(dataset_name)

            dataset = self.data_reader.load_dataset(dataset_name, subset)
            
            if dataset is None:
                logger.error(f"Failed to load dataset: {dataset_name}, subset: {subset}")
                return None

            if dataset_name == "M-A-D/DarijaBridge":
                dataset = self._handle_mad_darija_bridge(dataset)
            elif dataset_name == "imomayiz/darija-english" and subset == "submissions":
                dataset = self.handle_imomayiz_submissions(dataset)

            self.validator.validate_dataset(dataset, dataset_name, subset)
            logger.info(f"Successfully loaded and validated dataset: {dataset_name}, subset: {subset}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading dataset {dataset_name}/{subset}: {str(e)}", exc_info=True)
            self._mark_cache_as_failed(dataset_name, subset)
            return None

    def _should_clear_cache(self, dataset_name: str, subset: str) -> bool:
        marker_file = os.path.join(self.cache_dir, f"{dataset_name}_{subset}_failed")
        return os.path.exists(marker_file)

    def _clear_cache(self, dataset_name: str) -> None:
        cache_path = os.path.join(self.cache_dir, dataset_name.replace('/', '___'))
        if os.path.exists(cache_path):
            logger.info(f"Clearing cache for dataset: {dataset_name}")
            shutil.rmtree(cache_path)

    def _mark_cache_as_failed(self, dataset_name: str, subset: str) -> None:
        marker_file = os.path.join(self.cache_dir, f"{dataset_name}_{subset}_failed")
        with open(marker_file, 'w') as f:
            f.write('failed')

    def _handle_mad_darija_bridge(self, dataset: DatasetType) -> DatasetType:
        if isinstance(dataset, dict):
            logger.info("Converting M-A-D/DarijaBridge dataset from dict to Dataset")
            return Dataset.from_dict(dataset)
        return dataset

    def handle_imomayiz_submissions(self, dataset: DatasetType) -> DatasetType:
        logger.info("Custom handling for imomayiz/darija-english submissions")
        # Implement custom handling logic here
        # For now, we'll just return the dataset as-is
        return dataset
