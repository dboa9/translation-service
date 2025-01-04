# File: test_atlasia_hf_loading.py
import os
import sys
from pathlib import Path
from typing import Any, Dict

from datasets import Dataset, DatasetDict, load_dataset


def setup_python_path():
    """Add project root to Python path."""
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..')
    )
    sys.path.insert(0, project_root)
    return project_root


# Set up Python path before imports
project_root = setup_python_path()

# Import project modules
from tests.unified_tests.hf_base_loader import HFBaseLoader, DataPaths  # noqa: E402


def test_atlasia_hf_loading(sample_size: float = 0.03) -> Dict[str, Any]:
    # Initialize loader
    base_dir = Path(project_root)
    data_paths = DataPaths(base_dir)
    loader = HFBaseLoader(data_paths)
    
    dataset_name = "atlasia/darija_english"
    subsets = ["web_data", "comments", "stories", "doda", "transliteration"]
    results = {}

    for subset in subsets:
        print(f"\nTesting subset: {subset}")
        try:
            # Load from Hugging Face
            hf_dataset = load_dataset(
                dataset_name,
                subset,
                split=f"train[:{int(sample_size*100)}%]"
            )
            
            # Load locally
            local_dataset = loader.load_dataset(dataset_name, subset)
            if local_dataset is None:
                raise ValueError("Failed to load local dataset")
            
            # Sample local dataset to match HF sample size
            local_dataset = local_dataset.select(
                range(int(len(local_dataset) * sample_size))
            )

            # Compare datasets
            hf_columns = set(getattr(hf_dataset, 'column_names', []))
            local_columns = set(getattr(local_dataset, 'column_names', []))
            assert hf_columns == local_columns, (
                f"Column mismatch in {subset}. "
                f"HF: {hf_columns}, Local: {local_columns}"
            )
            assert isinstance(hf_dataset, (Dataset, DatasetDict))
            assert isinstance(local_dataset, (Dataset, DatasetDict))
            assert len(hf_dataset) == len(local_dataset), (
                f"Length mismatch in {subset}. "
                f"HF: {len(hf_dataset)}, Local: {len(local_dataset)}"
            )

            results[subset] = {
                "status": "success",
                "columns": list(hf_columns),
                "sample_size": len(hf_dataset),
                "data_format": str(type(hf_dataset))
            }
            
            print("  Status: Success")
            print(f"  Columns: {', '.join(results[subset]['columns'])}")
            print(f"  Sample size: {results[subset]['sample_size']}")
            print(f"  Data format: {results[subset]['data_format']}")

        except Exception as e:
            results[subset] = {
                "status": "error",
                "error_message": str(e)
            }
            print("  Status: Error")
            print(f"  Error message: {str(e)}")

    return results


if __name__ == "__main__":
    results = test_atlasia_hf_loading()
    print("\nSummary of Results:")
    for subset, result in results.items():
        print(f"\n{subset}:")
        for key, value in result.items():
            print(f"  {key}: {value}")
