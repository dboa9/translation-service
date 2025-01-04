"""
Validator for handling HuggingFace model authentication and validation.
Extends the enhanced validation system while maintaining token efficiency.
"""
from typing import Dict, Any, Optional, Tuple
from datasets import Dataset
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
import logging
import os
from ..enhanced_dataset_validator import EnhancedDatasetValidator

logger = logging.getLogger(__name__)

class ModelAuthValidator(EnhancedDatasetValidator):
    """
    Validator that handles HuggingFace model authentication and validation.
    Integrates with existing validation system while adding model-specific checks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, token: Optional[str] = None):
        """
        Initialize validator with optional config and HuggingFace token.
        
        Args:
            config: Configuration dictionary
            token: HuggingFace API token
        """
        super().__init__(config or {})
        self.token = token or os.getenv('HF_TOKEN')
        self._authenticate()
        
    def _authenticate(self) -> None:
        """Attempt HuggingFace authentication if token is available."""
        if self.token:
            try:
                login(token=self.token)
                logger.info("Successfully authenticated with HuggingFace")
            except Exception as e:
                logger.error(f"Failed to authenticate with HuggingFace: {e}")
                logger.info("Some models may not be accessible without valid authentication")
    
    def validate_model(self, model_name: str, chunk_size: int = 100) -> Dict[str, Any]:
        """
        Validate a model's accessibility and functionality.
        Uses chunking for token-efficient validation.
        
        Args:
            model_name: Name/path of the model to validate
            chunk_size: Size of chunks for validation
            
        Returns:
            Dict containing validation results
        """
        try:
            # First check basic accessibility
            is_accessible = self._validate_model_access(model_name)
            if not is_accessible:
                return {
                    "status": "inaccessible",
                    "error": "Model requires authentication or does not exist",
                    "requires_auth": self._is_private_repo(model_name)
                }
            
            # Try loading model components
            model, tokenizer = self._load_model_components(model_name)
            if not model or not tokenizer:
                return {
                    "status": "load_failed",
                    "error": "Failed to load model components",
                    "requires_auth": False
                }
            
            # Validate model functionality
            validation_result = self._validate_model_functionality(
                model, tokenizer, chunk_size
            )
            
            return {
                "status": "valid" if validation_result else "invalid",
                "error": None if validation_result else "Functionality validation failed",
                "requires_auth": False,
                "components": {
                    "model": True,
                    "tokenizer": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating model {model_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "requires_auth": False
            }
    
    def _validate_model_access(self, model_name: str) -> bool:
        """Check if model can be accessed."""
        try:
            # Try loading just the tokenizer config which is lightweight
            AutoTokenizer.from_pretrained(model_name, token=self.token)
            return True
        except Exception as e:
            logger.error(f"Error accessing model {model_name}: {e}")
            return False
    
    def _is_private_repo(self, model_name: str) -> bool:
        """Check if model repository is private."""
        try:
            AutoTokenizer.from_pretrained(model_name)
            return False
        except Exception as e:
            return "private repository" in str(e).lower() or "permission to this repo" in str(e).lower()
    
    def _load_model_components(
        self, model_name: str
    ) -> Tuple[Optional[Any], Optional[Any]]:
        """Load model and tokenizer with authentication if needed."""
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, token=self.token)
            model = AutoModelForCausalLM.from_pretrained(
                model_name, token=self.token
            )
            return model, tokenizer
        except Exception as e:
            logger.error(f"Error loading model components for {model_name}: {e}")
            return None, None
    
    def _validate_model_functionality(
        self, model: Any, tokenizer: Any, chunk_size: int
    ) -> bool:
        """
        Validate model functionality using chunked processing.
        Implements token-efficient validation similar to TokenEfficientValidator.
        """
        try:
            # Create small test dataset
            test_data = Dataset.from_dict({
                "text": ["Hello, how are you?", "What is your name?"]
            })
            
            # Process in chunks
            for i in range(0, len(test_data), chunk_size):
                chunk = test_data.select(range(i, min(i + chunk_size, len(test_data))))
                
                # Basic translation test
                inputs = tokenizer(
                    chunk["text"], 
                    return_tensors="pt", 
                    padding=True, 
                    truncation=True
                )
                outputs = model.generate(**inputs)
                tokenizer.batch_decode(outputs, skip_special_tokens=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating model functionality: {e}")
            return False
    
    def validate_dataset_with_model(
        self, 
        dataset: Dataset,
        model_name: str,
        dataset_name: str,
        subset: str,
        chunk_size: int = 100
    ) -> bool:
        """
        Validate both dataset and model together.
        Combines dataset validation with model validation.
        
        Args:
            dataset: Dataset to validate
            model_name: Name of model to validate with
            dataset_name: Name of dataset
            subset: Dataset subset
            chunk_size: Size of chunks for processing
            
        Returns:
            bool indicating if validation passed
        """
        try:
            # First validate dataset
            if not super().validate_dataset(dataset, dataset_name, subset):
                return False
            
            # Then validate model
            model_validation = self.validate_model(model_name, chunk_size)
            if model_validation["status"] != "valid":
                logger.error(
                    f"Model validation failed for {model_name}: {model_validation['error']}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in combined validation: {e}")
            return False
