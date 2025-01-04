# FILE: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/core/config_analysis/config_loader.py

import logging
import os
from typing import Dict, List, Tuple
import yaml

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}

    def verify_config_exists(self) -> bool:
        return os.path.exists(self.config_path)

    def check_basic_structure(self, config: Dict) -> Tuple[bool, List[str]]:
        issues = []
        if not isinstance(config, dict):
            issues.append("Root element must be a dictionary")
            return False, issues

        if "datasets" not in config:
            issues.append("Missing 'datasets' key in configuration")
            return False, issues

        for dataset_name, dataset_config in config["datasets"].items():
            if not isinstance(dataset_config, dict):
                issues.append(f"Invalid config structure for {dataset_name}")
                continue

            if "columns" not in dataset_config:
                issues.append(f"Missing columns for {dataset_name}")

        return len(issues) == 0, issues

def initialize_config_loader(base_dir: str) -> ConfigLoader:
    config_path = os.path.join(base_dir, "config", "column_mapping.yaml")
    return ConfigLoader(config_path)

if __name__ == "__main__":
    # For testing purposes
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_loader = initialize_config_loader(base_dir)
    config = config_loader.load_config()
    print("Config loaded successfully:", bool(config))
    valid, issues = config_loader.check_basic_structure(config)
    print("Config structure valid:", valid)
    if not valid:
        print("Issues:", issues)
