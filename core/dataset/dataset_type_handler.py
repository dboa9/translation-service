# File: dataset_type_handler.py
from typing import Union, List, Dict, Any

from datasets import (
    Dataset, IterableDataset, DatasetDict, IterableDatasetDict
)


class DatasetTypeHandler:
    @staticmethod
    def get_column_names(
        dataset: Union[Dataset, IterableDataset, DatasetDict,
                       IterableDatasetDict]
    ) -> List[str]:
        """Get column names from the dataset"""
        if isinstance(dataset, Dataset):
            return dataset.column_names
        elif isinstance(dataset, DatasetDict):
            # Assume all splits have the same columns, use the first split
            first_split = next(iter(dataset.values()))
            return first_split.column_names
        elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
            # For iterable datasets, infer column names from first example
            try:
                if isinstance(dataset, IterableDatasetDict):
                    first_split = next(iter(dataset.values()))
                else:
                    first_split = dataset
                first_example = next(iter(first_split))
                return list(first_example.keys())
            except StopIteration:
                return []
        else:
            return []

    @staticmethod
    def get_dataset_info(
        dataset: Union[Dataset, IterableDataset, DatasetDict,
                       IterableDatasetDict]
    ) -> Dict[str, Any]:
        """Get information about the dataset"""
        info: Dict[str, Any] = {"type": type(dataset).__name__}

        if isinstance(dataset, Dataset):
            info["num_rows"] = len(dataset)
            info["columns"] = dataset.column_names
        elif isinstance(dataset, DatasetDict):
            info["splits"] = {}
            for split_name, split_dataset in dataset.items():
                info["splits"][split_name] = {
                    "num_rows": len(split_dataset),
                    "columns": split_dataset.column_names
                }
        elif isinstance(dataset, IterableDataset):
            info["columns"] = DatasetTypeHandler.get_column_names(dataset)
        elif isinstance(dataset, IterableDatasetDict):
            info["splits"] = list(dataset.keys())
            info["columns"] = DatasetTypeHandler.get_column_names(dataset)

        return info

# The file ends here
