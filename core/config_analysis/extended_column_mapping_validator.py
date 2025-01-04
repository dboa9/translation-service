import yaml
from core.config_analysis.column_mapping_validator import validate_column_mapping_structure

def validate_extended_column_mapping_structure(file_path: str):
    """
    Extends the basic column mapping structure validation with additional checks.
    """
    result = validate_column_mapping_structure(file_path)
    if not result["status"]:
        return result

    # Add extended validation checks here
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)

        if "datasets" in config:
            for dataset_name, dataset_config in config["datasets"].items():
                # Example: Check if dataset names are valid (e.g., no spaces)
                if " " in dataset_name:
                    result["status"] = False
                    result["message"] += f"Dataset name '{dataset_name}' contains spaces. "

                if isinstance(dataset_config, dict) and "required_columns" in dataset_config:
                    if not isinstance(dataset_config["required_columns"], list):
                        result["status"] = False
                        result["message"] += f"required_columns for dataset '{dataset_name}' is not a list. "
                    else:
                        for column in dataset_config["required_columns"]:
                            if not isinstance(column, str):
                                result["status"] = False
                                result["message"] += f"Invalid column name '{column}' for dataset '{dataset_name}'. "

    except yaml.YAMLError as e:
        result["status"] = False
        result["message"] = f"Error parsing YAML file: {str(e)}"
    except FileNotFoundError:
        result["status"] = False
        result["message"] = f"File not found: {file_path}"
    except Exception as e:
        result["status"] = False
        result["message"] = f"Unexpected error during extended validation: {str(e)}"

    return result

if __name__ == "__main__":
    from pathlib import Path
    config_path = Path(__file__).parent.parent.parent / "config" / "column_mapping.yaml"
    validation_result = validate_extended_column_mapping_structure(str(config_path))
    print(f"Extended validation result: {validation_result['status']}")
    print(f"Message: {validation_result['message']}")
