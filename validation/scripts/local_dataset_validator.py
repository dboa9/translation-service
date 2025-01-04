# File: local_dataset_validator.py
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Optional


# Dataset configurations including previously removed datasets
EXPECTED_DATASETS = {
    "BounharAbdelaziz/English-to-Moroccan-Darija": None,
    "atlasia/darija_english": [
        "web_data", "comments", "stories", "doda", "transliteration"
    ],
    "imomayiz/darija-english": ["sentences", "submissions"],
    "M-A-D/DarijaBridge": None,  # Keep original case for display
    # Previously removed datasets being added back
    "Helsinki-NLP/opus-tatoeba-en-ar": None,
    "Helsinki-NLP/opus-mt-ar-en": None,
    "opus-mt-en-ar": None,
    "Helsinki-NLP/opus-mt-en-ar": None
}


class DatasetCacheValidator:
    def __init__(self):
        # Use relative paths from current directory
        self.project_root = Path(
            "/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project"
        )
        self.cache_dir = self.project_root / "core/datasets_cache"
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("DatasetCacheValidator")
        log_dir = self.project_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"dataset_cache_validation_{timestamp}.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        return logger

    def normalize_name(self, name: str) -> str:
        """Normalize dataset name for comparison"""
        return name.lower().replace("-", "_")

    def get_dataset_info(self, path: Path) -> Optional[Dict]:
        """Get dataset info from json file if it exists"""
        try:
            # Look for dataset_info.json in version subdirectory
            for version_dir in (path / "default").glob("*.*.*"):
                for hash_dir in version_dir.glob("*"):
                    info_file = hash_dir / "dataset_info.json"
                    if info_file.exists():
                        with open(info_file) as f:
                            return json.load(f)
        except Exception as e:
            self.logger.error(
                f"Error reading dataset info for {path}: {str(e)}"
            )
        return None

    def get_existing_datasets(self) -> Set[str]:
        """Get list of existing datasets in cache"""
        existing = set()
        try:
            for item in self.cache_dir.glob("*"):
                if item.is_dir() and not item.name.endswith(".lock"):
                    # Check if default/version directory exists
                    default_dir = item / "default"
                    if default_dir.exists():
                        # Get dataset info if available
                        info = self.get_dataset_info(item)
                        if info:
                            # Use dataset name from info if available
                            org_name = item.name.split("___")[0]
                            dataset_name = info.get("dataset_name", "")
                            if dataset_name:
                                full_name = f"{org_name}/{dataset_name}"
                                existing.add(self.normalize_name(full_name))
                        else:
                            # Fallback to directory name
                            dataset_name = item.name.replace("___", "/")
                            existing.add(self.normalize_name(dataset_name))
        except Exception as e:
            self.logger.error(f"Error scanning cache directory: {str(e)}")
        return existing

    def validate_cache(self) -> Dict:
        """Validate existing cache against expected datasets"""
        self.logger.info("Starting dataset cache validation...")

        existing_datasets = self.get_existing_datasets()

        results = {
            "timestamp": datetime.now().isoformat(),
            "cache_dir": str(self.cache_dir),
            "existing_datasets": list(existing_datasets),
            "missing_datasets": [],
            "needs_redownload": False,
            "cache_valid": True
        }

        # Check for missing datasets
        for dataset, configs in EXPECTED_DATASETS.items():
            normalized_name = self.normalize_name(dataset)

            if normalized_name not in existing_datasets:
                results["missing_datasets"].append(dataset)
                results["needs_redownload"] = True
                results["cache_valid"] = False
                self.logger.warning(f"Missing dataset: {dataset}")

            # Check for specific configurations
            if configs:
                for config in configs:
                    config_path = (
                        self.cache_dir /
                        f"{dataset.replace('/', '___')}_{config}"
                    )
                    if not config_path.exists():
                        results["missing_datasets"].append(
                            f"{dataset} ({config})"
                        )
                        results["needs_redownload"] = True
                        results["cache_valid"] = False
                        self.logger.warning(
                            f"Missing dataset configuration: "
                            f"{dataset} ({config})"
                        )

        # Log validation results
        if results["cache_valid"]:
            self.logger.info("Dataset cache validation successful")
        else:
            missing_count = len(results['missing_datasets'])
            msg = f"Dataset cache incomplete. Missing {missing_count} datasets"
            self.logger.warning(msg)

        return results

    def check_cache_integrity(self) -> bool:
        """Check integrity of cache files"""
        try:
            lock_files = list(self.cache_dir.glob("*.lock"))
            for lock_file in lock_files:
                base_name = lock_file.name.split(".lock")[0]
                corresponding_dir = self.cache_dir / base_name
                if not corresponding_dir.exists():
                    self.logger.warning(
                        f"Found orphaned lock file: {lock_file}"
                    )
                    lock_file.unlink()
            return True
        except Exception as e:
            self.logger.error(f"Error checking cache integrity: {str(e)}")
            return False


def main():
    validator = DatasetCacheValidator()

    print("Checking dataset cache...")
    results = validator.validate_cache()

    if results["cache_valid"]:
        print("\n✅ Dataset cache is valid!")
        print(f"Found {len(results['existing_datasets'])} datasets")
        print("\nExisting datasets:")
        for dataset in sorted(results['existing_datasets']):
            print(f"  - {dataset}")
    else:
        print("\n⚠️  Dataset cache needs updating:")
        print(f"Missing {len(results['missing_datasets'])} datasets:")
        for dataset in sorted(results['missing_datasets']):
            print(f"  - {dataset}")

    if validator.check_cache_integrity():
        print("\n✅ Cache integrity check passed")
    else:
        print("\n⚠️  Cache integrity check failed")

    return 0 if results["cache_valid"] else 1


if __name__ == "__main__":
    exit(main())
