"""
System resource monitoring utilities
"""
import psutil
import logging
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    gpu_metrics: Optional[Dict[str, Dict[str, float]]] = None

class ResourceMonitor:
    """Monitors system resource usage"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system resource metrics"""
        try:
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Try to get GPU metrics if available
            gpu_metrics = self._get_gpu_metrics()
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                gpu_metrics=gpu_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {str(e)}")
            return SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0
            )
            
    def _get_gpu_metrics(self) -> Optional[Dict[str, Dict[str, float]]]:
        """Get GPU metrics if available"""
        try:
            import torch
            if torch.cuda.is_available():
                metrics = {}
                for i in range(torch.cuda.device_count()):
                    memory_allocated = torch.cuda.memory_allocated(i)
                    memory_reserved = torch.cuda.memory_reserved(i)
                    metrics[i] = {
                        'memory_allocated': memory_allocated,
                        'memory_reserved': memory_reserved
                    }
                return metrics
        except ImportError:
            pass
        except Exception as e:
            self.logger.error(f"Error getting GPU metrics: {str(e)}")
        return None
