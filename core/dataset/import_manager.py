# core/dataset/import_manager.py

import importlib
import os
from typing import List, Optional, Tuple, Any


def get_latest_module(base_name: str, directory: Optional[str] = None) -> Any:
    if directory is None:
        directory = os.path.dirname(__file__)
    
    def find_module(dir: str) -> Tuple[Optional[str], List[str]]:
        files = [f for f in os.listdir(dir) if f.startswith(base_name) and f.endswith('.py')]
        if files:
            return dir, files
        for subdir in os.listdir(dir):
            subdir_path = os.path.join(dir, subdir)
            if os.path.isdir(subdir_path):
                subdir_files = [f for f in os.listdir(subdir_path) if f.startswith(base_name) and f.endswith('.py')]
                if subdir_files:
                    return subdir_path, subdir_files
        return None, []

    # Look in the current directory and its subdirectories
    found_dir, files = find_module(directory)
    
    # If not found, look in the parent directory
    if not files and found_dir is None:
        parent_dir = os.path.dirname(directory)
        found_dir, files = find_module(parent_dir)
    
    if not files or found_dir is None:
        raise ImportError(f"No module found starting with {base_name} in {directory}, its subdirectories, or parent directory")
    
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(found_dir, f)))
    module_name = latest_file[:-3]  # Remove .py extension
    
    if found_dir == directory:
        return importlib.import_module(f".{module_name}", package=__package__)
    elif found_dir == os.path.dirname(directory):
        return importlib.import_module(f"..{module_name}", package=__package__)
    else:
        relative_path = os.path.relpath(found_dir, directory).replace(os.path.sep, '.')
        return importlib.import_module(f".{relative_path}.{module_name}", package=__package__)

# Import modules
data_reader = get_latest_module('data_reader')
base_loader = get_latest_module('base_loader')
data_paths = get_latest_module('data_paths')

# Export classes and functions
DataReader = data_reader.DataReader
BaseLoader = base_loader.BaseLoader

# Lazy imports for ModernDatasetHandler and DatasetHandlerFactory
def get_ModernDatasetHandler():
    return get_latest_module('modern_dataset_handler').ModernDatasetHandler

def get_DatasetHandlerFactory():
    return get_latest_module('dataset_handler_factory').DatasetHandlerFactory

# Add any other classes or functions you need to export
