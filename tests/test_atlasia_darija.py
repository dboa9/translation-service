import unittest
from core.dataset_loader import load_dataset_to_dataframe
from core.validation_utils import validate_dataset

class TestAtlasiaDarija(unittest.TestCase):
    def test_atlasia_darija_english(self):
        configs = ["web_data", "comments", "stories", "doda", "transliteration"]
        for config in configs:
            with self.subTest(config=config):
                df = load_dataset_to_dataframe("atlasia/darija_english", config)
                validate_dataset(df, "atlasia/darija_english", config)
                self.assertIsNotNone(df)
                self.assertGreater(len(df), 0)
