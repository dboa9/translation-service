from typing import List, Dict, Any
from .validators.base_validator import BaseValidator
from .validators.specialized_validators import initialize_validators
from .config.data_paths import DataPaths

class ValidationBridge:
    def __init__(self, data_paths: DataPaths):
        self.validators: List[BaseValidator] = initialize_validators(data_paths)

    def run_all_validations(self) -> Dict[str, Any]:
        results = {}
        for validator in self.validators:
            validator_name = validator.__class__.__name__
            results[validator_name] = validator.validate()
        return results

    def get_all_validation_reports(self) -> Dict[str, Any]:
        reports = {}
        for validator in self.validators:
            validator_name = validator.__class__.__name__
            reports[validator_name] = validator.get_validation_report()
        return reports

def initialize_validation_bridge(base_dir: str) -> ValidationBridge:
    data_paths = DataPaths(base_dir)
    return ValidationBridge(data_paths)
