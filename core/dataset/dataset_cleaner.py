# File: dataset_cleaner.py
from typing import Union

from datasets import (
    Dataset, DatasetDict, IterableDataset, IterableDatasetDict
)


class DatasetCleaner:
    @staticmethod
    def remove_empty_columns(
        dataset: Union[Dataset, DatasetDict, IterableDataset,
                       IterableDatasetDict]
    ) -> Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]:
        """Remove columns with empty names"""
        if isinstance(dataset, Dataset):
            return dataset.remove_columns(
                [col for col in dataset.column_names if not col]
            )
        elif isinstance(dataset, DatasetDict):
            return DatasetDict({
                k: DatasetCleaner.remove_empty_columns(v)
                for k, v in dataset.items()
            })
        elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
            # IterableDataset and IterableDatasetDict don't support
            # column removal
            return dataset
        else:
            return dataset

    @staticmethod
    def remove_empty_rows(
        dataset: Union[Dataset, DatasetDict, IterableDataset,
                       IterableDatasetDict]
    ) -> Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]:
        """Remove rows where all values are empty or None"""
        def is_row_empty(example):
            return not any(v for v in example.values() if v)

        if isinstance(dataset, Dataset):
            return dataset.filter(lambda x: not is_row_empty(x))
        elif isinstance(dataset, DatasetDict):
            return DatasetDict({
                k: DatasetCleaner.remove_empty_rows(v)
                for k, v in dataset.items()
            })
        elif isinstance(dataset, IterableDataset):
            return dataset.filter(lambda x: not is_row_empty(x))
        elif isinstance(dataset, IterableDatasetDict):
            return IterableDatasetDict({
                k: v.filter(lambda x: not is_row_empty(x))
                for k, v in dataset.items()
            })
        else:
            return dataset

    @staticmethod
    def clean_dataset(
        dataset: Union[Dataset, DatasetDict, IterableDataset,
                       IterableDatasetDict]
    ) -> Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]:
        """Remove empty columns and rows from the dataset"""
        cleaned = DatasetCleaner.remove_empty_columns(dataset)
        return DatasetCleaner.remove_empty_rows(cleaned)

# The file ends here
