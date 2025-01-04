from pathlib import Path
import yaml
from typing import Dict, Any, Optional

DATASET_CONFIGS = {
    "atlasia/darija_english": {
        "subsets": ["web_data", "comments", "stories", "doda", "transliteration"],
        "required_columns": {
            "web_data": ["english", "darija", "source"],
            "comments": ["id", "english", "darija", "source"],
            "stories": ["ChapterName", "ChapterLink", "Author", "Tags", "darija", "english", "chunk_id", "source"],
            "doda": ["id", "darija", "en"],
            "transliteration": ["darija_arabizi", "darija_arabic"]
        }
    },
    "imomayiz/darija-english": {
        "subsets": ["sentences"],
        "required_columns": {
            "sentences": ["darija", "eng", "darija_ar"]
        }
    },
    "M-A-D/DarijaBridge": {
        "subsets": ["default"],
        "required_columns": {
            "default": ["sentence", "translation", "translated", "corrected", "correction", "quality", "metadata"]
        }
    },
    "BounharAbdelaziz/English-to-Moroccan-Darija": {
        "subsets": ["default"],
        "required_columns": {
            "default": ["english", "darija", "includes_arabizi"]
        }
    }
}

class IntegrationChecker:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use default DATASET_CONFIGS."""
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                # Merge file config with default config, preferring file config
                return {**DATASET_CONFIGS, **(file_config or {})}
        return DATASET_CONFIGS

    def check_integration(self, dataset_name: str, subset: str) -> bool:
        """
        Check if a dataset and its subset are properly integrated.
        
        Args:
            dataset_name: Name of the dataset (e.g., "atlasia/darija_english")
            subset: Name of the subset (e.g., "web_data", "default")
            
        Returns:
            bool: True if integration check passes, False otherwise
        """
        # Check if dataset exists in config
        if dataset_name not in self.config:
            return False

        dataset_config = self.config[dataset_name]

        # Handle default subset for datasets that don't specify subsets
        if subset == "default":
            if "subsets" not in dataset_config:
                return True
            return "default" in dataset_config["subsets"]

        # Check if subset is valid for this dataset
        if "subsets" in dataset_config:
            if subset not in dataset_config["subsets"]:
                return False

        # Check if required columns are defined for this subset
        if "required_columns" in dataset_config:
            if subset not in dataset_config["required_columns"]:
                return False

        return True

    def get_required_columns(self, dataset_name: str, subset: str) -> list:
        """Get the required columns for a dataset subset."""
        if dataset_name not in self.config:
            return []
        
        dataset_config = self.config[dataset_name]
        if "required_columns" not in dataset_config:
            return []
            
        subset_columns = dataset_config["required_columns"].get(subset, [])
        return subset_columns
