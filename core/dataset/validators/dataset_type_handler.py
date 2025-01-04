from typing import Any, Callable, Dict, Optional
from datasets import Dataset

def handle_dataset_type(dataset: Any, dataset_name: str, config: Optional[str], validate_func: Callable) -> Dict[str, Any]:
    if isinstance(dataset, Dataset):
        # If it's a Dataset object, we treat it as a single split
        return validate_func(dataset, dataset_name, config)
    elif isinstance(dataset, dict):
        # If it's a dictionary, we iterate over its values
        results = {}
        for split_name, split_data in dataset.items():
            split_result = validate_func(split_data, dataset_name, config, split_name)
            results[split_name] = split_result
        return results
    else:
        raise ValueError(f"Unsupported dataset type: {type(dataset)}")
