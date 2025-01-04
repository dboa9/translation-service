from pathlib import Path
import yaml
from core.dataset.dataset_validator import DatasetValidator
from core.dataset.hf_base_loader import HFBaseLoader

class DataReader:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.hf_loader = HFBaseLoader(base_dir)
        self.config = self.load_config()
        self.validator = DatasetValidator(self.config)

    def load_dataset(self, dataset_name, subset):
        dataset = self.hf_loader.load_dataset(dataset_name, subset)
        self.validator.validate_dataset(dataset, dataset_name, subset)
        return dataset

    def load_config(self):
        config_path = Path(self.base_dir) / "config" / "column_mapping_extended.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
