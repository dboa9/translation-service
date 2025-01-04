import logging
import unittest

from datasets import load_dataset
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestHuggingFaceDatasets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subsets = ["web_data", "comments", "stories", "doda", "transliteration"]
        cls.raw_datasets = {}
        cls.tokenizer = AutoTokenizer.from_pretrained("BounharAbdelaziz/Transliteration-Moroccan-Darija")

    def test_load_datasets(self):
        for subset in self.subsets:
            try:
                self.raw_datasets[subset] = load_dataset("atlasia/darija_english", subset)
                logger.info(f"Successfully loaded {subset} dataset")
                self.assertIsNotNone(self.raw_datasets[subset])
            except Exception as e:
                logger.error(f"Error loading {subset} dataset: {str(e)}")
                self.fail(f"Failed to load {subset} dataset")

    def test_dataset_structure(self):
        expected_features = {
            "web_data": ["english", "darija", "source"],
            "comments": ["id", "english", "darija", "source"],
            "stories": ["ChapterName", "ChapterLink", "Author", "Tags", "darija", "english", "chunk_id", "source"],
            "doda": ["id", "darija", "en"],
            "transliteration": ["darija_arabizi", "darija_arabic"]
        }

        for subset, features in expected_features.items():
            self.assertIn(subset, self.raw_datasets)
            dataset = self.raw_datasets[subset]["train"]
            self.assertEqual(set(dataset.features.keys()), set(features))

    def test_tokenization(self):
        max_length = 128

        def preprocess_function(examples, dataset_type):
            if dataset_type == "transliteration":
                input_text = examples["darija_arabizi"]
                target_text = examples["darija_arabic"]
            elif dataset_type == "doda":
                input_text = examples["darija"]
                target_text = examples["en"]
            else:
                input_text = examples["darija"]
                target_text = examples["english"]

            model_inputs = self.tokenizer(input_text, max_length=max_length, truncation=True, padding="max_length")
            with self.tokenizer.as_target_tokenizer():
                labels = self.tokenizer(target_text, max_length=max_length, truncation=True, padding="max_length")

            model_inputs["labels"] = labels["input_ids"]
            return model_inputs

        for subset, dataset in self.raw_datasets.items():
            try:
                tokenized_dataset = dataset["train"].map(
                    lambda x: preprocess_function(x, subset),
                    batched=True,
                    remove_columns=dataset["train"].column_names
                )
                logger.info(f"Successfully tokenized {subset} dataset")
                self.assertIsNotNone(tokenized_dataset)
                self.assertIn("input_ids", tokenized_dataset.features)
                self.assertIn("attention_mask", tokenized_dataset.features)
                self.assertIn("labels", tokenized_dataset.features)
            except Exception as e:
                logger.error(f"Error tokenizing {subset} dataset: {str(e)}")
                self.fail(f"Failed to tokenize {subset} dataset")

if __name__ == "__main__":
    unittest.main()
