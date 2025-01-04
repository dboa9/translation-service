from typing import Optional, Union
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from core.dataset.dataset_wrapper import DatasetWrapper

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

class DatasetWrapperAdapter:
    def __init__(self, base_dir: str):
        self.dataset_wrapper = DatasetWrapper(base_dir)

    def load_and_validate_dataset(self, dataset_name: str, subset: str) -> Optional[DatasetType]:
        dataset = self.dataset_wrapper.load_and_validate_dataset(dataset_name, subset)
        
        if dataset is None:
            return None

        # Handle IterableDataset and IterableDatasetDict
        if isinstance(dataset, IterableDataset):
            return self._convert_iterable_dataset(dataset)
        elif isinstance(dataset, IterableDatasetDict):
            return self._convert_iterable_dataset_dict(dataset)
        
        return dataset

    def _convert_iterable_dataset(self, dataset: IterableDataset) -> Dataset:
        # Convert IterableDataset to Dataset
        data = list(dataset)
        if not data:
            return Dataset.from_dict({})
        return Dataset.from_dict({k: [d[k] for d in data] for k in data[0].keys()})

    def _convert_iterable_dataset_dict(self, dataset: IterableDatasetDict) -> DatasetDict:
        # Convert IterableDatasetDict to DatasetDict
        return DatasetDict({k: self._convert_iterable_dataset(v) for k, v in dataset.items()})
