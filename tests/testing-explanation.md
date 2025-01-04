# Testing System Explanation

## Understanding `python -m unittest`
- This is Python's built-in testing framework
- Your existing tests in `tests/unified_tests/` are already structured for unittest
- When you run `python -m unittest discover`, it automatically finds and runs all test files that start with `test_`

## Your Current Test Structure
```bash
tests/
└── unified_tests/
    ├── test_atlasia_hf_loading.py      # Tests for Hugging Face dataset loading
    ├── test_dataset_loading.py         # General dataset loading tests
    ├── test_path_impact_analyzer.py    # Tests for the path analyzer
    └── ...
```

## Coverage Testing
Coverage testing shows how much of your code is tested. Here's how to use it:

```bash
# Install coverage
pip install coverage

# Run coverage analysis
coverage run -m unittest discover

# View report in terminal
coverage report

# Generate HTML report
coverage html
```

The HTML report will be in `htmlcov/index.html` and shows which lines of code were tested.

## Test Types in Your Project
1. Dataset Loading Tests:
   - test_atlasia_loading.py
   - test_dataset_loading.py
   - test_huggingface_datasets.py

2. Path Analysis Tests:
   - test_path_impact_analyzer.py

3. Integration Tests:
   - test_working_datasets.py

## Running Specific Test Groups
```bash
# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest tests/unified_tests/test_path_impact_analyzer.py

# Run tests with coverage
coverage run -m unittest tests/unified_tests/test_path_impact_analyzer.py
```
