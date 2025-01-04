import subprocess
import sys
import time
import psutil
import logging
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def monitor_resources() -> Dict[str, float]:
    """Monitor system resources during test execution."""
    process = psutil.Process()
    return {
        'cpu_percent': process.cpu_percent(),
        'memory_percent': process.memory_percent(),
        'memory_mb': process.memory_info().rss / 1024 / 1024
    }

def run_tests_with_monitoring():
    """Run translation tests with resource monitoring."""
    start_time = time.time()
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'environment': 'local',
        'resources': [],
        'status': 'running',
        'duration': 0,
        'errors': []
    }
    
    try:
        # Create logs directory if it doesn't exist
        Path('logs').mkdir(exist_ok=True)
        
        # Start monitoring resources
        logger.info("Starting test execution with monitoring...")
        
        # Run pytest with output capture
        process = subprocess.Popen(
            [
                'python', '-m', 'pytest',
                'tests/test_all_models_translation.py',
                '-v',
                '--log-cli-level=INFO',
                '--log-file=logs/test_execution.log'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor resources while tests are running
        while process.poll() is None:
            resources = monitor_resources()
            test_results['resources'].append({
                'timestamp': time.time() - start_time,
                **resources
            })
            
            # Log resource usage
            logger.info(
                f"CPU: {resources['cpu_percent']:.1f}% | "
                f"Memory: {resources['memory_mb']:.1f}MB "
                f"({resources['memory_percent']:.1f}%)"
            )
            
            time.sleep(1)  # Check every second
            
        # Get test output
        stdout, stderr = process.communicate()
        
        # Update test results
        test_results.update({
            'status': 'completed' if process.returncode == 0 else 'failed',
            'duration': time.time() - start_time,
            'return_code': process.returncode
        })
        
        if stdout:
            logger.info("Test Output:")
            logger.info(stdout)
            
        if stderr:
            logger.error("Test Errors:")
            logger.error(stderr)
            test_results['errors'].append(stderr)
            
        # Save test results
        results_file = f'logs/test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
            
        logger.info(f"Test execution completed in {test_results['duration']:.1f} seconds")
        logger.info(f"Results saved to {results_file}")
        
        # Print summary
        print("\n=== Test Execution Summary ===")
        print(f"Status: {test_results['status']}")
        print(f"Duration: {test_results['duration']:.1f} seconds")
        print(f"Peak Memory Usage: {max(r['memory_mb'] for r in test_results['resources']):.1f}MB")
        print(f"Detailed results saved to: {results_file}")
        
        return process.returncode
        
    except Exception as e:
        logger.error(f"Error during test execution: {str(e)}")
        test_results.update({
            'status': 'error',
            'duration': time.time() - start_time,
            'errors': [str(e)]
        })
        return 1

if __name__ == '__main__':
    sys.exit(run_tests_with_monitoring())
