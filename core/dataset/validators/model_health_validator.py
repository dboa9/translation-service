from typing import Dict, Any, Optional
from datetime import datetime
from ..dataset_validator import DatasetValidator

class ModelHealthValidator(DatasetValidator):
    """
    Validator class to handle model health validation without modifying existing code.
    Extends the base DatasetValidator to maintain compatibility.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.validation_rules = {
            "status": self._validate_status,
            "success_rate": self._validate_success_rate,
            "last_successful": self._validate_last_successful
        }

    def validate_model_health(self, health_data: Dict[str, Any], is_healthy: bool) -> bool:
        """
        Validates model health data according to specified rules
        
        Args:
            health_data: Dictionary containing model health metrics
            is_healthy: Expected health state of the model
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            # Validate status matches health state
            if not self._validate_status(health_data.get("status", ""), is_healthy):
                return False
                
            # Validate success rate
            if not self._validate_success_rate(health_data.get("success_rate", 0), is_healthy):
                return False
                
            # Validate last_successful field
            if not self._validate_last_successful(health_data.get("last_successful"), is_healthy):
                return False
                
            return True
            
        except Exception as e:
            self._log_validation_error(f"Health validation failed: {str(e)}")
            return False

    def _validate_status(self, status: str, is_healthy: bool) -> bool:
        """Validates that status matches expected health state"""
        if is_healthy:
            return status in ["healthy", "degraded"]
        return status == "unhealthy"

    def _validate_success_rate(self, rate: float, is_healthy: bool) -> bool:
        """Validates success rate matches expected health state"""
        if is_healthy:
            return rate >= 0.5  # Healthy or degraded
        return rate < 0.5  # Unhealthy

    def _validate_last_successful(self, last_successful: Optional[str], is_healthy: bool) -> bool:
        """
        Validates last_successful field matches expected health state.
        For unhealthy models, last_successful should be None.
        """
        if not is_healthy:
            return last_successful is None
        return True  # For healthy models, any value is acceptable

    def _log_validation_error(self, message: str) -> None:
        """Log validation errors"""
        # Implement logging if needed
        pass
