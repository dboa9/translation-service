"""
Tests for the PipelineEfficientValidator class.
"""
import pytest
from pathlib import Path
import json
import torch
from core.dataset.pipeline_efficient_validator import PipelineEfficientValidator

@pytest.fixture
def validator(tmp_path):
    """Create a validator instance with a temporary directory."""
    return PipelineEfficientValidator(str(tmp_path))

@pytest.fixture
def sample_dataset(tmp_path):
    """Create a sample dataset for testing."""
    dataset = [
        {
            "input": "Translate to English: مرحبا كيف حالك",
            "output": "Hello, how are you?"
        },
        {
            "input": "Translate to Darija: Good morning",
            "output": "صباح الخير"
        }
    ]
    
    # Save as JSON
    json_path = tmp_path / "dataset.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False)
        
    return json_path

def test_validator_initialization(validator):
    """Test validator initialization."""
    assert validator is not None
    assert validator.batch_size == 8
    assert validator.model_name == "MBZUAI-Paris/Atlas-Chat-9B"

def test_sample_structure_validation(validator):
    """Test sample structure validation."""
    valid_sample = {
        "input": "Test input",
        "output": "Test output"
    }
    invalid_sample = {
        "input": "Test input"
        # Missing output
    }
    
    assert validator._validate_sample_structure(valid_sample)
    assert not validator._validate_sample_structure(invalid_sample)

def test_dataset_loading(validator, sample_dataset):
    """Test dataset loading functionality."""
    dataset_config = {
        "path": str(sample_dataset.relative_to(validator.base_path)),
        "type": "json"
    }
    
    samples = validator._load_dataset_samples(sample_dataset)
    assert len(samples) == 2
    assert all("input" in sample and "output" in sample for sample in samples)

@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_pipeline_initialization(validator):
    """Test pipeline initialization (skip if CUDA not available)."""
    success = validator.initialize_pipeline()
    assert success
    assert validator.pipe is not None

def test_efficient_validation(validator, sample_dataset):
    """Test efficient dataset validation."""
    dataset_config = {
        "path": str(sample_dataset.relative_to(validator.base_path)),
        "type": "json",
        "name": "test_dataset"
    }
    
    results = validator.validate_dataset_efficiently(dataset_config, max_samples=1)
    assert results["success"]
    assert "total_samples" in results
    assert "valid_samples" in results
    assert "validation_rate" in results

def test_batch_validation(validator):
    """Test batch validation functionality."""
    samples = [
        {
            "input": "Test input 1",
            "output": "Test output 1"
        },
        {
            "input": "Test input 2",
            "output": "Test output 2"
        }
    ]
    
    results = validator.validate_batch(samples)
    assert len(results) == len(samples)
    assert all(isinstance(result, bool) for result in results)

@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_model_integration(validator):
    """Test actual model integration (skip if CUDA not available)."""
    success = validator.initialize_pipeline()
    assert success
    
    sample = {
        "input": "Translate to English: مرحبا",
        "output": "Hello"
    }
    
    results = validator.validate_batch([sample])
    assert len(results) == 1
    assert isinstance(results[0], bool)
