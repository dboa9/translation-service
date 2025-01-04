# File: lightweight_test_runner.py
# lightweight_test_runner.py

import gc
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Union, List, Any

import psutil

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.debug("Importing from config.paths")
from bup.paths import project_paths

logger.debug("Importing EnhancedHFLoader")
try:
    from core.dataset.enhanced_hf_loader import EnhancedHFLoader
except ImportError as e:
    logger.error(f"Error importing EnhancedHFLoader: {e}")
    sys.exit(1)

logger.debug("Importing DatasetPreprocessor")
try:
    from core.dataset.dataset_preprocessor import DatasetPreprocessor
except ImportError as e:
    logger.error(f"Error importing DatasetPreprocessor: {e}")
    sys.exit(1)

# Setup paths using ProjectPaths
LOG_DIR = project_paths.MONITOR_LOGS_DIR
RESULTS_DIR = project_paths.VALIDATION_DIR / "results"
TEST_RESULTS_DIR = project_paths.VALIDATION_DIR / "test_results"

# Create necessary directories
for directory in [LOG_DIR, RESULTS_DIR, TEST_RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"dataset_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

class SystemRequirements:
    MIN_MEMORY_GB = 2
    MIN_DISK_GB = 5

    @classmethod
    def check_system(cls) -> Dict[str, Union[bool, float]]:
        memory_gb = psutil.virtual_memory().total / (1024**3)
        disk_gb = psutil.disk_usage("/").free / (1024**3)

        return {
            "memory_sufficient": memory_gb >= cls.MIN_MEMORY_GB,
            "disk_sufficient": disk_gb >= cls.MIN_DISK_GB,
            "memory_gb": memory_gb,
            "disk_gb": disk_gb,
        }


class DatasetTester:
    def __init__(self, memory_limit_gb: float = 1.5):
        self.memory_limit_gb = memory_limit_gb
        self.results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": self._get_system_info(),
            "tests": {},
        }
        self.column_mapping_path = project_paths.CONFIG_DIR / "column_mapping.yaml"
        logger.info(f"Column mapping path: {self.column_mapping_path}")
        if not self.column_mapping_path.exists():
            logger.error(f"Column mapping file not found at {self.column_mapping_path}")
        self.loader = EnhancedHFLoader(cache_dir=project_paths.CACHE_DIR)
        self.preprocessor = DatasetPreprocessor()

    def _get_system_info(self) -> Dict:
        return {
            "python_version": sys.version,
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "disk_free_gb": psutil.disk_usage("/").free / (1024**3),
        }

    def _check_memory_usage(self) -> float:
        gc.collect()
        return psutil.Process().memory_info().rss / (1024**3)

    def test_dataset_loading(self):
        """Test dataset loading and record metrics"""
        logger.info("Testing dataset loading...")

        datasets_to_process: List[Dict[str, str]] = [
            {"name": "imomayiz/darija-english", "subset": "sentences"},
            {"name": "atlasia/darija_english", "subset": "web_data"},
            {"name": "M-A-D/DarijaBridge", "subset": "default"},
            {"name": "BounharAbdelaziz/English-to-Moroccan-Darija", "subset": "default"}
        ]

        results = {}
        for dataset_info in datasets_to_process:
            dataset_name = dataset_info["name"]
            subset = dataset_info["subset"]
            try:
                logger.info(f"Loading dataset: {dataset_name}, subset: {subset}")
                dataset = self.loader.load_dataset(dataset_name, subset=subset)
                
                if dataset is None:
                    logger.error(f"Failed to load dataset: {dataset_name}, subset: {subset}")
                    results[f"{dataset_name}/{subset}"] = {"error": "Dataset loading failed"}
                    continue

                # Preprocess the dataset
                preprocessed_dataset = self.preprocessor.preprocess_dataset(dataset, dataset_name)
                
                memory_used = self._check_memory_usage()
                results[f"{dataset_name}/{subset}"] = {
                    "loaded": True,
                    "num_examples": len(preprocessed_dataset),
                    "memory_gb": memory_used,
                }
                logger.info(f"Successfully processed {dataset_name}/{subset}")

            except Exception as e:
                logger.error(f"Error processing {dataset_name}/{subset}: {str(e)}")
                results[f"{dataset_name}/{subset}"] = {"error": str(e)}

        self.results["loading_metrics"] = results
        return len([r for r in results.values() if "error" not in r]) > 0

    def verify_data_quality(self, datasets: Dict[str, Dict[str, Any]]):
        """Verify data quality metrics"""
        try:
            metrics = {
                "total_datasets": len(datasets),
                "datasets_loaded": sum(1 for result in datasets.values() if result.get("loaded", False)),
                "total_examples": sum(result.get("num_examples", 0) for result in datasets.values() if "num_examples" in result),
                "errors": sum(1 for result in datasets.values() if "error" in result),
            }

            return metrics
        except Exception as e:
            logger.error(f"Data quality verification error: {str(e)}")
            return None

    def run_tests(self):
        """Run all dataset tests"""
        logger.info("Starting dataset tests...")

        # Check system requirements
        sys_check = SystemRequirements.check_system()
        if not sys_check["memory_sufficient"] or not sys_check["disk_sufficient"]:
            logger.warning(
                f"System below recommended specifications:\n"
                f"Memory: {sys_check['memory_gb']:.1f}GB (min {SystemRequirements.MIN_MEMORY_GB}GB)\n"
                f"Disk: {sys_check['disk_gb']:.1f}GB (min {SystemRequirements.MIN_DISK_GB}GB)"
            )

        # Run tests
        success = self.test_dataset_loading()

        if success:
            quality_metrics = self.verify_data_quality(self.results["loading_metrics"])
            if quality_metrics:
                self.results["quality_metrics"] = quality_metrics

        # Save results
        result_file = (
            TEST_RESULTS_DIR
            / f"dataset_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(result_file, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Test results saved to {result_file}")
        
        # Print results to console
        print(json.dumps(self.results, indent=2))
        
        return success


def main():
    logger.info("Starting dataset validation...")

    tester = DatasetTester()
    if tester.run_tests():
        logger.info("Dataset validation completed successfully")
        return 0
    else:
        logger.error("Dataset validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
