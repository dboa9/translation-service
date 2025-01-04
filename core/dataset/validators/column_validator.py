from typing import Dict, Any, Optional
from datasets import Dataset
import logging

from .dataset_type_handler import handle_dataset_type
from .column_validation_logic import validate_columns
from .error_handler import log_error

logger = logging.getLogger(__name__)

class ColumnValidator:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def validate_dataset_dict(self, dataset_name: str, dataset: Any, config: Optional[str] = None) -> Dict[str, Any]:
        try:
            return handle_dataset_type(dataset, dataset_name, config, self.validate_columns)
        except Exception as e:
            return log_error(f"Error validating dataset {dataset_name}: {str(e)}")

    def validate_columns(self, dataset: Dataset, dataset_name: str, config: Optional[str] = None, split_name: Optional[str] = None) -> Dict[str, Any]:
        return validate_columns(dataset, dataset_name, config, split_name)

# Any other necessary methods...
