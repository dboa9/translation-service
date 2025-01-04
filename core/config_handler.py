# File: config_handler.py
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigHandler:
    def __init__(self, config_path: str = 'config/column_mapping.yaml'):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        """Load the configuration from the YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}"
            )
        
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        return self.config

    def get_dataset_config(self, dataset_name: str) -> Dict[str, Any]:
        """Get the configuration for a specific dataset."""
        return self.config.get('datasets', {}).get(dataset_name, {})

    def get_column_mapping(self, dataset_name: str) -> Dict[str, str]:
        """Get the column mapping for a specific dataset."""
        return self.get_dataset_config(dataset_name).get('column_mapping', {})

    def get_validation_rules(self, dataset_name: str) -> Dict[str, Any]:
        """Get the validation rules for a specific dataset."""
        return self.get_dataset_config(dataset_name).get('validation', {})
