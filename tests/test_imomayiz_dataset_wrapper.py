import logging
import pytest
from typing import Optional, Union, List
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

DATASET_CONFIGS = {
    "imomayiz/darija-english": {
        "subsets": ["sentences"],
        "required_columns": {
            "sentences": ["darija", "eng", "darija_ar"]
        }
    }
}

class TestImomayizDatasetWrapper:
    @pytest.fixture(autouse=True)
    def setup(self, project_root_path, dataset_wrapper, credentials):
        self.base_dir = str(project_root_path)
        self.cache_dir = credentials.get('cache_dir', './cache')
        self.wrapper = dataset_wrapper
        logger.debug(f"TestImomayizDatasetWrapper set up with base_dir: {self.base_dir}, cache_dir: {self.cache_dir}")

    def _print_dataset_info(self, dataset: Optional[DatasetType], subset: str):
        if dataset is None:
            logger.info(f"Dataset for {subset} is None")
            return

        logger.info(f"Dataset type for {subset}: {type(dataset)}")
        if isinstance(dataset, (Dataset, DatasetDict)):
            logger.info(f"Dataset keys: {dataset.keys() if isinstance(dataset, DatasetDict) else 'No keys (Dataset)'}")
            if isinstance(dataset, DatasetDict):
                logger.info(f"Dataset columns: {dataset['train'].column_names if 'train' in dataset else 'No train split'}")
            else:
                logger.info(f"Dataset columns: {dataset.column_names}")
        elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
            logger.info(f"Dataset is Iterable. Cannot display keys or columns.")
        else:
            logger.info(f"Unknown dataset type: {type(dataset)}")

    def _get_column_names(self, dataset: DatasetType) -> Optional[List[str]]:
        if isinstance(dataset, (Dataset, IterableDataset)):
            return dataset.column_names
        elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            first_split = next(iter(dataset.values()))
            return first_split.column_names if first_split else None
        else:
            logger.error(f"Unexpected dataset type: {type(dataset)}")
            return None

    def _assert_columns_present(self, column_names: List[str], dataset_name: str, subset: str):
        expected_columns = DATASET_CONFIGS[dataset_name]["required_columns"][subset]
        for col in expected_columns:
            assert col in column_names, f"'{col}' column not found in dataset for subset {subset}. Available columns: {column_names}"

    def test_imomayiz_darija_english(self):
        dataset_name = "imomayiz/darija-english"
        for subset in DATASET_CONFIGS[dataset_name]["subsets"]:
            logger.info(f"Testing subset: {subset}")
            dataset = self.wrapper.load_and_validate_dataset(dataset_name, subset)
            assert dataset is not None, f"Dataset is None for subset: {subset}"
            self._print_dataset_info(dataset, subset)
            column_names = self._get_column_names(dataset)
            assert column_names is not None, f"Failed to get column names for subset: {subset}"
            self._assert_columns_present(column_names, dataset_name, subset)
