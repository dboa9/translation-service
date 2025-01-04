# File: consolidated-dataset-test.py
# dataset_loading_validation.py
# Location: /home/ubuntu/darija_project_new/validation/scripts/consolidated-dataset-test.py

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

# Import existing components
from core.monitoring.monitoring_module import ResourceMonitor
from validation.scripts.lightweight_test_runner import DatasetTester, SystemRequirements

# Setup paths
BASE_DIR = Path("/home/ubuntu/darija_project_new")
LOG_DIR = BASE_DIR / "logs"
TEST_DIR = BASE_DIR / "test_results"

class EnhancedDatasetValidator:
    def __init__(self):
        self.monitor = ResourceMonitor()
        self.tester = DatasetTester()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        LOG_FILE = LOG_DIR / f"dataset_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger = logging.getLogger("DatasetValidation")
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    async def run_validation(self):
        """Run dataset validation with monitoring"""
        try:
            self.logger.info("Starting dataset validation with monitoring...")
            
            # Start monitoring in background
            monitoring_task = asyncio.create_task(self._run_monitoring())
            
            # Check system requirements
            sys_check = SystemRequirements.check_system()
            self.logger.info(f"System check results: {sys_check}")
            
            if not sys_check["memory_sufficient"] or not sys_check["disk_sufficient"]:
                self.logger.warning("System resources below recommended specifications")
                
            # Run dataset tests
            test_results = await self._run_tests()
            
            # Combine results with monitoring data
            final_results = self._combine_results(test_results)
            
            # Save consolidated results
            self._save_results(final_results)
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            raise
        finally:
            # Cleanup
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass

    async def _run_monitoring(self):
        """Run monitoring in background"""
        while True:
            try:
                metrics = self.monitor.collect_system_metrics()
                await asyncio.sleep(5)  # 5 second interval
            except asyncio.CancelledError:
                break

    async def _run_tests(self):
        """Run dataset tests"""
        self.logger.info("Running dataset tests...")
        success = self.tester.run_tests()
        return {
            "success": success,
            "results": self.tester.results,
            "test_timestamp": datetime.now().isoformat()
        }

    def _combine_results(self, test_results: Dict) -> Dict:
        """Combine test results with monitoring data"""
        return {
            "test_results": test_results,
            "system_metrics": self.monitor.metrics_history,
            "validation_timestamp": datetime.now().isoformat()
        }

    def _save_results(self, results: Dict):
        """Save consolidated results"""
        result_file = TEST_DIR / f"dataset_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        result_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        self.logger.info(f"Validation results saved to {result_file}")

async def main():
    validator = EnhancedDatasetValidator()
    try:
        results = await validator.run_validation()
        print(f"Validation {'succeeded' if results['test_results']['success'] else 'failed'}")
        return 0 if results['test_results']['success'] else 1
    except Exception as e:
        print(f"Validation failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    asyncio.run(main())
