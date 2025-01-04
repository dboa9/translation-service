# File: core/utils/base_utilities_module.py

import logging
import os
import json
import gc
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import psutil

# Conditional import for torch
try:
    import torch
    from torch.cuda import get_device_properties
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch is not installed. GPU metrics will not be available.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemMetrics:
    def __init__(self):
        self.timestamp: str = datetime.now().isoformat()
        self.cpu_usage: float = 0.0
        self.memory_usage: float = 0.0
        self.disk_usage: float = 0.0
        self.gpu_metrics: Optional[Dict] = None
        self.translation_metrics: Dict = {}

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "cpu_usage": self.cpu_usage, 
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "gpu_metrics": self.gpu_metrics,
            "translation_metrics": self.translation_metrics
        }

class ResourceMonitor:
    def __init__(
        self,
        base_dir: str = None,
        disk_threshold: float = 90.0,
        memory_threshold: float = 85.0,
        log_retention_days: int = 7
    ):
        if base_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.base_dir = Path(base_dir)
        self.monitoring_dir = self.base_dir / "monitoring"
        self.metrics_dir = self.monitoring_dir / "metrics"
        self.logs_dir = self.monitoring_dir / "logs"

        # Create directories
        for directory in [self.monitoring_dir, self.metrics_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self.disk_threshold = disk_threshold
        self.memory_threshold = memory_threshold
        self.log_retention_days = log_retention_days

        # Configure logging
        self.setup_logging()

    def setup_logging(self):
        try:
            file_handler = logging.FileHandler(
                self.logs_dir / "resource_monitor.log"
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Error setting up logging: {e}")

    def check_gpu_metrics(self) -> Optional[Dict]:
        if not TORCH_AVAILABLE or not torch.cuda.is_available():
            return None

        gpu_metrics = {}
        try:
            for i in range(torch.cuda.device_count()):
                props = get_device_properties(i)
                gpu_metrics[f"gpu_{i}"] = {
                    "name": props.name,
                    "total_memory": props.total_memory,
                    "memory_allocated": torch.cuda.memory_allocated(i),
                    "memory_reserved": torch.cuda.memory_reserved(i)
                }
        except Exception as e:
            logger.error(f"Error checking GPU metrics: {e}")
        return gpu_metrics

    def get_system_metrics(self) -> SystemMetrics:
        metrics = SystemMetrics()
        
        try:
            # CPU metrics
            metrics.cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.memory_usage = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage(str(self.base_dir))
            metrics.disk_usage = disk.percent
            
            # GPU metrics
            metrics.gpu_metrics = self.check_gpu_metrics()
            
            return metrics
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            return metrics

    def save_metrics(self, metrics: SystemMetrics):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = self.metrics_dir / f"metrics_{timestamp}.json"
        
        try:
            with open(metrics_file, 'w') as f:
                json.dump(metrics.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")

    def check_resources(self) -> List[str]:
        warnings = []
        metrics = self.get_system_metrics()
        
        if metrics.disk_usage > self.disk_threshold:
            msg = f"Disk usage critical: {metrics.disk_usage}%"
            warnings.append(msg)
            logger.warning(msg)
            
        if metrics.memory_usage > self.memory_threshold:
            msg = f"Memory usage critical: {metrics.memory_usage}%"
            warnings.append(msg)
            logger.warning(msg)

        return warnings

    def cleanup(self):
        """Clean up resources and logs"""
        try:
            # Clear GPU memory
            if TORCH_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Run garbage collection
            gc.collect()
            
            logger.info("Resource cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

# You can add any additional functions or class methods here if needed

if __name__ == "__main__":
    monitor = ResourceMonitor()
    metrics = monitor.get_system_metrics()
    monitor.save_metrics(metrics)
    warnings = monitor.check_resources()
    if warnings:
        print("Resource warnings:", warnings)
    monitor.cleanup()
