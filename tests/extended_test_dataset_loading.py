import unittest
import sys
from pathlib import Path
import io
import contextlib
import traceback

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tests.test_dataset_loading import TestDatasetLoading
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

class ExtendedTestDatasetLoading(TestDatasetLoading):
    def setUp(self):
        # Capture the debug output from core.dataset.__init__.py
        debug_output = io.StringIO()
        with contextlib.redirect_stdout(debug_output):
            try:
                import core.dataset
                print(f"core.dataset module successfully imported")
                print(f"core.dataset.__file__: {core.dataset.__file__}")
                print(f"Contents of core.dataset:")
                for item in dir(core.dataset):
                    print(f"  {item}")
                
                from core.dataset import HFBaseLoaderWrapper
                self.loader = HFBaseLoaderWrapper()
                print("HFBaseLoaderWrapper successfully imported and instantiated")
            except ImportError as e:
                print(f"Error importing HFBaseLoaderWrapper: {e}")
                print(f"Traceback:")
                traceback.print_exc()
                print(f"Current sys.path: {sys.path}")
                print(f"Project root: {project_root}")
                print(f"Contents of core/dataset directory:")
                for item in Path(project_root / 'core' / 'dataset').iterdir():
                    print(f"  {item}")
                raise

        # Print the captured debug output
        print("Debug output:")
        print(debug_output.getvalue())

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
                    
                    # Check for 'train' split, but don't fail if it's missing
                    if 'train' not in dataset:
                        print(f"Warning: 'train' split not found in {dataset_name}")
                    else:
                        actual_columns = dataset['train'].column_names
                        print(f"Columns for {dataset_name}: {actual_columns}")
                        
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
