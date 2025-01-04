# File: monitoring-test.py
#!/usr/bin/env python3
# monitoring_integration_test.py
# Location: /home/ubuntu/darija_project_new/validation/scripts/monitoring_integration_test.py

import logging
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Setup paths
BASE_DIR = Path("/home/ubuntu/darija_project_new")
LOG_DIR = BASE_DIR / "logs/monitoring"
TEST_DIR = BASE_DIR / "validation/results"

class MonitoringValidator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_logging()
        self.monitoring_dir = BASE_DIR / "web/components/monitoring"
        self.results = []

    def setup_logging(self):
        """Configure logging"""
        log_file = LOG_DIR / f"monitoring_test_{self.timestamp}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("MonitoringTest")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    async def validate_monitoring_components(self):
        """Validate monitoring component files"""
        try:
            expected_files = [
                "consolidated-translation-metrics.tsx",
                "monitoring-types.ts",
            ]

            for file in expected_files:
                file_path = self.monitoring_dir / file
                if not file_path.exists():
                    self.logger.error(f"Missing monitoring file: {file}")
                    return False
                self.logger.info(f"Found monitoring file: {file}")

            # Verify monitoring configuration
            config_file = self.monitoring_dir / "metrics" / "monitoring_config.json"
            if not config_file.exists():
                self.logger.error("Missing monitoring configuration")
                return False

            self.logger.info("All required monitoring files present")
            return True

        except Exception as e:
            self.logger.error(f"Error validating monitoring components: {str(e)}")
            return False

    async def test_metrics_api(self):
        """Test metrics API endpoints"""
        try:
            from fastapi.testclient import TestClient
            from core.api.metrics_api import app

            client = TestClient(app)
            
            # Test system metrics endpoint
            response = client.get("/api/metrics/system")
            assert response.status_code == 200
            self.logger.info("System metrics API test passed")

            # Test translation metrics endpoint
            response = client.get("/api/metrics/translation")
            assert response.status_code == 200
            self.logger.info("Translation metrics API test passed")

            return True

        except Exception as e:
            self.logger.error(f"Error testing metrics API: {str(e)}")
            return False

    def save_test_results(self, results: Dict):
        """Save test results"""
        result_file = TEST_DIR / f"monitoring_test_{self.timestamp}.json"
        result_file.parent.mkdir(parents=True, exist_ok=True)

        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Test results saved to {result_file}")

    async def run_all_tests(self):
        """Run all monitoring tests"""
        try:
            self.logger.info("Starting monitoring integration tests")

            results = {
                "timestamp": self.timestamp,
                "components_valid": await self.validate_monitoring_components(),
                "api_tests_passed": await self.test_metrics_api(),
                "test_timestamp": datetime.now().isoformat()
            }

            self.save_test_results(results)
            
            success = all(results.values())
            self.logger.info(f"Tests {'passed' if success else 'failed'}")
            return success

        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return False

async def main():
    validator = MonitoringValidator()
    try:
        success = await validator.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))