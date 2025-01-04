import yaml
from pathlib import Path
from typing import Dict, Any

def validate_column_mapping_structure(file_path: str) -> Dict[str, Any]:
    """
    Validate the structure of the column_mapping.yaml file.
    
    Args:
    file_path (str): Path to the column_mapping.yaml file.
    
    Returns:
    Dict[str, Any]: A dictionary containing the validation result and any error messages.
    """
    result = {"status": True, "message": ""}
    
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Check if the file is empty
        if not config:
            result["status"] = False
            result["message"] = "The column_mapping.yaml file is empty."
            return result
        
        # Check for required top-level keys
        required_keys = ["datasets", "column_types", "validation_rules"]
        for key in required_keys:
            if key not in config:
                result["status"] = False
                result["message"] += f"Missing required key: {key}. "
        
        # Check the structure of the 'datasets' section
        if "datasets" in config:
            for dataset, dataset_config in config["datasets"].items():
                if not isinstance(dataset_config, dict):
                    result["status"] = False
                    result["message"] += f"Invalid structure for dataset {dataset}. "
                else:
                    required_dataset_keys = ["subsets", "required_columns"]
                    for key in required_dataset_keys:
                        if key not in dataset_config:
                            result["status"] = False
                            result["message"] += f"Missing required key '{key}' for dataset {dataset}. "
        
        # Add more specific checks as needed
        
        if result["status"]:
            result["message"] = "Column mapping structure is valid."
        
    except yaml.YAMLError as e:
        result["status"] = False
        result["message"] = f"Error parsing YAML file: {str(e)}"
    except FileNotFoundError:
        result["status"] = False
        result["message"] = f"File not found: {file_path}"
    except Exception as e:
        result["status"] = False
        result["message"] = f"Unexpected error: {str(e)}"
    
    return result

if __name__ == "__main__":
    config_path = Path(__file__).parent.parent.parent / "config" / "column_mapping.yaml"
    validation_result = validate_column_mapping_structure(str(config_path))
    print(f"Validation result: {validation_result['status']}")
    print(f"Message: {validation_result['message']}")
