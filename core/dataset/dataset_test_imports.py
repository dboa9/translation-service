# File: test_imports.py
import sys
from pathlib import Path

# Redirect stdout to a file
sys.stdout = open('import_test_output.log', 'w')

# Add the project root directory to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

print(f"Current working directory: {Path.cwd()}")
print(f"__file__: {__file__}")
print(f"Project root: {project_root}")
print(f"sys.path: {sys.path}")

def test_import(module_name):
    try:
        __import__(module_name)
        print(f"Successfully imported {module_name}")
    except ImportError as e:
        print(f"Error importing {module_name}: {e}")

# Test imports
test_import("core.dataset.hf_base_loader")
test_import("core.dataset.dataset_info")
test_import("core.dataset.dataset_validator")
test_import("core.dataset.dataset_processor")
test_import("core.dataset.enhanced_hf_loader")
test_import("core.dataset.enhanced_dataset_handler")

print("Import tests completed")

# Close the file
sys.stdout.close()

# Restore stdout
sys.stdout = sys.__stdout__
