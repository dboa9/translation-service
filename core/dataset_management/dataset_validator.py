# File: dataset_validator.py
#!/usr/bin/env python3
# core/dataset_management/dataset_validator.py

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
import yaml

from core.config_analysis.extended_column_mapping_validator import validate_extended_column_mapping_structure

from datasets import Dataset, load_dataset, DatasetDict
from datasets.iterable_dataset import IterableDataset

from core.dataset.dataset_types import DatasetType
from config.project_paths import DATASET_CONFIGS

logger = logging.getLogger(__name__)

class DatasetValidator:
    """Enhanced dataset validator with quality metrics and debug options."""

    def __init__(self, config_path: str = 'config/dataset_loader_debug.yaml', cache_dir: Optional[Path] = None):
        """Initialize the dataset validator.
        
        Args:
            config_path: Path to the debug configuration file
            cache_dir: Optional path to the cache directory
        """
        self.config = self._load_config(config_path)
        self.quality_metrics = self.config['dataset']['validation']
        self.cache_dir = cache_dir
        self.logger = self._setup_logging()
        self.validation_stats: Dict[str, int] = {}

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(self.config['logging']['level'])

        log_dir = Path(self.config['logging']['file']['path']).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        fh = logging.FileHandler(self.config['logging']['file']['path'])
        fh.setFormatter(logging.Formatter(self.config['logging']['format']))
        logger.addHandler(fh)

        return logger

    def load_and_validate_dataset(
        self,
        dataset_name: str,
        split: str = "train"
    ) -> Tuple[bool, List[str], Dict[str, int]]:
        """Load and validate a dataset from the Hugging Face hub."""
        try:
            cache_dir_str = str(self.cache_dir) if self.cache_dir else None
            dataset = load_dataset(dataset_name, split=split, cache_dir=cache_dir_str)
            
            if isinstance(dataset, DatasetDict):
                if split in dataset:
                    dataset = dataset[split]
                else:
                    msg = f"Split '{split}' not found in dataset"
                    self.logger.error(msg)
                    return False, [msg], {}
            
            if isinstance(dataset, IterableDataset):
                msg = "IterableDataset not supported for validation"
                self.logger.error(msg)
                return False, [msg], {}
                
            if not isinstance(dataset, Dataset):
                msg = "Failed to load dataset as Dataset object"
                self.logger.error(msg)
                return False, [msg], {}
                
            return self.validate_dataset(dataset, dataset_name, split)
        except Exception as e:
            msg = f"Failed to load dataset {dataset_name}: {str(e)}"
            self.logger.error(msg)
            return False, [msg], {}

    def validate_dataset(
        self,
        dataset: Dataset,
        dataset_name: str,
        subset: str
    ) -> Tuple[bool, List[str], Dict[str, int]]:
        """Validate dataset structure and data quality."""
        self.logger.info(f"Starting validation for dataset: {dataset_name} - {subset}")

        # Validate extended column mapping structure
        mapping_errors = validate_extended_column_mapping_structure('config/column_mapping.yaml')
        if mapping_errors:
            self.logger.warning(f"Extended column mapping validation failed: {mapping_errors}")
            return False, mapping_errors, {}

        if not dataset:
            self.logger.error("Dataset is None")
            return False, ["Dataset is None"], {}

        total_examples = len(dataset)
        stats: Dict[str, int] = {
            "total_examples": total_examples,
            "empty_examples": 0,
            "short_examples": 0,
            "long_examples": 0,
            "invalid_ratio_examples": 0,
            "invalid_format_examples": 0,
            "valid_examples": 0
        }
        issues: List[str] = []

        # Validate column names
        required_columns = DATASET_CONFIGS[dataset_name]["required_columns"][subset]
        missing_cols = [col for col in required_columns if col not in dataset.column_names]
        if missing_cols:
            msg = f"Missing required columns: {missing_cols}"
            issues.append(msg)
            self.logger.warning(msg)
            return False, issues, stats

        # Validate each example
        for idx, example in enumerate(dataset):
            if not isinstance(example, dict):
                stats["invalid_format_examples"] += 1
                continue

            try:
                # Adjust column names based on the dataset and subset
                english_col = "english" if "english" in required_columns else "eng"
                darija_col = "darija" if "darija" in required_columns else "darija_ar"
                
                english_text = example.get(english_col, "")
                darija_text = example.get(darija_col, "")

                if not isinstance(english_text, str) or not isinstance(darija_text, str):
                    stats["invalid_format_examples"] += 1
                    continue

                if not english_text.strip() or not darija_text.strip():
                    stats["empty_examples"] += 1
                    if self.config['debug']['log_failed_examples']:
                        self.logger.debug(f"Empty example found: {example}")
                    continue

                english_words = len(english_text.split())
                darija_words = len(darija_text.split())

                # Check length constraints
                if (english_words < self.quality_metrics["min_length"] or
                        darija_words < self.quality_metrics["min_length"]):
                    stats["short_examples"] += 1
                    if self.config['debug']['log_failed_examples']:
                        self.logger.debug(f"Short example found: {example}")

                if (english_words > self.quality_metrics["max_length"] or
                        darija_words > self.quality_metrics["max_length"]):
                    stats["long_examples"] += 1
                    if self.config['debug']['log_failed_examples']:
                        self.logger.debug(f"Long example found: {example}")

                # Check ratio constraints
                if english_words > 0 and darija_words > 0:
                    ratio = english_words / darija_words
                    if (ratio < self.quality_metrics["min_ratio"] or
                            ratio > self.quality_metrics["max_ratio"]):
                        stats["invalid_ratio_examples"] += 1
                        if self.config['debug']['log_failed_examples']:
                            self.logger.debug(f"Invalid ratio example found: {example}")

            except Exception as e:
                self.logger.error(f"Error processing example {idx}: {e}")
                issues.append(f"Error processing example {idx}: {e}")

        # Calculate valid examples
        stats["valid_examples"] = (
            total_examples -
            stats["empty_examples"] -
            stats["invalid_format_examples"]
        )

        self.validation_stats = stats
        if self.config['debug']['log_validation_stats']:
            self.logger.info(f"Validation complete for {dataset_name} - {subset}. Stats: {stats}")
        
        return success, issues, stats

if __name__ == "__main__":
    validator = DatasetValidator()
    for dataset_name, config in DATASET_CONFIGS.items():
        for subset in config['subsets']:
            success, issues, stats = validator.load_and_validate_dataset(dataset_name, subset)
            print(f"Dataset: {dataset_name}, Subset: {subset}")
            print(f"Success: {success}")
            print(f"Issues: {issues}")
            print(f"Stats: {stats}")
            print("---")
