"""
Tests for the ModelAuthValidator class.
"""
import unittest
from unittest.mock import patch, MagicMock
from datasets import Dataset
from core.dataset.validators.model_auth_validator import ModelAuthValidator

class TestModelAuthValidator(unittest.TestCase):
    """Test cases for ModelAuthValidator."""
    
    def setUp(self):
        self.validator = ModelAuthValidator()
        self.test_model = "test/model"
    
    @patch('core.dataset.validators.model_auth_validator.login')
    def test_authentication(self, mock_login):
        """Test HuggingFace authentication."""
        token = "test_token"
        validator = ModelAuthValidator(token=token)
        mock_login.assert_called_once_with(token=token)
    
    @patch('core.dataset.validators.model_auth_validator.AutoTokenizer')
    def test_model_access_validation(self, mock_tokenizer):
        """Test model access validation."""
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        
        # Test successful access
        result = self.validator._validate_model_access(self.test_model)
        self.assertTrue(result)
        mock_tokenizer.from_pretrained.assert_called_once()
        
        # Test failed access
        mock_tokenizer.from_pretrained.side_effect = Exception("Access denied")
        result = self.validator._validate_model_access("private/model")
        self.assertFalse(result)
    
    @patch('core.dataset.validators.model_auth_validator.AutoTokenizer')
    @patch('core.dataset.validators.model_auth_validator.AutoModelForCausalLM')
    def test_model_component_loading(self, mock_model, mock_tokenizer):
        """Test loading model components."""
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()
        
        model, tokenizer = self.validator._load_model_components(self.test_model)
        self.assertIsNotNone(model)
        self.assertIsNotNone(tokenizer)
        
        # Test failed loading
        mock_tokenizer.from_pretrained.side_effect = Exception("Loading failed")
        model, tokenizer = self.validator._load_model_components("error/model")
        self.assertIsNone(model)
        self.assertIsNone(tokenizer)
    
    def test_private_repo_detection(self):
        """Test private repository detection."""
        with patch('core.dataset.validators.model_auth_validator.AutoTokenizer') as mock:
            # Test public repo
            mock.from_pretrained.return_value = MagicMock()
            self.assertFalse(self.validator._is_private_repo(self.test_model))
            
            # Test private repo
            mock.from_pretrained.side_effect = Exception(
                "Model is not accessible. It might be a private repository."
            )
            self.assertTrue(self.validator._is_private_repo("private/model"))
    
    @patch('core.dataset.validators.model_auth_validator.AutoTokenizer')
    @patch('core.dataset.validators.model_auth_validator.AutoModelForCausalLM')
    def test_model_validation(self, mock_model, mock_tokenizer):
        """Test full model validation."""
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()
        
        # Test successful validation
        result = self.validator.validate_model(self.test_model)
        self.assertEqual(result["status"], "valid")
        
        # Test inaccessible model
        mock_tokenizer.from_pretrained.side_effect = Exception("Access denied")
        result = self.validator.validate_model("private/model")
        self.assertEqual(result["status"], "inaccessible")
    
    def test_combined_validation(self):
        """Test combined dataset and model validation."""
        dataset = Dataset.from_dict({
            "text": ["Example 1", "Example 2"],
            "label": [0, 1]
        })
        
        with patch.object(ModelAuthValidator, 'validate_model') as mock_validate:
            mock_validate.return_value = {"status": "valid", "error": None}
            
            # Test successful validation
            result = self.validator.validate_dataset_with_model(
                dataset, self.test_model, "test_dataset", "main"
            )
            self.assertTrue(result)
            
            # Test failed model validation
            mock_validate.return_value = {
                "status": "error",
                "error": "Validation failed"
            }
            result = self.validator.validate_dataset_with_model(
                dataset, "error/model", "test_dataset", "main"
            )
            self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
