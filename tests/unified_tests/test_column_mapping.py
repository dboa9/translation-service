# File: test_column_mapping.py
# Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/tests/unified_tests/test_column_mapping.py
# Author: dboa9 (danielalchemy9@gmail.com)
# Date: 2024-11-16

import unittest
import logging
import os
from pathlib import Path
from datasets import load_dataset, Dataset
import pandas as pd
import json

from core.dataset.validators.column_validator import ColumnValidator
from core.dataset.config.data_paths import DataPaths
from core.dataset.dataset_types import DatasetType

DATASET_CONFIGS = {
    "atlasia/darija_english": {
        "subsets": ["web_data", "comments", "stories", "doda", "transliteration"],
        "required_columns": {
            "web_data": ["darija", "english", "source"],
            "comments": ["id", "english", "darija", "source"],
            "stories": ["ChapterName", "darija", "english", "chunk_id"],
            "doda": ["id", "darija", "en"],
            "transliteration": ["darija_arabizi", "darija_arabic"]
        }
    },
    "imomayiz/darija-english": {
        "subsets": ["sentences", "submissions"],
        "required_columns": {
            "sentences": ["darija", "eng", "darija_ar"],
            "submissions": ["darija", "eng", "darija_ar", "timestamp"]
        }
    },
    "M-A-D/DarijaBridge": {
        "subsets": ["default"],
        "required_columns": {
            "default": ["sentence", "translation", "translated", "corrected", "correction", "quality", "metadata"]
        }
    },
    "BounharAbdelaziz/English-to-Moroccan-Darija": {
        "subsets": ["default"],
        "required_columns": {
            "default": ["english", "darija", "includes_arabizi"]
        }
    }
}

class TestColumnMapping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.base_dir = Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project")
        cls.validator = ColumnValidator(str(cls.base_dir))  # Convert Path to string
        cls.data_paths = DataPaths(str(cls.base_dir))  # Convert Path to string
        
        logging.basicConfig(level=logging.INFO)
        cls.logger = logging.getLogger(__name__)

    def load_test_dataset(self, dataset_name: str, config: str) -> DatasetType:
        """Handle dataset loading with special cases"""
        try:
            if dataset_name == "imomayiz/darija-english" and config == "submissions":
                # Special handling for imomayiz submissions
                return self._load_imomayiz_submissions()
            
            return load_dataset(dataset_name, config, cache_dir=str(self.data_paths.cache_dir))
        except Exception as e:
            self.logger.error(f"Error loading dataset {dataset_name} ({config}): {str(e)}")
            raise

    def _load_imomayiz_submissions(self) -> Dataset:
        """Special handling for imomayiz submissions with parser error"""
        submissions_path = self.data_paths.get_dataset_test_path("imomayiz/darija-english") / "submissions"
        
        # Load and parse JSON files manually
        data = []
        for json_file in submissions_path.glob("*.json"):
            try:
                with open(json_file) as f:
                    submission = json.load(f)
                    # Extract required fields
                    data.append({
                        "darija": submission.get("darija", ""),
                        "eng": submission.get("eng", ""),
                        "darija_ar": submission.get("darija_ar", ""),
                        "timestamp": submission.get("timestamp", "")
                    })
            except Exception as e:
                self.logger.warning(f"Error parsing {json_file}: {str(e)}")
                continue
                
        return Dataset.from_pandas(pd.DataFrame(data))

    def test_all_datasets(self):
        """Test column mapping for all datasets"""
        for dataset_name, config in DATASET_CONFIGS.items():
            for subset in config['subsets']:
                with self.subTest(dataset=dataset_name, config=subset):
                    try:
                        dataset = self.load_test_dataset(dataset_name, subset)
                        self.assertTrue(
                            self.validator.validate_dataset_dict(dataset_name, dataset, subset),
                            f"Column validation failed for {dataset_name} ({subset})"
                        )
                        self.logger.info(f"Column mapping valid for {dataset_name} ({subset})")
                    except Exception as e:
                        self.logger.error(f"Test failed for {dataset_name} ({subset}): {str(e)}")
                        raise

if __name__ == "__main__":
    unittest.main(verbosity=2)
