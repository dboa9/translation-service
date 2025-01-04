# File: dataset-cache-validator.py
# dataset_cache_validator.py
# Location: /home/ubuntu/darija_project_new/validation/scripts/dataset_cache_validator.py

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Set

# Dataset configurations including previously removed datasets
EXPECTED_DATASETS = {
    "BounharAbdelaziz/English-to-Moroccan-Darija": None,
    "atlasia/darija_english": [
        "web_data", "comments", "stories", "doda", "transliteration"
    ],
    "imomayiz/darija-english": ["sentences", "submissions"],
    "M-A-D/DarijaBridge": None,
    # Previously removed datasets being added back
    "Helsinki-NLP/opus-tatoeba-en-ar": None,
    "Helsinki-NLP/opus-mt-ar-en": None,
    "opus-mt-en-ar": None,
    "Helsinki-NLP/opus-mt-en-ar": None
}

class DatasetCacheValidator:
    def __init__(self, cache_dir: str = "/home/ubuntu/darija_project_new/datasets_cache"):
        self.cache_dir = Path(cache_dir)
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("DatasetCacheValidator")
        log_dir = Path("/home/ubuntu/darija_project_new/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"dataset_cache_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        return logger

    def get_existing_datasets(self) -> Set[str]:
        """Get list of existing datasets in cache"""
        existing = set()
        try:
            for item in self.cache_dir.glob("*"):
                if item.is_dir() and not item.name.endswith(".lock"):
                    # Convert cache directory format to dataset name
                    dataset_name = item.name.replace("___", "/")
                    existing.add(dataset_name)
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
            normalized_name = dataset.replace("/", "___").lower()
            
            if normalized_name not in [d.lower() for d in existing_datasets]:
                results["missing_datasets"].append(dataset)
                results["needs_redownload"] = True
                results["cache_valid"] = False
                self.logger.warning(f"Missing dataset: {dataset}")
            
            # Check for specific configurations
            if configs:
                for config in configs:
                    config_path = self.cache_dir / f"{normalized_name}_{config}"
                    if not config_path.exists():
                        results["missing_datasets"].append(f"{dataset} ({config})")
                        results["needs_redownload"] = True
                        results["cache_valid"] = False
                        self.logger.warning(f"Missing dataset configuration: {dataset} ({config})")

        # Log validation results
        if results["cache_valid"]:
            self.logger.info("Dataset cache validation successful")
        else:
            self.logger.warning(
                f"Dataset cache incomplete. Missing {len(results['missing_datasets'])} datasets"
            )

        return results

    def check_cache_integrity(self) -> bool:
        """Check integrity of cache files"""
        try:
            lock_files = list(self.cache_dir.glob("*.lock"))
            for lock_file in lock_files:
                corresponding_dir = self.cache_dir / lock_file.name.split(".lock")[0]
                if not corresponding_dir.exists():
                    self.logger.warning(f"Found orphaned lock file: {lock_file}")
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
    else:
        print("\n⚠️  Dataset cache needs updating:")
        print(f"Missing {len(results['missing_datasets'])} datasets:")
        for dataset in results['missing_datasets']:
            print(f"  - {dataset}")
            
    if validator.check_cache_integrity():
        print("\n✅ Cache integrity check passed")
    else:
        print("\n⚠️  Cache integrity check failed")
        
    return 0 if results["cache_valid"] else 1

if __name__ == "__main__":
    exit(main())
