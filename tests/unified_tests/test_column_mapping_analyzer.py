#Do not REMOVE LOCATION OR FILE NAME COMMENTS, EDIT IF NEEDED BUT NO REMOVAL OF THESE KINDS OF COMMENTS
# tests/unified_tests/test_column_mapping_analyzer.py

import unittest
from unittest.mock import MagicMock
from core.config_analysis.column_mapping_analyzer import ColumnMappingAnalyzer
from core.dataset.config.data_paths import DataPaths
from datasets import Dataset

class TestColumnMappingAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_paths = DataPaths("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project")
        self.analyzer = ColumnMappingAnalyzer(self.data_paths)

    def test_analyze_column_mapping(self):
        mock_dataset = Dataset.from_dict({"english": ["Hello"], "darija": ["Salam"], "source": ["test"]})
        result = self.analyzer.analyze_column_mapping("atlasia/darija_english", mock_dataset, "web_data")
        self.assertEqual(result["status"], True)

    def test_preprocess_dataset(self):
        mock_dataset = Dataset.from_dict({"english": ["Hello"], "darija": ["Salam"], "source": ["test"]})
        preprocessed = self.analyzer.preprocess_dataset(mock_dataset, "atlasia/darija_english", "web_data")
        self.assertEqual(preprocessed, mock_dataset)  # Assuming no preprocessing is needed for this dataset

if __name__ == "__main__":
    unittest.main()
