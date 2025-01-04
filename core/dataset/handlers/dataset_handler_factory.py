# File: dataset_handler_factory.py
from typing import Any, Dict

# In any file that needs to import ModernDatasetHandler
from core.dataset.import_manager import ModernDatasetHandler

from .modern_dataset_handler import ModernDatasetHandler


class DatasetHandlerFactory:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def create_handler(self, dataset_name: str) -> ModernDatasetHandler:
        if dataset_name not in self.config:
            raise ValueError(
                f"No configuration found for dataset: {dataset_name}"
            )
        
        return ModernDatasetHandler(self.config[dataset_name])
