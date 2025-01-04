#core/dataset/extended_dataset_validator.py
import logging
from typing import Any, Dict, List, Tuple, Union, Optional, Set, cast, Iterable

from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

logger = logging.getLogger(__name__)

class ExtendedDatasetValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def validate_dataset(self, dataset: DatasetType, dataset_name: str, subset: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        success = True
        issues = []
        stats = {}

        logger.info(f"Validating dataset: {dataset_name}, subset: {subset}")
        logger.debug(f"Dataset type: {type(dataset)}")

        if isinstance(dataset, (Dataset, IterableDataset)):
            success, issues, stats = self._validate_single_dataset(dataset, dataset_name, subset)
        elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            for split, split_dataset in dataset.items():
                split_success, split_issues, split_stats = self._validate_single_dataset(split_dataset, dataset_name, subset, split)
                success = success and split_success
                issues.extend(split_issues)
                stats[split] = split_stats
        else:
            return False, [f"Unsupported dataset type: {type(dataset)}"], {}

        return success, issues, stats

    def _validate_single_dataset(self, dataset: Union[Dataset, IterableDataset], dataset_name: str, subset: str, split: Optional[str] = None) -> Tuple[bool, List[str], Dict[str, Any]]:
        success = True
        issues = []
        stats = {"num_rows": len(dataset) if isinstance(dataset, Dataset) else "unknown", "columns": dataset.column_names}

        logger.info(f"Validating single dataset: {dataset_name}, subset: {subset}, split: {split}")

        try:
            datasets_config = self.config.get('debug', {}).get('datasets', {})
            logger.debug(f"Datasets config: {datasets_config}")
            
            dataset_config = datasets_config.get(dataset_name, {})
            logger.debug(f"Dataset config for {dataset_name}: {dataset_config}")
            
            subset_config = dataset_config.get('required_columns', {}).get(subset, {})
            logger.debug(f"Subset config for {subset}: {subset_config}")
            
            if not subset_config:
                raise ValueError(f"No configuration found for dataset: {dataset_name}, subset: {subset}")
            
            if isinstance(subset_config, dict) and split:
                expected_columns = subset_config.get(split)
                logger.debug(f"Expected columns for split {split}: {expected_columns}")
            else:
                expected_columns = subset_config
                logger.debug(f"Expected columns: {expected_columns}")

            if not expected_columns:
                raise ValueError(f"No required columns specified for dataset: {dataset_name}, subset: {subset}, split: {split}")
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            return False, [str(e)], stats

        actual_columns = set(dataset.column_names)
        expected_columns_set = self._create_set_from_list(expected_columns)
        missing_columns = expected_columns_set - actual_columns
        if missing_columns:
            success = False
            issue = f"Missing columns in {dataset_name}/{subset}/{split or ''}: {missing_columns}"
            issues.append(issue)
            logger.warning(issue)

        column_types = dataset_config.get('column_types', {})
        if not isinstance(column_types, dict):
            success = False
            issue = f"Column types must be a dictionary for dataset: {dataset_name}, subset: {subset}"
            issues.append(issue)
            logger.warning(issue)
        else:
            features = dataset.features if isinstance(dataset, Dataset) else None
            for column in expected_columns_set:
                if features and column in features:
                    feature = features[column]
                    column_type = feature.dtype if hasattr(feature, 'dtype') else type(feature).__name__
                    expected_type = column_types.get(column, column_type)
                    if column_type != expected_type:
                        issue = f"Column {column} in {dataset_name}/{subset}/{split or ''} has type {column_type}, expected {expected_type}"
                        issues.append(issue)
                        logger.warning(issue)
                elif column not in actual_columns:
                    success = False
                    issue = f"Column {column} not found in {dataset_name}/{subset}/{split or ''}"
                    issues.append(issue)
                    logger.warning(issue)

        logger.info(f"Validation result for {dataset_name}/{subset}/{split or ''}: Success={success}, Issues={issues}")
        return success, issues, stats

    def get_column_mapping(self, dataset_name: str, subset: str) -> Dict[str, str]:
        try:
            datasets_config = self.config.get('debug', {}).get('datasets', {})
            dataset_config = datasets_config.get(dataset_name, {})
            subset_config = dataset_config.get('required_columns', {}).get(subset, {})
            
            logger.debug(f"Getting column mapping for {dataset_name}/{subset}")
            logger.debug(f"Subset config: {subset_config}")
            
            if not subset_config:
                raise ValueError(f"No configuration found for dataset: {dataset_name}, subset: {subset}")
            
            if isinstance(subset_config, dict):
                required_columns = [col for split_columns in subset_config.values() for col in self._create_set_from_list(split_columns)]
            else:
                required_columns = list(self._create_set_from_list(subset_config))

            if not required_columns:
                raise ValueError(f"No required columns specified for dataset: {dataset_name}, subset: {subset}")
            
            column_mapping = {col: col for col in required_columns}
            logger.debug(f"Column mapping: {column_mapping}")
            return column_mapping
        except ValueError as e:
            logger.error(f"Error getting column mapping: {str(e)}")
            raise KeyError(f"Error getting column mapping for {dataset_name}/{subset}: {str(e)}")

    @staticmethod
    def _create_set_from_list(lst: Any) -> Set[str]:
        if lst is None:
            return set()
        elif isinstance(lst, str):
            return {lst}
        elif isinstance(lst, list):
            return set(item for item in lst if isinstance(item, str))
        elif isinstance(lst, dict):
            return set(item for item in lst.values() if isinstance(item, str))
        else:
            return set()
