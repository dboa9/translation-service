from typing import Dict, Any, Union, Optional
from datasets import Dataset, DatasetDict, IterableDataset
from .enhanced_dataset_validator import EnhancedDatasetValidator
import logging
from itertools import islice

class TokenEfficientValidator(EnhancedDatasetValidator):
    """
    A validator that processes datasets in chunks to avoid token limits.
    Extends EnhancedDatasetValidator to maintain compatibility while adding
    efficient processing methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config or {})
        self.chunk_size = 100  # Configurable chunk size
        self.logger = logging.getLogger(__name__)
        
    def validate_dataset(self, dataset: Union[Dataset, DatasetDict], dataset_name: str, subset: str) -> bool:
        """
        Validates a dataset in chunks to avoid token limits.
        
        Args:
            dataset: The dataset to validate
            dataset_name: Name of the dataset
            subset: Subset of the dataset
            
        Returns:
            Boolean indicating if validation passed
        """
        self.logger.info(f"Starting chunked validation for {dataset_name}/{subset}")
        
        try:
            # Get configuration
            try:
                config = self.config['datasets'][dataset_name][subset]
            except KeyError:
                config = {
                    'columns': dataset.column_names if isinstance(dataset, Dataset) else 
                              next(iter(dataset.values())).column_names
                }
            
            return self._validate_with_config(dataset, dataset_name, subset, config)
            
        except Exception as e:
            self.logger.error(f"Error during validation: {str(e)}")
            return False

    def _validate_with_config(
        self,
        dataset: Union[Dataset, DatasetDict],
        dataset_name: str,
        subset: str,
        config: dict
    ) -> bool:
        """Process dataset with chunking based on its type."""
        try:
            if isinstance(dataset, DatasetDict):
                for split, split_dataset in dataset.items():
                    if not self._validate_split(split_dataset, dataset_name, subset, split, config):
                        return False
                return True
            elif isinstance(dataset, Dataset):
                return self._validate_split(dataset, dataset_name, subset, 'default', config)
            else:
                raise ValueError(f"Unsupported dataset type: {type(dataset)}")
        except Exception as e:
            self.logger.error(f"Error in validation: {str(e)}")
            return False

    def _validate_split(
        self,
        split_dataset: Dataset,
        dataset_name: str,
        subset: str,
        split: str,
        config: dict
    ) -> bool:
        """Validate a dataset split using chunked processing."""
        try:
            # First validate columns - fail fast if columns are invalid
            if not self._validate_columns(split_dataset, dataset_name, subset, split, config):
                return False
                
            if isinstance(split_dataset, IterableDataset):
                return self._validate_iterable_split(split_dataset, dataset_name, subset, split, config)
            
            # Process regular Dataset in chunks
            total_size = len(split_dataset)
            for i in range(0, total_size, self.chunk_size):
                chunk = split_dataset.select(range(i, min(i + self.chunk_size, total_size)))
                
                # Log progress periodically
                if (i // self.chunk_size) % 10 == 0:
                    self.logger.info(
                        f"Processed {i//self.chunk_size} chunks "
                        f"({i}/{total_size} examples) for {dataset_name}/{subset}/{split}"
                    )
                    
            return True
            
        except Exception as e:
            self.logger.error(
                f"Error processing split {split} for {dataset_name}/{subset}: {str(e)}"
            )
            return False

    def _validate_iterable_split(
        self,
        dataset: IterableDataset,
        dataset_name: str,
        subset: str,
        split: str,
        config: dict
    ) -> bool:
        """Validate an IterableDataset split."""
        try:
            # Process in chunks using islice
            iterator = iter(dataset)
            chunk_count = 0
            
            while True:
                chunk = list(islice(iterator, self.chunk_size))
                if not chunk:
                    break
                    
                chunk_count += 1
                
                # Log progress periodically
                if chunk_count % 10 == 0:
                    self.logger.info(
                        f"Processed {chunk_count} chunks for {dataset_name}/{subset}/{split}"
                    )
                    
            return True
            
        except Exception as e:
            self.logger.error(
                f"Error processing IterableDataset {dataset_name}/{subset}/{split}: {str(e)}"
            )
            return False

    def _validate_columns(
        self,
        dataset: Union[Dataset, IterableDataset],
        dataset_name: str,
        subset: str,
        split: str,
        config: dict
    ) -> bool:
        """Validate columns with enhanced error handling."""
        try:
            expected_columns = config.get('columns', [])
            actual_columns = dataset.column_names
            
            if not actual_columns:
                self.logger.error(f"No columns found in dataset {dataset_name}/{subset}/{split}")
                return False
                
            missing_columns = set(expected_columns) - set(actual_columns)
            if missing_columns:
                self.logger.error(
                    f"Missing required columns in {dataset_name}/{subset}/{split}: {missing_columns}"
                )
                return False
                
            extra_columns = set(actual_columns) - set(expected_columns)
            if extra_columns:
                self.logger.warning(
                    f"Extra columns found in {dataset_name}/{subset}/{split}: {extra_columns}"
                )
                # Don't fail for extra columns, just warn
                
            return True
            
        except Exception as e:
            self.logger.error(
                f"Error validating columns for {dataset_name}/{subset}/{split}: {str(e)}"
            )
            return False

    def set_chunk_size(self, size: int) -> None:
        """Configure chunk size for processing."""
        self.chunk_size = size
