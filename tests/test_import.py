import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

print(f"Python version: {sys.version}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Contents of project root: {list(project_root.iterdir())}")
print(f"Contents of core directory: {list((project_root / 'core').iterdir())}")
print(f"Contents of core/dataset directory: {list((project_root / 'core' / 'dataset').iterdir())}")

try:
    from core.dataset.dataset_wrapper_adapter import DatasetWrapperAdapter
    print("Successfully imported DatasetWrapperAdapter")
    print(f"DatasetWrapperAdapter: {DatasetWrapperAdapter}")
except ImportError as e:
    print(f"Error importing DatasetWrapperAdapter: {e}")
    
    # Try to import the parent module
    try:
        import core.dataset
        print(f"Successfully imported core.dataset")
        print(f"Contents of core.dataset: {dir(core.dataset)}")
    except ImportError as e:
        print(f"Error importing core.dataset: {e}")

    # Try to import the core module
    try:
        import core
        print(f"Successfully imported core")
        print(f"Contents of core: {dir(core)}")
    except ImportError as e:
        print(f"Error importing core: {e}")
