import unittest
from pathlib import Path
import yaml
from typing import Union
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
import sys
import os

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, project_root)

from core.dataset.extended_dataset_validator import ExtendedDatasetValidator as NewExtendedDatasetValidator
from core.dataset.data_reader import DataReader
from core.dataset.parallel_loader import ParallelLoader
from core.dataset.config.data_paths import DataPaths
import logging

logger = logging.getLogger(__name__)

class MockIntegrationChecker:
    def check_integration(self, dataset, dataset_name, subset):
        return {"default": {"column_pair": {"integrated": True}}}

class TestNewComprehensiveDatasetValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project")
        cls.data_paths = DataPaths(base_dir=str(cls.base_dir))  # Convert Path to string
        cls.parallel_loader: ParallelLoader = ParallelLoader(cls.data_paths)
        cls.data_reader = DataReader(cls.base_dir)
        cls.config = cls.load_config()
        cls.dataset_validator = NewExtendedDatasetValidator(cls.config)
        cls.integration_checker = MockIntegrationChecker()

    @staticmethod
    def load_config():
        config_path = Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/config/dataset_loader_debug.yaml")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def test_all_datasets(self):
        for dataset_name, config in self.config['debug']['datasets'].items():
            logger.info(f"Testing dataset: {dataset_name}")
            for subset in config['subsets']:
                with self.subTest(dataset=dataset_name, subset=subset):
                    self._test_dataset_loading_and_validation(dataset_name, subset)

    def _test_dataset_loading_and_validation(self, dataset_name: str, subset: str):
        logger.info(f"Testing dataset loading and validation: {dataset_name}, subset: {subset}")
        
        # Test loading with DataReader
        try:
            dataset = self.data_reader.load_dataset(dataset_name, subset)
            self.assertIsNotNone(dataset)
            if dataset is not None:
                self._validate_and_check_integration(dataset, dataset_name, subset, "DataReader")
        except Exception as e:
            logger.error(f"Error loading dataset with DataReader: {e}")
            self.fail(f"DataReader failed to load dataset {dataset_name}/{subset}: {str(e)}")

        # Test loading with ParallelLoader
        try:
            dataset = self.parallel_loader.load_dataset(dataset_name, subset)
            self.assertIsNotNone(dataset)
            if dataset is not None:
                self._validate_and_check_integration(dataset, dataset_name, subset, "ParallelLoader")
        except Exception as e:
            logger.error(f"Error loading dataset with ParallelLoader: {e}")
            self.fail(f"ParallelLoader failed to load dataset {dataset_name}/{subset}: {str(e)}")

    def _validate_and_check_integration(self, dataset: Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict], dataset_name: str, subset: str, loader_type: str):
        # Validate dataset
        try:
            success, issues, stats = self.dataset_validator.validate_dataset(dataset, dataset_name, subset)
            self.assertTrue(success, f"Dataset validation failed for {dataset_name}/{subset} loaded with {loader_type}: {issues}")
            logger.info(f"Dataset validation successful for {dataset_name}/{subset} loaded with {loader_type}")
            logger.info(f"Validation stats: {stats}")
        except Exception as e:
            logger.error(f"Dataset validation failed for {dataset_name}/{subset} loaded with {loader_type}: {e}")
            self.fail(f"Dataset validation failed for {dataset_name}/{subset} loaded with {loader_type}: {str(e)}")

        # Check integration
        try:
            integration_results = self.integration_checker.check_integration(dataset, dataset_name, subset)
            self._assert_integration_success(integration_results, dataset_name, subset, loader_type)
        except Exception as e:
            logger.error(f"Integration check failed for {dataset_name}/{subset} loaded with {loader_type}: {e}")
            self.fail(f"Integration check failed for {dataset_name}/{subset} loaded with {loader_type}: {str(e)}")

    def _assert_integration_success(self, integration_results: dict, dataset_name: str, subset: str, loader_type: str):
        for split, results in integration_results.items():
            for column_pair, check_result in results.items():
                self.assertTrue(
                    check_result['integrated'],
                    f"Integration check failed for {column_pair} in {dataset_name}/{subset}/{split} loaded with {loader_type}"
                )

if __name__ == '__main__':
    unittest.main()
