import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

print("Current sys.path:")
for path in sys.path:
    print(f"  {path}")

print("\nTrying to import core.dataset...")
try:
    import core.dataset
    print("core.dataset imported successfully")
    print(f"core.dataset.__file__: {core.dataset.__file__}")
    print("Contents of core.dataset:")
    for item in dir(core.dataset):
        print(f"  {item}")
except ImportError as e:
    print(f"Error importing core.dataset: {e}")
    import traceback
    traceback.print_exc()

print("\nTrying to import HFBaseLoaderWrapper...")
try:
    from core.dataset import HFBaseLoaderWrapper
    print("HFBaseLoaderWrapper imported successfully")
except ImportError as e:
    print(f"Error importing HFBaseLoaderWrapper: {e}")
    import traceback
    traceback.print_exc()

print("\nContents of core/dataset directory:")
for item in Path(project_root / 'core' / 'dataset').iterdir():
    print(f"  {item}")
