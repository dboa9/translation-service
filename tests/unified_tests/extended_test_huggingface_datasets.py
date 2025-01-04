import logging
import sys
import unittest
from pathlib import Path

import yaml
from datasets import load_dataset
from transformers import AutoTokenizer, TFAutoModelForSeq2SeqLM

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from tests.unified_tests.test_huggingface_datasets import TestHuggingFaceDatasetsMock


class ExtendedTestHuggingFaceDatasets(TestHuggingFaceDatasetsMock):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Set up additional logging
        cls.logger = logging.getLogger(__name__)
        cls.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        cls.logger.addHandler(handler)

        # Load tokenizer and model
        cls.model_checkpoint = "BounharAbdelaziz/Transliteration-Moroccan-Darija"
        try:
            cls.tokenizer = AutoTokenizer.from_pretrained(cls.model_checkpoint)
            cls.model = TFAutoModelForSeq2SeqLM.from_pretrained(cls.model_checkpoint)
            cls.logger.info(f"Successfully loaded tokenizer and model from {cls.model_checkpoint}")
        except Exception as e:
            cls.logger.error(f"Error loading tokenizer or model: {e}")
            raise

        # Load column mapping configuration
        config_path = project_root / 'config' / 'column_mapping.yaml'
        with open(config_path, 'r') as f:
            cls.config = yaml.safe_load(f)

        # Set up dataset configurations
        cls.dataset_name = "atlasia/darija_english"
        cls.subsets = cls.config['datasets'][cls.dataset_name]['subsets']
        cls.raw_datasets = {}

    def get_column_names(self, subset):
        required_columns = self.config['datasets'][self.dataset_name]['required_columns'][subset]
        darija_col = next(col for col in required_columns if col in self.config['column_types']['darija'])
        english_col = next(col for col in required_columns if col in self.config['column_types']['english'])
        return darija_col, english_col

    def preprocess_function(self, examples, subset):
        self.logger.info(f"Preprocessing dataset: {subset}")
        max_input_length = 128
        max_target_length = 128

        darija_col, english_col = self.get_column_names(subset)

        if subset == "transliteration":
            input_text = examples["darija_arabizi"]
            target_text = examples["darija_arabic"]
            language_id = 1  # Custom ID for Darija
        else:
            input_text = examples[darija_col]
            target_text = examples[english_col]
            language_id = 0  # Custom ID for English

        try:
            # Tokenize input
            input_ids = [self.tokenizer.encode(text, add_special_tokens=True, max_length=max_input_length, truncation=True, padding='max_length') for text in input_text]
            input_ids_with_lang = [[language_id] + ids for ids in input_ids]

            # Tokenize target
            with self.tokenizer.as_target_tokenizer():
                labels = [self.tokenizer.encode(text, add_special_tokens=True, max_length=max_target_length, truncation=True, padding='max_length') for text in target_text]

            # Create attention masks
            attention_mask = [[1 if token != self.tokenizer.pad_token_id else 0 for token in seq] for seq in input_ids_with_lang]

            model_inputs = {
                "input_ids": input_ids_with_lang,
                "attention_mask": attention_mask,
                "labels": labels
            }

            self.logger.info(f"Preprocessed {len(input_text)} examples for {subset}")
            return model_inputs
        except Exception as e:
            self.logger.error(f"Error in preprocessing function for {subset}: {e}")
            raise

    def test_load_and_preprocess_datasets(self):
        self.logger.info("Starting test_load_and_preprocess_datasets")
        for subset in self.subsets:
            with self.subTest(subset=subset):
                try:
                    # Load dataset
                    self.raw_datasets[subset] = load_dataset(self.dataset_name, subset)
                    self.assertIsNotNone(self.raw_datasets[subset], f"Failed to load dataset {subset}")
                    self.logger.info(f"Successfully loaded dataset: {subset}")
                    print(f"Dataset {subset}: {self.raw_datasets[subset]}")

                    # Preprocess dataset
                    if "train" in self.raw_datasets[subset]:
                        tokenized_dataset = self.raw_datasets[subset]["train"].map(
                            lambda x: self.preprocess_function(x, subset),
                            batched=True
                        )
                        self.assertIsNotNone(tokenized_dataset, f"Failed to preprocess dataset {subset}")
                        self.logger.info(f"Successfully preprocessed dataset: {subset}")
                        print(f"Preprocessed dataset {subset} (first 2 examples): {tokenized_dataset[:2]}")
                    else:
                        self.logger.warning(f"No train split found in {subset} dataset.")
                except Exception as e:
                    self.logger.error(f"Error processing dataset {subset}: {e}")
                    self.fail(f"Failed to process dataset {subset}: {e}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
