from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseValidator(ABC):
    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_validation_report(self) -> Dict[str, Any]:
        pass
