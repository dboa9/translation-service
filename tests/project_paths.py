"""
Note: This code should be saved with the current GMT date and time in the format:
project_paths.py
Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/translation-service/tests/project_paths.py
Author: dboa9 (danielalchemy9@gmail.com)
"""

import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATASET_CONFIGS = {
    "atlasia/darija_english": {
        "subsets": ["web_data", "comments", "stories", "doda", "transliteration"],
        "required_columns": {
            "web_data": ["darija", "english", "source"],
            "comments": ["darija", "english", "source"],
            "stories": ["darija", "english", "source"],
            "doda": ["darija", "english", "source"],
            "transliteration": ["darija", "english", "source"]
        }
    },
    "imomayiz/darija-english": {
        "subsets": ["sentences", "submissions"],
        "required_columns": {
            "sentences": ["darija", "eng", "darija_ar"],
            "submissions": ["darija", "eng", "darija_ar", "timestamp"]
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

class ProjectPaths:
    def __init__(self):
        # Base directories
        self.BASE_DIR = self._detect_environment()
        
        # Core directories 
        self.CORE_DIR = self.BASE_DIR / "core"
        self.DATASET_DIR = self.CORE_DIR / "dataset"
        self.UTILS_DIR = self.CORE_DIR / "utils"
        self.INTERFACES_DIR = self.CORE_DIR / "interfaces"
        
        # Data directories
        self.DATA_DIR = self.BASE_DIR / "data"
        self.CACHE_DIR = self.BASE_DIR / "datasets_cache"
        self.TEST_DATA_DIR = self.BASE_DIR / "test_data_sample"
        
        # Model directories
        self.MODELS_DIR = self.BASE_DIR / "models"
        self.CHECKPOINTS_DIR = self.MODELS_DIR / "checkpoints"
        
        # Monitoring
        self.MONITOR_DIR = self.BASE_DIR / "monitoring"
        self.METRICS_DIR = self.MONITOR_DIR / "metrics"
        
        # Deployment paths
        self.DEPLOYMENT_DIR = self.BASE_DIR / "deployment"
        self.SCRIPTS_DIR = self.DEPLOYMENT_DIR / "scripts"
        
        # EC2 configuration
        self.EC2_HOST = os.getenv('EC2_HOST', 'ec2-34-233-67-166.compute-1.amazonaws.com')
        self.EC2_USER = os.getenv('EC2_USER', 'ubuntu')
        self.EC2_KEY_PATH = Path(os.getenv('EC2_KEY_PATH', '/home/mrdbo/key-6-10-24.pem'))
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Validate paths
        self._validate_paths()

    def _detect_environment(self) -> Path:
        """Detect current environment and return appropriate base path"""
        windows_path = Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project")
        ubuntu_path = Path("/home/mrdbo/daija_dataset_tests_project")
        ec2_path = Path("/home/ubuntu/darija_project_new")

        if windows_path.exists():
            logger.info("Detected Windows WSL environment")
            return windows_path
        elif ubuntu_path.exists():
            logger.info("Detected Ubuntu environment")
            return ubuntu_path
        elif ec2_path.exists():
            logger.info("Detected EC2 environment")
            return ec2_path
        else:
            raise EnvironmentError("Unable to detect valid project environment")

    def _ensure_directories(self):
        """Create required directories if they don't exist"""
        directories = [
            self.CORE_DIR,
            self.DATASET_DIR,
            self.UTILS_DIR,
            self.INTERFACES_DIR,
            self.DATA_DIR,
            self.CACHE_DIR,
            self.TEST_DATA_DIR,
            self.MODELS_DIR,
            self.CHECKPOINTS_DIR,
            self.MONITOR_DIR,
            self.METRICS_DIR,
            self.DEPLOYMENT_DIR,
            self.SCRIPTS_DIR
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")

    def _validate_paths(self):
        """Validate critical paths exist and are accessible"""
        critical_paths = {
            "Base Directory": self.BASE_DIR,
            "Core Directory": self.CORE_DIR,
            "Dataset Cache": self.CACHE_DIR,
            "Models Directory": self.MODELS_DIR
        }
        
        for name, path in critical_paths.items():
            if not path.exists():
                logger.error(f"Critical path missing: {name} at {path}")
                raise FileNotFoundError(f"Critical path missing: {name}")
            if not os.access(path, os.R_OK | os.W_OK):
                logger.error(f"Insufficient permissions for: {name}")
                raise PermissionError(f"Insufficient permissions for: {name}")

    def get_model_path(self, model_name: str) -> Path:
        """Get path for a specific model"""
        return self.MODELS_DIR / model_name

    def get_dataset_path(self, dataset_name: str, subset: str = "default") -> Path:
        """Get path for a specific dataset and subset"""
        dataset_dir = self.CACHE_DIR / dataset_name.replace("/", "___")
        if dataset_name in DATASET_CONFIGS and subset in DATASET_CONFIGS[dataset_name]["subsets"]:
            return dataset_dir / subset
        else:
            return dataset_dir

    def get_deployment_script(self, script_name: str) -> Path:
        """Get path for a deployment script"""
        return self.SCRIPTS_DIR / script_name

# Create singleton instance
project_paths = ProjectPaths()

if __name__ == "__main__":
    # Test path detection and validation
    try:
        print(f"Base directory: {project_paths.BASE_DIR}")
        print(f"Environment detected: {project_paths.BASE_DIR}")
        print("\nCritical paths:")
        print(f"Dataset cache: {project_paths.CACHE_DIR}")
        print(f"Models directory: {project_paths.MODELS_DIR}")
        print(f"Deployment scripts: {project_paths.SCRIPTS_DIR}")
        
        print("\nEC2 Configuration:")
        print(f"Host: {project_paths.EC2_HOST}")
        print(f"User: {project_paths.EC2_USER}")
        print(f"Key path: {project_paths.EC2_KEY_PATH}")
        
        # Test dataset path generation
        for dataset_name, config in DATASET_CONFIGS.items():
            for subset in config['subsets']:
                path = project_paths.get_dataset_path(dataset_name, subset)
                print(f"\nDataset path for {dataset_name} - {subset}: {path}")
                print(f"Required columns: {config['required_columns'].get(subset, 'Not specified')}")
        
    except Exception as e:
        logger.error(f"Error during path validation: {e}")
        raise
