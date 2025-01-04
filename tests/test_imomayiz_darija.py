import sys
import unittest
from pathlib import Path
from typing import Any, Callable

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

from core.dataset.dataset_validator import DatasetValidator
from core.dataset.hf_base_loader_wrapper import HFBaseLoaderWrapper


class TestImomayizDarija(unittest.TestCase):
    def setUp(self):
        self.loader = HFBaseLoaderWrapper()
        self.validator = DatasetValidator(config={})  # Provide an empty config

    def call_method_safely(self, method: Callable[..., Any], **kwargs: Any) -> Any:
        params = method.__code__.co_varnames[:method.__code__.co_argcount]
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in params}
        return method(**filtered_kwargs)

    def test_imomayiz_darija_english(self):
        dataset_name = "imomayiz/darija-english"
        configs = ["sentences"]  # Removed 'submissions' as it's not available
        
        for config in configs:
            with self.subTest(config=config):
                try:
                    # Load the dataset
                    dataset = self.call_method_safely(
                        self.loader.load_dataset,
                        dataset_name=dataset_name,
                        subset=config
                    )
                    self.assertIsNotNone(dataset, f"Dataset is None for config: {config}")

                    # Validate the dataset structure
                    validation_result = self.call_method_safely(
                        self.validator.validate_dataset,
                        dataset=dataset,
                        dataset_name=dataset_name,
                        subset=config
                    )
                    self.assertTrue(validation_result, f"Validation failed for dataset: {dataset_name}/{config}")
                    
                    if isinstance(dataset, (Dataset, DatasetDict)):
                        if isinstance(dataset, Dataset):
                            self.assertTrue(len(dataset) > 0, f"Dataset is empty for config: {config}")
                            actual_columns = dataset.column_names
                        else:  # DatasetDict
                            self.assertTrue(any(len(split) > 0 for split in dataset.values()), 
                                            f"All splits are empty for config: {config}")
                            # Check for 'train' split, but don't fail if it's missing
                            if 'train' not in dataset:
                                print(f"Warning: 'train' split not found in {dataset_name}/{config}")
                                actual_columns = next(iter(dataset.values())).column_names
                            else:
                                actual_columns = dataset['train'].column_names
                        
                        print(f"Columns for {dataset_name}/{config}: {actual_columns}")
                            
                    elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
                        # For iterable datasets, we can't check the length directly
                        if isinstance(dataset, IterableDataset):
                            self.assertTrue(next(iter(dataset), None) is not None, 
                                            f"Iterable dataset is empty for config: {config}")
                        else:  # IterableDatasetDict
                            self.assertTrue(any(next(iter(split), None) is not None for split in dataset.values()), 
                                            f"All iterable splits are empty for config: {config}")
                    else:
                        self.fail(f"Unexpected dataset type for config: {config}")
                except Exception as e:
                    self.fail(f"Error processing {dataset_name}/{config}: {str(e)}")

if __name__ == '__main__':
    unittest.main()
