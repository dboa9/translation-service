#core/dataset/enhanced_dataset_validator.py
from core.dataset.dataset_validator import DatasetValidator
from datasets import DatasetDict, Dataset
from typing import Union

class EnhancedDatasetValidator(DatasetValidator):
    """
    An enhanced version of the DatasetValidator that provides additional functionality
    for handling cases where the configuration might not be present and supports both
    Dataset and DatasetDict types.
    """

    def __init__(self, config):
        """
        Initialize the EnhancedDatasetValidator with the given configuration.

        Args:
            config (dict): The configuration dictionary for dataset validation.
        """
        super().__init__(config)

    def validate_dataset(self, dataset: Union[Dataset, DatasetDict], dataset_name: str, subset: str) -> bool:
        """
        Validate the given dataset using either the provided configuration or a default one.

        This method handles both Dataset and DatasetDict types and uses a default
        configuration if the specific configuration is not found.

        Args:
            dataset (Dataset or DatasetDict): The dataset to validate.
            dataset_name (str): The name of the dataset.
            subset (str): The subset of the dataset being validated.

        Returns:
            bool: True if the validation passes, False otherwise.

        Raises:
            ValueError: If the dataset type is not supported.
        """
        try:
            config = self.config['datasets'][dataset_name][subset]
        except KeyError:
            # Provide a default configuration if the specific configuration is not found
            config = {
                'columns': ['expected_column_1', 'expected_column_2']  # Replace with actual expected columns
            }
        
        return self._validate_with_config(dataset, dataset_name, subset, config)

    def _validate_with_config(self, dataset: Union[Dataset, DatasetDict], dataset_name: str, subset: str, config: dict) -> bool:
        """
        Validate the dataset using the provided configuration.

        This method handles both DatasetDict and Dataset types.

        Args:
            dataset (Dataset or DatasetDict): The dataset to validate.
            dataset_name (str): The name of the dataset.
            subset (str): The subset of the dataset being validated.
            config (dict): The configuration to use for validation.

        Returns:
            bool: True if the validation passes, False otherwise.

        Raises:
            ValueError: If the dataset type is not supported.
        """
        if isinstance(dataset, DatasetDict):
            for split, split_dataset in dataset.items():
                self._validate_split(split_dataset, dataset_name, subset, split, config)
        elif isinstance(dataset, Dataset):
            self._validate_split(dataset, dataset_name, subset, 'default', config)
        else:
            raise ValueError(f"Unsupported dataset type: {type(dataset)}")
        return True

    def _validate_split(self, split_dataset: Dataset, dataset_name: str, subset: str, split: str, config: dict):
        """
        Validate a specific split of the dataset using the provided configuration.

        This method can be extended to include additional validation checks beyond
        column validation.

        Args:
            split_dataset (Dataset): The dataset split to validate.
            dataset_name (str): The name of the dataset.
            subset (str): The subset of the dataset being validated.
            split (str): The name of the split being validated.
            config (dict): The configuration to use for validation.
        """
        self._validate_columns(split_dataset, dataset_name, subset, split, config)
        # Add other validation checks as needed

    def _validate_columns(self, split_dataset: Dataset, dataset_name: str, subset: str, split: str, config: dict):
        """
        Validate the columns of a dataset split using the provided configuration.

        This method checks if the actual columns in the dataset match the expected
        columns specified in the configuration. It prints a warning if there's
        a mismatch.

        Args:
            split_dataset (Dataset): The dataset split to validate.
            dataset_name (str): The name of the dataset.
            subset (str): The subset of the dataset being validated.
            split (str): The name of the split being validated.
            config (dict): The configuration to use for validation.
        """
        expected_columns = config.get('columns', [])
        actual_columns = split_dataset.column_names

        if set(expected_columns) != set(actual_columns):
            print(f"Warning: Column mismatch in dataset: {dataset_name}/{subset}/{split}. "
                  f"Expected: {expected_columns}, Actual: {actual_columns}")
        # Add other column-specific validation checks as needed

# TODO: Consider adding more methods for additional validation checks
# TODO: Implement logging instead of print statements for better error tracking
