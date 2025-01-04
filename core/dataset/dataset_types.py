from typing import Tuple, Any, Union, Dict, Optional, List, cast
import logging
from datasets import Dataset, IterableDataset, DatasetDict, IterableDatasetDict

logger = logging.getLogger(__name__)

DatasetType = Union[Dataset, IterableDataset, DatasetDict, IterableDatasetDict, Dict[str, Any]]

def get_dataset_types() -> Tuple[Optional[Any], ...]:
    try:
        from datasets import load_dataset
        return (load_dataset, Dataset, IterableDataset, DatasetDict, IterableDatasetDict)
    except ImportError as e:
        logger.error(f"Failed to import datasets: {e}")
        return (None, None, None, None, None)

(
    load_dataset, Dataset, IterableDataset,
    DatasetDict, IterableDatasetDict
) = get_dataset_types()

def ensure_dataset(data: Any) -> Any:  # type: ignore
    """Convert various dataset types to Dataset."""
    if Dataset is None or IterableDataset is None or DatasetDict is None or IterableDatasetDict is None:
        raise ImportError("Failed to import necessary dataset types")
    
    if isinstance(data, IterableDataset):
        return Dataset.from_dict(dict(next(iter(data))))
    if isinstance(data, IterableDatasetDict):
        first_split = next(iter(data.values()))
        return Dataset.from_dict(dict(next(iter(first_split))))
    if isinstance(data, DatasetDict):
        first_split = next(iter(data.values()))
        if isinstance(first_split, Dataset):
            return first_split
        raise ValueError("Invalid dataset format")
    if isinstance(data, Dataset):
        return data
    if isinstance(data, dict):
        return Dataset.from_dict(data)
    raise ValueError("Invalid dataset format")

def get_dataset_columns(dataset: Optional[DatasetType]) -> List[str]:
    if dataset is None:
        return []
    if Dataset is None or IterableDataset is None or DatasetDict is None or IterableDatasetDict is None:
        raise ImportError("Failed to import necessary dataset types")
    
    if isinstance(dataset, (Dataset, DatasetDict)):
        columns = dataset.column_names  # type: ignore
        if isinstance(columns, dict):
            return list(set().union(*columns.values()))
        return columns or []
    if isinstance(dataset, IterableDataset):
        return list(dataset.features.keys()) if hasattr(dataset, 'features') and dataset.features is not None else []  # type: ignore
    if isinstance(dataset, IterableDatasetDict):
        first_split = next(iter(dataset.values()))  # type: ignore
        return list(first_split.features.keys()) if hasattr(first_split, 'features') and first_split.features is not None else []  # type: ignore
    if isinstance(dataset, dict):
        return list(dataset.keys())
    return []

__all__ = [
    'load_dataset', 'Dataset', 'IterableDataset',
    'DatasetDict', 'IterableDatasetDict', 'DatasetType',
    'ensure_dataset', 'get_dataset_columns'
]

if __name__ == "__main__":
    print("Testing dataset_types.py")
    print(f"load_dataset: {load_dataset}")
    print(f"Dataset: {Dataset}")
    print(f"IterableDataset: {IterableDataset}")
    print(f"DatasetDict: {DatasetDict}")
    print(f"IterableDatasetDict: {IterableDatasetDict}")
    print(f"DatasetType: {DatasetType}")
    print(f"ensure_dataset: {ensure_dataset}")
    print(f"get_dataset_columns: {get_dataset_columns}")
