import unittest
import logging
from datasets import load_dataset
from transformers import AutoTokenizer
from core.dataset.config.data_paths import DataPaths
from core.config_analysis.column_mapping_analyzer import ColumnMappingAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMinimal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_configs = {
            "BounharAbdelaziz/English-to-Moroccan-Darija": None,
            "M-A-D/DarijaBridge": None,
            "atlasia/darija_english": "web_data",
            "imomayiz/darija-english": "sentences"
        }
        cls.tokenizer = AutoTokenizer.from_pretrained("BounharAbdelaziz/Transliteration-Moroccan-Darija")
        cls.data_paths = DataPaths(base_dir="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project")
        cls.column_analyzer = ColumnMappingAnalyzer(cls.data_paths)
        cls.datasets = {}

    def test_import(self):
        self.assertTrue(True, "This test should always pass")

    def test_tokenizer_loading(self):
        try:
            self.assertIsNotNone(self.tokenizer, "Tokenizer should not be None")
            logger.info("Tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {str(e)}")
            self.fail(f"Tokenizer loading failed: {str(e)}")

    def test_dataset_loading(self):
        for dataset_name, config in self.dataset_configs.items():
            with self.subTest(dataset=dataset_name):
                try:
                    if config:
                        dataset = load_dataset(dataset_name, config)
                    else:
                        dataset = load_dataset(dataset_name)
                    self.assertIsNotNone(dataset, f"Dataset {dataset_name} should not be None")
                    logger.info(f"Dataset {dataset_name} loaded successfully")
                    logger.info(f"Dataset structure: {dataset}")
                    self.datasets[dataset_name] = dataset
                except Exception as e:
                    logger.error(f"Failed to load dataset {dataset_name}: {str(e)}")
                    self.fail(f"Dataset {dataset_name} loading failed: {str(e)}")

    def test_column_mapping(self):
        for dataset_name, config in self.dataset_configs.items():
            with self.subTest(dataset=dataset_name):
                logger.info(f"Testing column mapping for dataset: {dataset_name} with config: {config}")
                mapping_result = self.column_analyzer.analyze_column_mapping(dataset_name, config)
                logger.info(f"Column mapping analysis result for {dataset_name}: {mapping_result}")
                self.assertTrue(mapping_result, f"Column mapping analysis failed for {dataset_name}")

if __name__ == '__main__':
    unittest.main()
