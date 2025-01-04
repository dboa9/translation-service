from typing import Any, Dict, List, Optional
from datasets import Dataset, DatasetDict

class DatasetValidator:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def validate_dataset(self, dataset: Dataset, dataset_name: str, subset: str) -> bool:
        if isinstance(dataset, DatasetDict):
            for split, split_dataset in dataset.items():
                if not self._validate_split(split_dataset, dataset_name, subset, split):
                    return False
        else:
            if not self._validate_split(dataset, dataset_name, subset, "default"):
                return False
        return True

    def _validate_split(self, split_dataset: Dataset, dataset_name: str, subset: str, split: str) -> bool:
        return self._validate_columns(split_dataset, dataset_name, subset, split)

    def _validate_columns(self, split_dataset: Dataset, dataset_name: str, subset: str, split: str) -> bool:
        try:
            subset_config = self.config.get('datasets', {}).get(dataset_name, {}).get(subset, {})
            expected_columns = subset_config.get('columns', [])
            
            if not expected_columns:
                print(f"Warning: No column configuration found for {dataset_name}/{subset}. Skipping column validation.")
                return True

            actual_columns = split_dataset.column_names
            missing_columns = set(expected_columns) - set(actual_columns)
            
            if missing_columns:
                print(f"Error: Missing columns in {dataset_name}/{subset}/{split}: {missing_columns}")
                return False
            
            return True
        except Exception as e:
            print(f"Error validating columns for {dataset_name}/{subset}/{split}: {str(e)}")
            return False
