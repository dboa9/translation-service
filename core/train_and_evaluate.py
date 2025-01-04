# File: train_and_evaluate.py
import evaluate
import numpy as np
from datasets import Dataset


class TranslationTrainer:
    def __init__(self, model=None, tokenizer=None, max_length=128):
        self.model = model
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.metric = evaluate.load("sacrebleu")

    def prepare_dataset(self, dataset: Dataset) -> Dataset:
        """Prepare the dataset for training."""
        if self.tokenizer is None:
            raise ValueError("Tokenizer is not initialized.")

        def tokenize_function(examples):
            return self.tokenizer(
                examples["source"],
                examples["target"],
                max_length=self.max_length,
                truncation=True,
                padding="max_length"
            )

        return dataset.map(tokenize_function, batched=True)

    def initialize_model(self):
        """Initialize the model and tokenizer."""
        if self.model is None:
            raise ValueError("Model is not initialized.")
        
        if not hasattr(self.model, 'generation_config'):
            raise ValueError(
                "Model does not have generation_config attribute."
            )

        self.model.generation_config.max_length = self.max_length
        # Example value, adjust as needed
        self.model.generation_config.num_beams = 4

    def compute_metrics(self, eval_pred):
        if self.tokenizer is None:
            raise ValueError("Tokenizer is not initialized.")

        predictions, labels = eval_pred
        decoded_preds = self.tokenizer.batch_decode(
            predictions, skip_special_tokens=True
        )
        labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
        decoded_labels = self.tokenizer.batch_decode(
            labels, skip_special_tokens=True
        )

        result = self.metric.compute(
            predictions=decoded_preds, references=decoded_labels
        )
        return {"bleu": result["score"]}

    def train(self, train_dataset: Dataset, eval_dataset: Dataset):
        if self.model is None or self.tokenizer is None:
            raise ValueError(
                "Model and tokenizer must be initialized before training."
            )

        # ... (rest of the training code)

    def evaluate(self, test_dataset: Dataset):
        if self.model is None or self.tokenizer is None:
            raise ValueError(
                "Model and tokenizer must be initialized before evaluation."
            )

        # ... (rest of the evaluation code)

# ... (rest of the file content)
