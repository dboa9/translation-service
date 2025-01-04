# File: deployment_test_runner.py
# Note: File should be saved with current GMT date/time
# Format: deployment_test_runner.py

import logging
import sys
from pathlib import Path
from datetime import datetime

# Import updated path management
from bup.paths import project_paths

logger = logging.getLogger(__name__)

class DeploymentValidator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
        self.setup_logging()
        
    def setup_logging(self):
        log_file = project_paths.BASE_DIR / "logs" / f"deployment_validation_{self.timestamp}.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def validate_deployment(self):
        """Validate deployment structure and files"""
        # First verify paths
        path_status = self._verify_paths()
        if not path_status["verified"]:
            logger.error(f"Missing directories: {path_status['missing']}")
            return False

        # Check required files
        required_files = [
            project_paths.get_version_path("dataset_loader"),
            project_paths.get_version_path("web_interface"),
            project_paths.UTILS_DIR / "base_utilities_module.py"
        ]

        missing_files = []
        for file in required_files:
            if not file.exists():
                missing_files.append(file)
                logger.error(f"Missing required file: {file}")

        return len(missing_files) == 0

    def _verify_paths(self):
        """Verify all critical paths exist"""
        required_dirs = [
            project_paths.BASE_DIR,
            project_paths.CORE_DIR,
            project_paths.INTERFACES_DIR,
            project_paths.UTILS_DIR,
            project_paths.MONITORING_DIR,
            project_paths.METRICS_DIR,
            project_paths.ALERTS_DIR,
            project_paths.MONITOR_LOGS_DIR,
        ]

        missing = []
        for directory in required_dirs:
            if not directory.exists():
                missing.append(directory)

        return {"verified": len(missing) == 0, "missing": missing}

def main():
    validator = DeploymentValidator()
    if validator.validate_deployment():
        logger.info("Deployment validation successful")
        return 0
    else:
        logger.error("Deployment validation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
