import json
import sys
import unittest
from pathlib import Path

import pandas as pd
from datasets import Dataset

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from core.base_loader import BaseLoader
from core.config_handler import ConfigHandler


class TestHuggingFaceDatasetsMock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = project_root
        cls.config_handler = ConfigHandler(str(cls.base_dir / 'config' / 'dataset_loader_debug.yaml'))
        cls.base_loader = BaseLoader(cls.config_handler)
        cls.mock_data_dir = cls.base_dir / "test_data_sample"

    def load_mock_dataset(self, dataset_name, subset):
        # Check for CSV file
        csv_file = self.mock_data_dir / dataset_name / f"{subset}_sample.csv"
        if not csv_file.exists():
            csv_file = self.mock_data_dir / dataset_name / f"{dataset_name.split('/')[-1]}_{subset}_sample.csv"

        if csv_file.exists():
            df = pd.read_csv(csv_file)
            return Dataset.from_pandas(df)

        # Check for JSON file
        json_file = self.mock_data_dir / dataset_name / "data" / "train-00000-of-00001-parquet.json"
        if json_file.exists():
            with open(json_file, 'r') as f:
                metadata = json.load(f)
            
            # Create a sample dataset based on the metadata
            features = metadata.get('features', {})
            sample_data = {
                feature: ['Sample data'] * 5 for feature in features.keys()
            }
            return Dataset.from_dict(sample_data)

        raise FileNotFoundError(f"Mock data file not found for {dataset_name} - {subset}")

    def test_atlasia_darija_english(self):
        dataset_name = "atlasia/darija_english"
        subsets = ["web_data", "comments", "stories", "doda", "transliteration"]
        for subset in subsets:
            with self.subTest(subset=subset):
                dataset = self.load_mock_dataset(dataset_name, subset)
                self.assertIsNotNone(dataset, f"Failed to load mock dataset {dataset_name} - {subset}")
                self.assertGreater(len(dataset), 0, f"Dataset {dataset_name} - {subset} is empty")

    def test_imomayiz_darija_english(self):
        dataset_name = "imomayiz/darija-english"
        subset = "sentences"
        dataset = self.load_mock_dataset(dataset_name, subset)
        self.assertIsNotNone(dataset, f"Failed to load mock dataset {dataset_name} - {subset}")
        self.assertGreater(len(dataset), 0, f"Dataset {dataset_name} - {subset} is empty")

    def test_mad_darija_bridge(self):
        dataset_name = "M-A-D/DarijaBridge"
        subset = "default"
        dataset = self.load_mock_dataset(dataset_name, subset)
        self.assertIsNotNone(dataset, f"Failed to load mock dataset {dataset_name}")
        self.assertGreater(len(dataset), 0, f"Dataset {dataset_name} is empty")

    def test_bounhar_english_to_moroccan_darija(self):
        dataset_name = "BounharAbdelaziz/English-to-Moroccan-Darija"
        subset = "default"
        dataset = self.load_mock_dataset(dataset_name, subset)
        self.assertIsNotNone(dataset, f"Failed to load mock dataset {dataset_name}")
        self.assertGreater(len(dataset), 0, f"Dataset {dataset_name} is empty")

if __name__ == "__main__":
    unittest.main()
