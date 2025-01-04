import unittest
import sys
from pathlib import Path
import logging
from io import StringIO

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from tests.unified_tests.extended_test_huggingface_datasets import ExtendedTestHuggingFaceDatasets

if __name__ == "__main__":
    # Set up logging
    log_file = project_root / "logs" / "extended_huggingface_tests.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a StringIO object to capture test output
    test_output = StringIO()
    runner = unittest.TextTestRunner(stream=test_output, verbosity=2)

    # Create a test suite with the extended tests
    suite = unittest.TestLoader().loadTestsFromTestCase(ExtendedTestHuggingFaceDatasets)
    
    # Run the tests
    result = runner.run(suite)
    
    # Get the full test output
    output = test_output.getvalue()

    # Log the test output
    logging.info("Test Output:\n" + output)
    
    # Print and log a summary of the test results
    summary = f"\nTest Summary:\n"
    summary += f"Ran {result.testsRun} tests\n"
    summary += f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}\n"
    summary += f"Failures: {len(result.failures)}\n"
    summary += f"Errors: {len(result.errors)}\n"

    print(summary)
    logging.info(summary)

    # Write the full output to a separate file
    with open(project_root / "logs" / "extended_huggingface_tests_full_output.log", "w") as f:
        f.write(output)
    
    # Exit with a non-zero code if there were failures or errors
    sys.exit(len(result.failures) + len(result.errors))
