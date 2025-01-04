# File: validation_config.py
from typing import Any, Dict


class ValidationConfig:
    """Configuration for dataset validation"""
    
    def __init__(
        self,
        min_length: int = 1,
        max_length: int = 1000,
        allowed_characters: str = r'[\w\s.,!?-]+'
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.allowed_characters = allowed_characters

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ValidationConfig':
        """Create config from dictionary"""
        return cls(
            min_length=config.get('min_length', 1),
            max_length=config.get('max_length', 1000),
            allowed_characters=config.get(
                'allowed_characters',
                r'[\w\s.,!?-]+'
            )
        )