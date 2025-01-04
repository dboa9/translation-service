"""
Enhanced torch validator that handles torch.classes warnings gracefully
"""
import logging
import warnings
from typing import Any, Dict, Optional, Type
from pathlib import Path
from datasets import Dataset, DatasetDict

from core.dataset.dataset_validator import DatasetValidator

logger = logging.getLogger(__name__)

class EnhancedTorchValidator(DatasetValidator):
    """
    Enhanced validator that handles torch.classes warnings gracefully
    while maintaining all original validation functionality
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Filter torch warnings before parent initialization
        warnings.filterwarnings(
            'ignore', 
            message='.*torch.classes.*',
            category=UserWarning
        )
        super().__init__(config)

    def validate_torch_operations(self) -> bool:
        """
        Validate basic torch operations while handling warnings
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                import torch
                
                # Test basic tensor operations
                test_tensor = torch.zeros(1)
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                test_tensor = test_tensor.to(device)
                del test_tensor
                
                return True
        except Exception as e:
            logger.warning(f"Torch operations warning (non-critical): {str(e)}")
            return False
        
    def validate_dataset(self, dataset: Dataset, dataset_name: str, subset: str) -> bool:
        """
        Enhanced dataset validation with torch warning handling
        
        Args:
            dataset: Dataset to validate
            dataset_name: Name of the dataset
            subset: Subset name
            
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            ValueError: If dataset is None or invalid type
        """
        if dataset is None:
            raise ValueError("Dataset cannot be None")
            
        if not isinstance(dataset, (Dataset, DatasetDict)):
            raise ValueError(f"Expected Dataset or DatasetDict, got {type(dataset)}")
            
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                # First validate torch operations
                if not self.validate_torch_operations():
                    logger.warning("Torch operations validation failed")
                    return False
                
                # Check if configuration exists for this dataset/subset
                subset_config = self.config.get('datasets', {}).get(dataset_name, {}).get(subset, {})
                if not subset_config:
                    logger.warning(f"No configuration found for {dataset_name}/{subset}")
                    return False
                    
                # Then proceed with parent validation
                return super().validate_dataset(dataset, dataset_name, subset)
        except Exception as e:
            logger.warning(f"Dataset validation warning (non-critical): {str(e)}")
            return False

    def _validate_split(self, split_dataset: Dataset, dataset_name: str, subset: str, split: str) -> bool:
        """
        Enhanced split validation with torch warning handling
        
        Args:
            split_dataset: Dataset split to validate
            dataset_name: Name of the dataset
            subset: Subset name
            split: Split name
            
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            ValueError: If split_dataset is None or invalid type
        """
        if split_dataset is None:
            raise ValueError("Split dataset cannot be None")
            
        if not isinstance(split_dataset, Dataset):
            raise ValueError(f"Expected Dataset, got {type(split_dataset)}")
            
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                # Check if configuration exists
                subset_config = self.config.get('datasets', {}).get(dataset_name, {}).get(subset, {})
                if not subset_config:
                    logger.warning(f"No configuration found for {dataset_name}/{subset}")
                    return False
                
                return super()._validate_split(split_dataset, dataset_name, subset, split)
        except Exception as e:
            logger.warning(f"Split validation warning (non-critical): {str(e)}")
            return False

    @classmethod
    def create_validator(
        cls,
        validator_type: str = "enhanced",
        config: Optional[Dict[str, Any]] = None
    ) -> DatasetValidator:
        """
        Create a validator instance based on type
        
        Args:
            validator_type: Type of validator to create
                - "standard": Original DatasetValidator
                - "enhanced": EnhancedTorchValidator with warning handling
            config: Optional configuration dictionary
            
        Returns:
            DatasetValidator instance
        """
        validators: Dict[str, Type[DatasetValidator]] = {
            "standard": DatasetValidator,
            "enhanced": cls
        }
        
        validator_class = validators.get(validator_type.lower(), cls)
        return validator_class(config)
