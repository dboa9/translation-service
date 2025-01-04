import os
import sys
from pathlib import Path
import unittest
import logging
from typing import Union, List, Dict, Any

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from core.dataset.hf_base_loader import HFBaseLoader
from core.dataset.config.data_paths import DataPaths
from core.dataset.dataset_types import DatasetType
from core.dataset.integration_checker import IntegrationChecker
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

logger = logging.getLogger(__name__)

DATASET_CONFIGS = {
    "atlasia/darija_english": {
        "subsets": ["web_data", "comments", "stories", "doda", "transliteration"],
    }
}

class TestAtlasiaLoading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = Path(project_root)
        cls.data_paths = DataPaths(str(cls.base_dir))
        config_path = cls.base_dir / 'config' / 'dataset_loader_debug.yaml'
        cls.loader = HFBaseLoader(base_dir=str(cls.base_dir))
        cls.integration_checker = IntegrationChecker(config_path)

    def test_atlasia_loading(self):
        dataset_name = "atlasia/darija_english"
        for subset in DATASET_CONFIGS[dataset_name]["subsets"]:
            with self.subTest(subset=subset):
                try:
                    dataset = self.loader.load_dataset(dataset_name, subset)
                    self.assertIsNotNone(dataset, f"Failed to load dataset {dataset_name} - {subset}")
                    self.assertTrue(self._dataset_has_data(dataset), f"Dataset {dataset_name} - {subset} is empty")
                    
                    logger.info(f"Successfully loaded {dataset_name} - {subset}")
                    logger.info(f"  Columns: {', '.join(self._get_column_names(dataset))}")
                    logger.info(f"  Number of rows: {self._get_dataset_size(dataset)}")
                    
                    # Check integration
                    integration_result = self.integration_checker.check_integration(dataset_name, subset)
                    self.assertTrue(integration_result, f"Integration check failed for {dataset_name} ({subset})")
                    logger.info(f"Integration check passed for {dataset_name} ({subset})")
                except Exception as e:
                    logger.error(f"Error during loading or integration check for {dataset_name} ({subset}): {str(e)}")
                    self.fail(f"Test failed for {dataset_name} ({subset}): {str(e)}")

    def _dataset_has_data(self, dataset: DatasetType) -> bool:
        if isinstance(dataset, (Dataset, DatasetDict)):
            return len(dataset) > 0
        elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
            return next(iter(dataset), None) is not None
        return False

    def _get_column_names(self, dataset: DatasetType) -> List[str]:
        if isinstance(dataset, Dataset):
            return dataset.column_names
        elif isinstance(dataset, DatasetDict):
            # Assuming all splits have the same columns, we'll use the first split
            first_split = next(iter(dataset.values()))
            return first_split.column_names if first_split else []
        elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
            first_item = next(iter(dataset), None)
            return list(first_item.keys()) if first_item else []
        return []

    def _get_dataset_size(self, dataset: DatasetType) -> str:
        if isinstance(dataset, (Dataset, DatasetDict)):
            return str(len(dataset))
        return "Unknown (IterableDataset)"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
