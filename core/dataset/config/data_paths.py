import os
from pathlib import Path

class DataPaths:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "datasets_cache"
        self.test_data_dir = self.base_dir / "test_data_sample"
        self.config_dir = self.base_dir / "config"

    def get_dataset_test_path(self, dataset_name: str) -> Path:
        return self.test_data_dir / dataset_name.replace("/", "_")

    def get_dataset_cache_path(self, dataset_name: str) -> Path:
        return self.cache_dir / dataset_name.replace("/", "___")

    def get_config_path(self, config_file: str) -> Path:
        return self.config_dir / config_file
