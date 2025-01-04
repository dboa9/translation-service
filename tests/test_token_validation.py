import pytest
from datasets import Dataset
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.dataset.dataset_validator import DatasetValidator
from core.dataset.token_efficient_validator import TokenEfficientValidator

def create_test_dataset(size: int = 1000) -> Dataset:
    """Creates a test dataset with specified size."""
    return Dataset.from_dict({
        'text': [f'Example {i}' for i in range(size)],
        'label': [i % 2 for i in range(size)]
    })

def create_test_config() -> dict:
    """Creates a test configuration."""
    return {
        'datasets': {
            'test_dataset': {
                'main': {
                    'columns': ['text', 'label']
                }
            }
        }
    }

def test_basic_validation():
    """Tests basic dataset validation."""
    config = create_test_config()
    validator = DatasetValidator(config)
    dataset = create_test_dataset(100)
    
    assert validator.validate_dataset(dataset, 'test_dataset', 'main')

def test_token_efficient_validation():
    """Tests token-efficient dataset validation."""
    config = create_test_config()
    validator = TokenEfficientValidator(config)
    validator.set_chunk_size(50)  # Process in small chunks
    
    # Test with different dataset sizes
    small_dataset = create_test_dataset(100)
    assert validator.validate_dataset(small_dataset, 'test_dataset', 'main')
    
    medium_dataset = create_test_dataset(500)
    assert validator.validate_dataset(medium_dataset, 'test_dataset', 'main')

def test_invalid_dataset():
    """Tests validation with invalid dataset."""
    config = create_test_config()
    validator = TokenEfficientValidator(config)
    
    # Create dataset missing required column
    invalid_dataset = Dataset.from_dict({
        'text': ['Example 1', 'Example 2']  # Missing 'label' column
    })
    
    assert not validator.validate_dataset(invalid_dataset, 'test_dataset', 'main')

def test_chunked_processing():
    """Tests that chunked processing works correctly."""
    config = create_test_config()
    validator = TokenEfficientValidator(config)
    
    # Test with chunk sizes smaller than dataset
    validator.set_chunk_size(10)
    dataset = create_test_dataset(25)  # Should require 3 chunks
    
    assert validator.validate_dataset(dataset, 'test_dataset', 'main')

if __name__ == '__main__':
    pytest.main([__file__])
