import unittest
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from core.dataset.hf_base_loader_wrapper import HFBaseLoaderWrapper

class TestDatasetLoading(unittest.TestCase):
    def setUp(self):
        self.loader = HFBaseLoaderWrapper()

    def test_dataset_loading(self, dataset='imomayiz/darija-english', subset='sentences'):
        dataset_name = f"{dataset}/{subset}"
        try:
            dataset = self.loader.load_dataset(dataset, subset)
            self.assertIsNotNone(dataset, f"Dataset is None for {dataset_name}")
            
            if isinstance(dataset, (Dataset, DatasetDict)):
                if isinstance(dataset, Dataset):
                    self.assertTrue(len(dataset) > 0, f"Dataset is empty for {dataset_name}")
                else:  # DatasetDict
                    self.assertTrue(any(len(split) > 0 for split in dataset.values()), 
                                    f"All splits are empty for {dataset_name}")
                    
                    # Check for any available split, not just 'train'
                    available_splits = list(dataset.keys())
                    if not available_splits:
                        print(f"Warning: No splits found in {dataset_name}")
                    else:
                        first_split = available_splits[0]
                        actual_columns = dataset[first_split].column_names
                        print(f"Columns for {dataset_name} (split: {first_split}): {actual_columns}")
                        
            elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
                # For iterable datasets, we can't check the length directly
                if isinstance(dataset, IterableDataset):
                    self.assertTrue(next(iter(dataset), None) is not None, 
                                    f"Iterable dataset is empty for {dataset_name}")
                else:  # IterableDatasetDict
                    self.assertTrue(any(next(iter(split), None) is not None for split in dataset.values()), 
                                    f"All iterable splits are empty for {dataset_name}")
            else:
                self.fail(f"Unexpected dataset type for {dataset_name}")
        except Exception as e:
            self.fail(f"Error loading or validating {dataset_name}: {str(e)}")

if __name__ == '__main__':
    unittest.main()
