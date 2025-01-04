import sys
import os

def test_import(module_name):
    try:
        __import__(module_name)
        print(f"Successfully imported {module_name}")
    except ImportError as e:
        print(f"Failed to import {module_name}: {e}")
    sys.stdout.flush()  # Ensure output is immediately visible

print("Starting import tests...")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
sys.stdout.flush()

test_import('datasets')
test_import('transformers')
test_import('torch')
test_import('core.dataset.config.data_paths')
test_import('core.config_analysis.column_mapping_analyzer')

print("Import tests completed")
