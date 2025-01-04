# Pipeline Efficient Validator

This validator provides a token-efficient way to validate datasets for the Atlas-Chat-9B model while maintaining compatibility with existing tests.

## Setup

1. Ensure you have the required dependencies:
```bash
pip install transformers sentencepiece torch
```

2. Activate your conda environment:
```bash
conda activate dataset_test_deploy_ec2
```

## Usage

1. Basic usage:

```python
from core.dataset.pipeline_efficient_validator import PipelineEfficientValidator

# Initialize validator
validator = PipelineEfficientValidator(base_path="/path/to/datasets")

# Configure dataset
dataset_config = {
    "path": "relative/path/to/dataset.json",
    "type": "json",
    "name": "my_dataset"
}

# Validate efficiently
results = validator.validate_dataset_efficiently(dataset_config)
```

2. With batch size control:

```python
# Initialize with custom batch size
validator = PipelineEfficientValidator(
    base_path="/path/to/datasets",
    batch_size=16  # Adjust based on your memory constraints
)
```

3. With sample limit:

```python
# Validate only first N samples
results = validator.validate_dataset_efficiently(
    dataset_config,
    max_samples=100
)
```

## Features

1. Token Efficiency:
- Batched processing
- Structure validation before model inference
- Streaming support for large files
- Memory-efficient dataset loading

2. Test Safety:
- Extends existing validator without modifications
- Maintains test compatibility
- Proper error handling and logging

3. Format Support:
- JSON files
- JSONL files (streaming)
- Directories of JSON/JSONL files

## Best Practices

1. Token Management:
- Use appropriate batch sizes (default: 8)
- Enable streaming for large files
- Validate structure before model inference

2. Error Handling:
- Check validation results
- Monitor logs for issues
- Handle partial successes

3. Testing:
- Run provided tests before deployment
- Test with sample datasets first
- Monitor memory usage

## Example Workflow

1. Prepare your dataset in JSON or JSONL format:
```json
[
    {
        "input": "Translate to English: مرحبا كيف حالك",
        "output": "Hello, how are you?"
    },
    {
        "input": "Translate to Darija: Good morning",
        "output": "صباح الخير"
    }
]
```

2. Create validator and validate:
```python
# Initialize
validator = PipelineEfficientValidator("/path/to/datasets")

# Configure
config = {
    "path": "dataset.json",
    "type": "json",
    "name": "translation_dataset"
}

# Validate
results = validator.validate_dataset_efficiently(config)

# Check results
if results["success"]:
    print(f"Validation rate: {results['validation_rate']}")
    print(f"Valid samples: {results['valid_samples']}/{results['total_samples']}")
else:
    print(f"Validation failed: {results.get('error')}")
```

## Testing

Run the tests to ensure everything works:

```bash
pytest tests/test_pipeline_efficient_validator.py -v
```

## Notes

1. The validator uses the Atlas-Chat-9B model which requires:
   - CUDA support for GPU acceleration
   - Sufficient memory for model loading
   - Proper conda environment activation

2. For large datasets:
   - Use JSONL format for streaming support
   - Adjust batch size based on memory
   - Monitor validation progress through logs

3. Error handling:
   - Check validation results
   - Monitor logs for issues
   - Handle partial successes appropriately

This validator helps maintain token efficiency while ensuring proper dataset validation for the Atlas-Chat-9B model.
