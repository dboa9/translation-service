"""
Tests for EnhancedTorchValidator

This test suite demonstrates how to use the EnhancedTorchValidator
to handle torch.classes warnings while maintaining dataset validation functionality.
"""
import pytest
from datasets import Dataset
import pandas as pd
import warnings

from core.dataset.dataset_validator import DatasetValidator
from core.dataset.enhanced_torch_validator import EnhancedTorchValidator

def test_warning_suppression():
    """Test that torch warnings are properly suppressed"""
    validator = EnhancedTorchValidator()
    
    # The warning should be suppressed
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        validator.validate_torch_operations()
        # No warnings should be recorded
        assert len([x for x in w if "torch.classes" in str(x.message)]) == 0

def test_create_validator():
    """Test validator creation with different types"""
    # Test creating enhanced validator
    validator = EnhancedTorchValidator.create_validator("enhanced")
    assert isinstance(validator, EnhancedTorchValidator)
    
    # Test creating standard validator
    validator = EnhancedTorchValidator.create_validator("standard")
    assert isinstance(validator, DatasetValidator)
    assert not isinstance(validator, EnhancedTorchValidator)

def test_validate_torch_operations():
    """Test basic torch operations validation"""
    validator = EnhancedTorchValidator()
    assert validator.validate_torch_operations() is True

def test_validate_dataset():
    """Test dataset validation with proper columns"""
    # Create a simple test dataset
    data = {
        'text': ['Hello', 'World'],
        'label': [0, 1]
    }
    df = pd.DataFrame(data)
    dataset = Dataset.from_pandas(df)
    
    # Create validator with test config
    config = {
        'datasets': {
            'test_dataset': {
                'test_subset': {
                    'columns': ['text', 'label']
                }
            }
        }
    }
    validator = EnhancedTorchValidator(config)
    
    # Validation should pass with all required columns present
    assert validator.validate_dataset(dataset, 'test_dataset', 'test_subset') is True

def test_validate_dataset_missing_columns():
    """Test dataset validation with missing columns"""
    # Create dataset missing required columns
    data = {'text': ['Hello', 'World']}  # Missing 'label' column
    df = pd.DataFrame(data)
    dataset = Dataset.from_pandas(df)
    
    # Create validator requiring additional columns
    config = {
        'datasets': {
            'test_dataset': {
                'test_subset': {
                    'columns': ['text', 'label']
                }
            }
        }
    }
    validator = EnhancedTorchValidator(config)
    
    # Validation should fail due to missing column
    assert validator.validate_dataset(dataset, 'test_dataset', 'test_subset') is False

def test_validate_split():
    """Test split validation functionality"""
    # Create test dataset
    data = {
        'text': ['Hello', 'World'],
        'label': [0, 1]
    }
    df = pd.DataFrame(data)
    dataset = Dataset.from_pandas(df)
    
    # Create validator with test config
    config = {
        'datasets': {
            'test_dataset': {
                'test_subset': {
                    'columns': ['text', 'label']
                }
            }
        }
    }
    validator = EnhancedTorchValidator(config)
    
    # Split validation should pass with all required columns
    assert validator._validate_split(dataset, 'test_dataset', 'test_subset', 'train') is True

def test_error_handling():
    """Test error handling for invalid inputs"""
    validator = EnhancedTorchValidator()
    
    # Test with None dataset
    with pytest.raises(ValueError, match="Dataset cannot be None"):
        validator.validate_dataset(None, 'test_dataset', 'test_subset')
    
    # Test with invalid dataset type
    with pytest.raises(ValueError, match="Expected Dataset or DatasetDict"):
        validator.validate_dataset({}, 'test_dataset', 'test_subset')
    
    # Test with None split dataset
    with pytest.raises(ValueError, match="Split dataset cannot be None"):
        validator._validate_split(None, 'test_dataset', 'test_subset', 'train')
    
    # Test with invalid split dataset type
    with pytest.raises(ValueError, match="Expected Dataset"):
        validator._validate_split({}, 'test_dataset', 'test_subset', 'train')

def test_graceful_error_handling():
    """Test graceful handling of non-critical errors"""
    validator = EnhancedTorchValidator()
    
    # Create an invalid dataset that will cause non-critical errors
    data = {'text': [None, None]}  # Invalid data that might cause processing errors
    df = pd.DataFrame(data)
    dataset = Dataset.from_pandas(df)
    
    # Should return False but not raise exception for non-critical errors
    assert validator.validate_dataset(dataset, 'invalid', 'invalid') is False
    assert validator._validate_split(dataset, 'invalid', 'invalid', 'invalid') is False
