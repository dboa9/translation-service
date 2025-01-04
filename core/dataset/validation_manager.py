# File: validation_manager.py
# Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/core/dataset/validation_manager.py
# Author: dboa9 (danielalchemy9@gmail.com)
# Date: 2024-11-16

from typing import Dict, List, Optional
from pathlib import Path
from datasets import Dataset

from .validators.specialized_validators import create_validator

class ValidationManager:
    """Manages dataset validation pipeline"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir
        self.validators = {
            'structure': create_validator('structure', base_dir),
            'cache': create_validator('cache', base_dir),
            'content': create_validator('content', base_dir)
        }
        
    def validate_dataset(self, dataset_name: str, dataset: Dataset, config: str = "default") -> Dict[str, bool]:
        """Run all validations on a dataset"""
        results = {}
        
        # Structure validation
        structure_success, structure_errors = self.validators['structure'].validate(
            dataset_name, dataset, config=config
        )
        results['structure'] = structure_success
        
        # Cache validation
        cache_success, cache_errors = self.validators['cache'].validate(
            dataset_name, dataset
        )
        results['cache'] = cache_success
        
        # Content validation
        content_success, content_errors = self.validators['content'].validate(
            dataset_name, dataset
        )
        results['content'] = content_success
        
        return results