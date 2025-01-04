from typing import Dict, Any, Union, List, Tuple
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from core.dataset.dataset_validator import DatasetValidator
import logging

logger = logging.getLogger(__name__)

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

class NewExtendedDatasetValidator(DatasetValidator):
    def validate_dataset(self, dataset: DatasetType, dataset_name: str, subset: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        success = True
        issues = []
        stats = {}

        if isinstance(dataset, (Dataset, IterableDataset)):
            success, issues, stats = self._validate_split(dataset, dataset_name, subset, "default")
        elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            for split, split_dataset in dataset.items():
                split_success, split_issues, split_stats = self._validate_split(split_dataset, dataset_name, subset, split)
                success = success and split_success
                issues.extend(split_issues)
                stats[split] = split_stats
        else:
            return False, [f"Unsupported dataset type: {type(dataset)}"], {}

        return success, issues, stats

    def _validate_split(self, split_dataset: Union[Dataset, IterableDataset], dataset_name: str, subset: str, split: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        success = True
        issues = []
        stats = {"num_rows": len(split_dataset) if isinstance(split_dataset, Dataset) else "unknown", "columns": split_dataset.column_names}

        if isinstance(split_dataset, IterableDataset):
            split_dataset = self._convert_iterable_dataset(split_dataset)

        try:
            subset_config = self.config['datasets'][dataset_name][subset]
            if not isinstance(subset_config, dict):
                raise ValueError(f"Invalid configuration for dataset: {dataset_name}/{subset}. Expected a dictionary.")
            expected_columns = set(subset_config['required_columns'])
        except KeyError:
            return False, [f"No configuration found for dataset: {dataset_name}/{subset}"], stats

        actual_columns = set(split_dataset.column_names)
        if not expected_columns.issubset(actual_columns):
            missing_columns = expected_columns - actual_columns
            success = False
            issues.append(f"Missing columns in {dataset_name}/{subset}/{split}: {missing_columns}")

        for column in expected_columns:
            if column in split_dataset.features:
                feature = split_dataset.features[column]
                if hasattr(feature, 'dtype'):
                    column_type = feature.dtype
                else:
                    column_type = type(feature).__name__
                expected_type = subset_config.get('column_types', {}).get(column, column_type)
                if column_type != expected_type:
                    logger.warning(f"Column {column} in {dataset_name}/{subset} in split '{split}' has type {column_type}, expected '{expected_type}'")
            else:
                success = False
                issues.append(f"Column {column} not found in {dataset_name}/{subset} in split '{split}'")

        return success, issues, stats

    def _convert_iterable_dataset(self, dataset: IterableDataset) -> Dataset:
        data = list(dataset)
        return Dataset.from_dict({k: [d[k] for d in data] for k in data[0].keys()})

    def get_column_mapping(self, dataset_name: str, subset: str) -> Dict[str, str]:
        try:
            return {col: col for col in self.config['datasets'][dataset_name][subset]['required_columns']}
        except KeyError as e:
            logger.error(f"Error getting column mapping for {dataset_name}/{subset}: {str(e)}")
            raise
