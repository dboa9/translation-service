# File: test_data_preparation.py
import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

try:
    from datasets import load_dataset
except ImportError:
    print("Error: 'datasets' library not found. "
          "Please install it using 'pip install datasets'.")
    sys.exit(1)


def test_dataset_loading_and_features():
    """Test loading each dataset and examine its features."""
    datasets = [
        ("web_data", "web_data"),
        ("comments", "comments"),
        ("stories", "stories"),
        ("doda", "doda"),
        ("transliteration", "transliteration")
    ]

    results: Dict[str, Any] = {}
    for name, dataset_type in datasets:
        print(f"\nTesting dataset: {name}")
        try:
            # Load dataset
            dataset = load_dataset("atlasia/darija_english", name)
            print(f"Successfully loaded {name} dataset")
            
            # Examine features
            features = dataset['train'].features
            print(f"Features: {features}")
            
            # Check data types
            print("Data types for each feature:")
            for feature_name, feature_type in features.items():
                print(f"  {feature_name}: {feature_type}")
            
            # Sample data
            first_example = dataset['train'][0]
            print("\nFirst example:")
            for key, value in first_example.items():
                if isinstance(value, str):
                    print(f"  {key}: {value[:100]}")
                else:
                    print(f"  {key}: {value}")
            
            # Dataset statistics
            print(f"\nDataset size: {len(dataset['train'])} examples")
            
            # Verify text content
            print("\nVerifying text content...")
            for key, value in first_example.items():
                if isinstance(value, str):
                    print(f"  {key} length: {len(value)} characters")
                    print(f"  {key} sample: {value[:50]}...")

            results[name] = {
                "status": "success",
                "features": features,
                "size": len(dataset['train'])
            }

        except Exception as e:
            print(f"Error processing {name} dataset: {str(e)}")
            results[name] = {
                "status": "error",
                "error": str(e)
            }

    return results


if __name__ == "__main__":
    print("Starting dataset preparation tests...")
    results = test_dataset_loading_and_features()
    
    print("\nSummary of Results:")
    for dataset_name, result in results.items():
        status = result["status"]
        if status == "success":
            print(f"\n{dataset_name}:")
            print(f"  Status: {status}")
            print(f"  Features: {list(result['features'].keys())}")
            print(f"  Size: {result['size']} examples")
        else:
            print(f"\n{dataset_name}:")
            print(f"  Status: {status}")
            print(f"  Error: {result['error']}")
