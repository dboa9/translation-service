import sys
import os
from pathlib import Path

# Add the project root to the Python path using the same method as test_import.py
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

print("\nEnvironment Information:")
print(f"Python version: {sys.version}")
print(f"Project root: {project_root}")
print(f"Current working directory: {os.getcwd()}")

print("\nDirectory Structure:")
print("Contents of project root:")
for item in project_root.iterdir():
    print(f"  - {item.name}")

print("\nContents of core/translation directory:")
translation_dir = project_root / "core" / "translation"
if translation_dir.exists():
    for item in translation_dir.iterdir():
        print(f"  - {item.name}")
else:
    print("Translation directory not found!")

print("\nTrying imports:")
# Try to import the problematic module
try:
    from core.translation.AnasAbernllb_enhanced_darija_eng_v1_1 import model
    print("Successfully imported AnasAbernllb_enhanced_darija_eng_v1_1.model")
except ImportError as e:
    print(f"Error importing AnasAbernllb_enhanced_darija_eng_v1_1.model: {e}")
    
    # Try to import the parent module
    try:
        import core.translation
        print("Successfully imported core.translation")
        print(f"Contents of core.translation: {dir(core.translation)}")
    except ImportError as e:
        print(f"Error importing core.translation: {e}")

    # Try to import the core module
    try:
        import core
        print("Successfully imported core")
        print(f"Contents of core: {dir(core)}")
    except ImportError as e:
        print(f"Error importing core: {e}")

# Check if the model file exists
model_path = translation_dir / "AnasAbernllb-enhanced-darija-eng_v1-1" / "model.py"
print(f"\nChecking for model file at: {model_path}")
if model_path.exists():
    print("Model file exists. Contents:")
    with open(model_path, 'r') as f:
        print(f.read())
else:
    print("Model file does not exist!")

print("\nPython path:")
for path in sys.path:
    print(f"  - {path}")
