"""
Factory for creating dataset validators
"""
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Type

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.dataset.dataset_validator import DatasetValidator
from core.dataset.enhanced_torch_validator import EnhancedTorchValidator

class ValidatorFactory:
    """Factory class for creating dataset validators"""
    
    @staticmethod
    def create_validator(
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
            "enhanced": EnhancedTorchValidator
        }
        
        validator_class = validators.get(validator_type.lower(), EnhancedTorchValidator)
        return validator_class(config)
