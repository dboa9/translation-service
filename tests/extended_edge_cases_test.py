import unittest
from core.config_analysis.column_validator_core import validate_columns
from datasets import Dataset

class TestExtendedEdgeCases(unittest.TestCase):
    def test_empty_dataset(self):
        empty_dataset = Dataset.from_dict({})
        result = validate_columns(empty_dataset, "test_dataset", "empty_config")
        self.assertFalse(result["status"])

    def test_missing_required_column(self):
        dataset = Dataset.from_dict({"col1": [1, 2, 3]})
        result = validate_columns(dataset, "test_dataset", "missing_column_config")
        self.assertFalse(result["status"])

    def test_extra_columns(self):
        dataset = Dataset.from_dict({"required_col": [1, 2, 3], "extra_col": [4, 5, 6]})
        result = validate_columns(dataset, "test_dataset", "extra_column_config")
        self.assertTrue(result["status"])

    def test_mixed_data_types(self):
        dataset = Dataset.from_dict({"col1": [1, "two", 3.0]})
        result = validate_columns(dataset, "test_dataset", "mixed_types_config")
        self.assertTrue(result["status"])

    def test_large_dataset(self):
        large_dataset = Dataset.from_dict({"col1": list(range(1000000))})
        result = validate_columns(large_dataset, "test_dataset", "large_dataset_config")
        self.assertTrue(result["status"])

if __name__ == "__main__":
    unittest.main()
