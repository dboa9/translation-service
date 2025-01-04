from typing import Any, Dict, Optional
import logging
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir (Optional[str]): Directory to store cache files. 
                                     Defaults to project_root/cache if not specified.
        """
        if cache_dir is None:
            # Default to project_root/cache
            cache_dir = str(Path(__file__).parent.parent.parent / "cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache: Dict[str, Any] = {}
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create cache directory: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            Optional[Any]: Cached value if found, None otherwise
        """
        try:
            if key in self.cache:
                return self.cache[key]
            
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    value = json.load(f)
                self.cache[key] = value
                return value
                
        except Exception as e:
            logger.warning(f"Error reading from cache: {e}")
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
        """
        try:
            self.cache[key] = value
            
            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, 'w') as f:
                json.dump(value, f)
                
        except Exception as e:
            logger.warning(f"Error writing to cache: {e}")
    
    def clear(self) -> None:
        """Clear the in-memory cache."""
        self.cache.clear()

def initialize_cache_manager(cache_dir: Optional[str] = None) -> CacheManager:
    """
    Initialize and return a CacheManager instance.
    
    Args:
        cache_dir (Optional[str]): Directory to store cache files
        
    Returns:
        CacheManager: Initialized cache manager
    """
    return CacheManager(cache_dir)
