# File: monitoring-integration-test.py
# monitoring_integration_test.py
# Location: /home/ubuntu/darija_project_new/validation/scripts/monitoring_integration_test.py

import logging
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Import local modules
from core.monitoring.monitoring_module import ResourceMonitor
from core.utils.base_utilities_module import SystemMetrics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_integration_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MonitoringIntegrationTest:
    def __init__(self):
        self.base_dir = Path("/home/ubuntu/darija_project_new")
        self.monitor = ResourceMonitor()
        self.test_metrics: Dict[str, SystemMetrics] = {}
        
    async def generate_test_metrics(self, duration_seconds: int = 30):
        """Generate test metrics data for frontend testing"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < duration_seconds:
            try:
                metrics = self.monitor.get_system_metrics()
                
                # Add translation-specific test metrics
                metrics.translation_metrics = {
                    "bleuScore": 35.6 + (datetime.now().second % 5),
                    "translationTimeMs": 150 + (datetime.now().second * 2),
                    "successRate": 95.5 + (datetime.now().second % 3),
                    "translationsPerMinute": 60 + (datetime.now().second),
                    "totalTranslations": 1000 + (datetime.now().second * 10)
                }
                
                timestamp = datetime.now().isoformat()
                self.test_metrics[timestamp] = metrics
                
                # Save metrics to file for frontend testing
                self.save_metrics(timestamp, metrics)
                
                logger.info(f"Generated metrics for timestamp: {timestamp}")
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error generating metrics: {str(e)}")
                break
                
    def save_metrics(self, timestamp: str, metrics: SystemMetrics):
        """Save metrics to file for frontend consumption"""
        metrics_dir = self.base_dir / "web" / "public" / "test-metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        
        metrics_file = metrics_dir / f"metrics_{timestamp}.json"
        
        try:
            with open(metrics_file, 'w') as f:
                import json
                json.dump({
                    "timestamp": timestamp,
                    "metrics": metrics.to_dict()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")

async def main():
    integration_test = MonitoringIntegrationTest()
    
    logger.info("Starting monitoring integration test...")
    logger.info("This will generate 30 seconds of test metrics data")
    
    try:
        await integration_test.generate_test_metrics()
        logger.info("Test metrics generation completed")
        return 0
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    asyncio.run(main())
