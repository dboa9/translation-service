# File: cache_manager.py
#!/usr/bin/env python3
# core/dataset_management/cache_manager.py

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, List


class CacheManager:
    """Manages the dataset cache with improved deployment support."""

    def __init__(self, cache_dir: Path, max_cache_size_gb: float = 10.0):
        """Initialize the cache manager.
        
        Args:
            cache_dir: Path to the cache directory
            max_cache_size_gb: Maximum allowed cache size in GB
        """
        self.cache_dir = Path(cache_dir)
        self.max_cache_size_gb = max_cache_size_gb
        self.logger = self._setup_logging()
        self._init_cache_dir()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging with file and console handlers."""
        logger = logging.getLogger("CacheManager")
        logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"cache_manager_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(levelname)s: %(message)s')
        )
        logger.addHandler(console_handler)

        return logger

    def _init_cache_dir(self):
        """Initialize the cache directory structure."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Initialized cache directory: {self.cache_dir}")
            
            # Create necessary subdirectories
            (self.cache_dir / "downloads").mkdir(exist_ok=True)
            (self.cache_dir / "processed").mkdir(exist_ok=True)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache directory: {e}")
            raise RuntimeError(f"Cache initialization failed: {e}")

    def get_cache_size(self) -> float:
        """Get current cache size in GB."""
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(self.cache_dir):
                for filename in filenames:
                    fp = os.path.join(dirpath, filename)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
        except FileNotFoundError:
            self.logger.warning(f"Cache directory not found: {self.cache_dir}")
            return 0
        except Exception as e:
            self.logger.error(f"Error getting cache size: {e}")
            return 0
        return total_size / (1024**3)

    def get_cached_datasets(self) -> Set[str]:
        """Get list of currently cached datasets."""
        datasets = set()
        try:
            for item in self.cache_dir.glob("*"):
                if item.is_dir() and not item.name.startswith('.'):
                    datasets.add(item.name)
        except Exception as e:
            self.logger.error(f"Error getting cached datasets: {e}")
        return datasets

    def cleanup_cache(
        self,
        threshold_gb: Optional[float] = None,
        preserve: Optional[List[str]] = None
    ):
        """Clean cache if size exceeds threshold.
        
        Args:
            threshold_gb: Optional custom threshold in GB
            preserve: Optional list of dataset names to preserve
        """
        threshold = threshold_gb or self.max_cache_size_gb
        current_size = self.get_cache_size()
        preserve = preserve or []

        if current_size > threshold:
            msg = (
                f"Cache size ({current_size:.2f}GB) exceeds "
                f"threshold ({threshold:.2f}GB), cleaning up"
            )
            self.logger.warning(msg)
            
            # Get all files with their modification times
            files = []
            try:
                for f in self.cache_dir.glob("**/*"):
                    # Skip preserved datasets
                    if any(p in str(f) for p in preserve):
                        continue
                    if f.is_file():
                        files.append((f, os.path.getmtime(f)))
            except Exception as e:
                self.logger.error(f"Error scanning cache directory: {e}")
                return

            # Sort by modification time (oldest first)
            files.sort(key=lambda item: item[1])

            # Delete files until we're under threshold
            for file_path, _ in files:
                try:
                    if file_path.is_file():
                        size = os.path.getsize(file_path) / (1024**3)
                        file_path.unlink()
                        self.logger.info(
                            f"Deleted file: {file_path} ({size:.2f}GB)"
                        )
                    current_size = self.get_cache_size()
                    if current_size < threshold * 0.8:  # Keep 20% buffer
                        break
                except OSError as e:
                    self.logger.error(f"Error deleting {file_path}: {e}")

            # Clean empty directories
            self._cleanup_empty_dirs()

    def _cleanup_empty_dirs(self):
        """Remove empty directories in the cache."""
        try:
            for dirpath, dirnames, filenames in os.walk(
                self.cache_dir, topdown=False
            ):
                is_empty = not dirnames and not filenames
                is_not_root = dirpath != str(self.cache_dir)
                if is_empty and is_not_root:
                    os.rmdir(dirpath)
                    self.logger.info(f"Removed empty directory: {dirpath}")
        except Exception as e:
            self.logger.error(f"Error cleaning empty directories: {e}")

    def verify_cache_integrity(self) -> bool:
        """Verify cache integrity and clean up any corrupted files."""
        try:
            # Check for and remove incomplete downloads
            incomplete_files = list(self.cache_dir.glob("**/*.incomplete"))
            for f in incomplete_files:
                f.unlink()
                self.logger.warning(f"Removed incomplete download: {f}")

            # Check for and remove empty directories
            self._cleanup_empty_dirs()

            # Verify all files are readable
            for f in self.cache_dir.glob("**/*"):
                if f.is_file():
                    try:
                        with open(f, 'rb') as _:
                            pass
                    except Exception:
                        self.logger.error(f"Corrupted file detected: {f}")
                        f.unlink()
                        return False

            return True
        except Exception as e:
            self.logger.error(f"Error verifying cache integrity: {e}")
            return False

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        stats = {
            'total_size_gb': self.get_cache_size(),
            'datasets': list(self.get_cached_datasets()),
            'last_cleanup': None,
            'status': 'healthy'
        }
        
        try:
            file_count = sum(
                1 for _ in self.cache_dir.glob("**/*") if _.is_file()
            )
            stats['num_files'] = file_count
            stats['status'] = (
                'healthy' if self.verify_cache_integrity() else 'needs_cleanup'
            )
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            stats['status'] = 'error'
            
        return stats
