from typing import Dict, Any, Optional, List, Union
import yaml
from pathlib import Path
from datasets import Dataset
import logging

logger = logging.getLogger(__name__)

def load_column_mapping(base_dir: Optional[str] = None) -> Dict[str, Any]:
    """Load column mapping configuration from YAML file"""
    try:
        config_path = Path(base_dir) / "config" / "column_mapping.yaml" if base_dir else Path("config/column_mapping.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading column mapping config: {str(e)}")
        return {}

def get_required_columns(mapping: Dict[str, Any], dataset_name: str, config: Optional[str]) -> List[str]:
    """Get required columns for a dataset and config"""
    try:
        dataset_config = mapping['datasets'].get(dataset_name, {})
        if not config or config == 'default':
            # If no config specified or default, use first subset's columns
            first_subset = next(iter(dataset_config.get('required_columns', {}).keys()))
            return dataset_config.get('required_columns', {}).get(first_subset, [])
        return dataset_config.get('required_columns', {}).get(config, [])
    except Exception as e:
        logger.error(f"Error getting required columns: {str(e)}")
        return []

def is_multiple_columns_allowed(mapping: Dict[str, Any], dataset_name: str, config: str, col_type: str) -> bool:
    """Check if multiple columns are allowed for a specific column type"""
    try:
        # Check dataset-specific multiple columns configuration
        dataset_config = mapping['datasets'].get(dataset_name, {})
        multiple_allowed = dataset_config.get('multiple_columns_allowed', {})
        if config in multiple_allowed and col_type in multiple_allowed[config]:
            return True
            
        # Check global special cases
        special_cases = mapping.get('special_cases', {}).get('multiple_columns_allowed', {})
        if col_type in special_cases and special_cases[col_type]:
            return True
            
        return False
    except Exception:
        return False

def has_special_validation(mapping: Dict[str, Any], dataset_name: str, config: Optional[str]) -> bool:
    """Check if dataset has special validation rules"""
    try:
        dataset_config = mapping['datasets'].get(dataset_name, {})
        special_validation = dataset_config.get('special_validation', {})
        return config in special_validation
    except Exception:
        return False

def validate_special_case(mapping: Dict[str, Any], dataset: Dataset, dataset_name: str, config: str) -> Dict[str, Any]:
    """Validate dataset using special validation rules"""
    try:
        special_validation = mapping['datasets'][dataset_name]['special_validation'][config]
        required_columns = special_validation.get('required_columns', [])
        actual_columns = list(dataset.features.keys())
        
        # Check if all specially required columns are present
        missing_columns = [col for col in required_columns if col not in actual_columns]
        
        if missing_columns:
            return {
                "status": False,
                "message": f"Missing required columns for {dataset_name} ({config}): {', '.join(missing_columns)}",
                "columns": actual_columns,
                "missing_columns": missing_columns
            }
            
        return {
            "status": True,
            "message": f"Column validation passed for {dataset_name} ({config})",
            "columns": actual_columns
        }
    except Exception as e:
        logger.error(f"Error in special validation: {str(e)}")
        return {
            "status": False,
            "message": f"Special validation error for {dataset_name}: {str(e)}",
            "columns": []
        }

def validate_columns(dataset: Dataset, dataset_name: str, config: Optional[str] = None, split_name: Optional[str] = None) -> Dict[str, Any]:
    """Validate dataset columns against mapping configuration"""
    try:
        # Load column mapping configuration
        mapping = load_column_mapping()
        if not mapping:
            return {
                "status": False,
                "message": "Failed to load column mapping configuration",
                "columns": []
            }

        # Check for special validation rules first
        if has_special_validation(mapping, dataset_name, config):
            return validate_special_case(mapping, dataset, dataset_name, config)

        # Get actual columns from dataset
        actual_columns = list(dataset.features.keys())
        
        # Get required columns from mapping
        required_columns = get_required_columns(mapping, dataset_name, config)
        
        # Check if all required columns are present
        missing_columns = [col for col in required_columns if col not in actual_columns]
        
        if missing_columns:
            return {
                "status": False,
                "message": f"Missing required columns for {dataset_name}" + 
                          (f" ({config})" if config else "") +
                          f": {', '.join(missing_columns)}",
                "columns": actual_columns,
                "missing_columns": missing_columns
            }

        # Validate column types if specified in mapping
        column_types = mapping.get('column_types', {})
        invalid_columns = []
        
        for col_type, valid_names in column_types.items():
            columns_of_type = [col for col in actual_columns if col in valid_names]
            if len(columns_of_type) > 1 and not is_multiple_columns_allowed(mapping, dataset_name, config or 'default', col_type):
                invalid_columns.append(f"Multiple {col_type} columns found: {', '.join(columns_of_type)}")
        
        if invalid_columns:
            return {
                "status": False,
                "message": f"Column type validation failed for {dataset_name}" +
                          (f" ({config})" if config else "") +
                          f": {'; '.join(invalid_columns)}",
                "columns": actual_columns,
                "invalid_columns": invalid_columns
            }

        # Apply validation rules
        validation_rules = mapping.get('validation_rules', {})
        required_types = validation_rules.get('required_columns', [])
        allowed_extra = validation_rules.get('allowed_extra_columns', [])
        
        # Check if required column types are present
        for req_type in required_types:
            type_columns = column_types.get(req_type, [])
            if not any(col in actual_columns for col in type_columns):
                return {
                    "status": False,
                    "message": f"Missing required column type '{req_type}' for {dataset_name}" +
                              (f" ({config})" if config else ""),
                    "columns": actual_columns
                }

        # Validate extra columns
        extra_columns = set(actual_columns) - set(required_columns)
        invalid_extra = []
        for col in extra_columns:
            is_allowed = False
            # Check if column is in any of the allowed types
            for allowed_type in allowed_extra:
                if col in column_types.get(allowed_type, []):
                    is_allowed = True
                    break
            # Also check if column is in any valid column type
            for valid_names in column_types.values():
                if col in valid_names:
                    is_allowed = True
                    break
            if not is_allowed:
                invalid_extra.append(col)

        if invalid_extra:
            return {
                "status": False,
                "message": f"Invalid extra columns found for {dataset_name}" +
                          (f" ({config})" if config else "") +
                          f": {', '.join(invalid_extra)}",
                "columns": actual_columns,
                "invalid_extra": invalid_extra
            }

        return {
            "status": True,
            "message": f"Column validation passed for {dataset_name}" + 
                      (f" ({config})" if config else "") +
                      (f" ({split_name})" if split_name else ""),
            "columns": actual_columns
        }

    except Exception as e:
        logger.error(f"Error during column validation: {str(e)}")
        return {
            "status": False,
            "message": f"Validation error for {dataset_name}: {str(e)}",
            "columns": []
        }
