#tests/unified_tests/test_enhanced_column_mapping.py

import logging
import sys
import unittest
from pathlib import Path
from typing import Union

from datasets import (
    Dataset,
    DatasetDict,
    IterableDataset,
    IterableDatasetDict,
    load_dataset,
)

# Add project root to Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from core.config_analysis.column_mapping_analyzer import ColumnMappingAnalyzer
from core.dataset.config.data_paths import DataPaths

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
        "subsets": ["sentences"],  # Removed submissions as it requires special handling
        "required_columns": {
            "sentences": ["darija", "eng", "darija_ar"]
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

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

class TestEnhancedColumnMapping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.base_dir = project_root
        cls.data_paths = DataPaths(str(cls.base_dir))
        cls.column_analyzer = ColumnMappingAnalyzer(cls.data_paths)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        cls.logger = logging.getLogger(__name__)

    def load_test_dataset(self, dataset_name: str, config: str) -> Dataset:
        """Handle dataset loading with special cases"""
        try:
            dataset = load_dataset(
                dataset_name, 
                config, 
                cache_dir=str(self.data_paths.cache_dir)
            )
            
            # Handle different dataset types
            if isinstance(dataset, DatasetDict):
                # Use the first split by default
                split_name = next(iter(dataset.keys()))
                dataset = dataset[split_name]
            elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
                self.logger.warning(f"Converting iterable dataset to regular dataset for {dataset_name}")
                dataset = Dataset.from_dict(next(iter(dataset)))
                
            self.logger.info(f"Successfully loaded dataset {dataset_name} ({config})")
            return dataset
            
        except Exception as e:
            self.logger.error(f"Error loading dataset {dataset_name} ({config}): {str(e)}")
            raise

    def test_all_datasets(self):
        """Test column mapping for all datasets"""
        failed_tests = []
        
        for dataset_name, config in DATASET_CONFIGS.items():
            for subset in config['subsets']:
                with self.subTest(dataset=dataset_name, config=subset):
                    try:
                        self.logger.info(f"Testing dataset {dataset_name} ({subset})")
                        dataset = self.load_test_dataset(dataset_name, subset)
                        
                        validation_result = self.column_analyzer.analyze_column_mapping(dataset_name, dataset, subset)
                        
                        if not validation_result["status"]:
                            error_msg = (
                                f"Column validation failed for {dataset_name} ({subset}): "
                                f"{validation_result['message']}"
                            )
                            self.logger.error(error_msg)
                            failed_tests.append((dataset_name, subset, error_msg))
                            continue
                            
                        self.logger.info(
                            f"Column mapping valid for {dataset_name} ({subset})"
                        )
                        
                    except Exception as e:
                        error_msg = f"Test failed for {dataset_name} ({subset}): {str(e)}"
                        self.logger.error(error_msg)
                        failed_tests.append((dataset_name, subset, error_msg))
                        continue

        # After all tests, report failures
        if failed_tests:
            failure_messages = "\n".join([
                f"{dataset} ({subset}): {error}"
                for dataset, subset, error in failed_tests
            ])
            self.fail(f"Some dataset validations failed:\n{failure_messages}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
