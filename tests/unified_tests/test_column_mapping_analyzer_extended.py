import unittest
from unittest.mock import MagicMock
from core.config_analysis.column_validator_core import validate_columns
from core.dataset.config.data_paths import DataPaths
from datasets import Dataset
import yaml
from pathlib import Path

class TestColumnMappingAnalyzerExtended(unittest.TestCase):
    def setUp(self):
        self.data_paths = DataPaths("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project")
        self.config_path = Path(__file__).resolve().parent.parent.parent / 'config' / 'column_mapping.yaml'
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def get_required_columns(self, dataset_name, config_name):
        """Get required columns for a given dataset and config"""
        dataset_config = self.config['datasets'].get(dataset_name, {})
        if config_name == 'subsets':
            return dataset_config.get('subsets', [])
        elif config_name in ['required_columns', 'special_validation', 'multiple_columns_allowed']:
            return list(dataset_config.get(config_name, {}).keys())
        else:
            return dataset_config.get('required_columns', {}).get(config_name, [])

    def test_analyze_column_mapping_for_all_datasets(self):
        for dataset_name, dataset_configs in self.config['datasets'].items():
            for config_name in ['subsets', 'required_columns', 'special_validation', 'multiple_columns_allowed']:
                with self.subTest(f"Testing {dataset_name} - {config_name}"):
                    required_columns = self.get_required_columns(dataset_name, config_name)
                    if required_columns:
                        mock_dataset = Dataset.from_dict({col: ["test"] for col in required_columns})
                        result = validate_columns(mock_dataset, dataset_name, config_name)
                        self.assertEqual(result["status"], True, f"Column mapping analysis failed for {dataset_name} - {config_name}")
                    else:
                        print(f"No {config_name} found for dataset {dataset_name}")

    def test_preprocess_dataset_for_all_datasets(self):
        for dataset_name, dataset_configs in self.config['datasets'].items():
            for config_name in dataset_configs.get('subsets', []):
                with self.subTest(f"Testing preprocessing for {dataset_name} - {config_name}"):
                    required_columns = self.get_required_columns(dataset_name, config_name)
                    if required_columns:
                        mock_dataset = Dataset.from_dict({col: ["test"] for col in required_columns})
                        result = validate_columns(mock_dataset, dataset_name, config_name)
                        self.assertEqual(result["status"], True, f"Preprocessing failed for {dataset_name} - {config_name}")
                        self.assertEqual(set(result["columns"]), set(required_columns), 
                                         f"Preprocessed columns do not match required columns for {dataset_name} - {config_name}")
                    else:
                        print(f"No required columns found for dataset {dataset_name} config {config_name}")

if __name__ == "__main__":
    unittest.main()
