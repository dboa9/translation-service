import logging
from datasets import load_dataset, Dataset, DatasetDict, IterableDataset, IterableDatasetDict
import pandas as pd
from typing import Union, Iterator

logger = logging.getLogger(__name__)

def load_dataset_to_dataframe(dataset_name: str, config: str) -> pd.DataFrame:
    try:
        dataset = load_dataset(dataset_name, config)
        return dataset_to_dataframe(dataset)
    except Exception as e:
        logger.error(f"Failed to load dataset {dataset_name} (config: {config})")
        logger.error(f"Error: {str(e)}")
        raise

def dataset_to_dataframe(dataset: Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict, pd.DataFrame, Iterator[pd.DataFrame]]) -> pd.DataFrame:
    if isinstance(dataset, pd.DataFrame):
        return dataset
    elif isinstance(dataset, (Dataset, IterableDataset)):
        return dataset.to_pandas()
    elif isinstance(dataset, (DatasetDict, IterableDatasetDict)) and 'train' in dataset:
        return dataset_to_dataframe(dataset['train'])
    elif isinstance(dataset, Iterator):
        return pd.concat(list(dataset))
    else:
        raise ValueError(f"Unsupported dataset type: {type(dataset)}")
