#Do not REMOVE LOCATION OR FILE NAME COMMENTS, EDIT IF NEEDED BUT NO REMOVAL OF THESE KINDS OF COMMENTS
# tests/unified_tests/test_column_mapping_analyzer.py
#tests/unified_tests/test_path_impact_analyzer.py
import unittest
from unittest.mock import MagicMock
from core.config_analysis.column_mapping_analyzer import ColumnMappingAnalyzer
from core.dataset.config.data_paths import DataPaths
from datasets import Dataset

class TestColumnMappingAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_paths = DataPaths("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project")
        self.analyzer = ColumnMappingAnalyzer(self.data_paths)

    def test_analyze_column_mapping(self):
        mock_dataset = Dataset.from_dict({"english": ["Hello"], "darija": ["Salam"], "source": ["test"]})
        result = self.analyzer.analyze_column_mapping("atlasia/darija_english", mock_dataset, "web_data")
        self.assertEqual(result["status"], True)

    def test_preprocess_dataset(self):
        mock_dataset = Dataset.from_dict({"english": ["Hello"], "darija": ["Salam"], "source": ["test"]})
        preprocessed = self.analyzer.preprocess_dataset(mock_dataset, "atlasia/darija_english", "web_data")
        self.assertEqual(preprocessed, mock_dataset)  # Assuming no preprocessing is needed for this dataset

if __name__ == "__main__":
    unittest.main()


import unittest
import tempfile
import os
from pathlib import Path
from core.utils.file_utils import ensure_directory_exists, write_file_content

class TestImpactAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        # Clean up temporary files after tests
        import shutil
        shutil.rmtree(self.test_dir)

    def _create_test_file(self, relative_path: str, content: str) -> Path:
        """Helper method to create test files with given content."""
        file_path = Path(self.test_dir) / relative_path
        ensure_directory_exists(file_path.parent)
        write_file_content(file_path, content)
        return file_path

    def test_analyze_imports(self):
        """Test import analysis functionality."""
        # Create test files
        main_content = """
        import os
        from data.processor import process_data
        from utils.helper import format_output
        """
        self._create_test_file("main.py", main_content)

        processor_content = """
        from utils.helper import validate_input
        def process_data(data):
            return validate_input(data)
        """
        self._create_test_file("data/processor.py", processor_content)

        helper_content = """
        def validate_input(data):
            return bool(data)
        def format_output(data):
            return str(data)
        """
        self._create_test_file("utils/helper.py", helper_content)

    def test_analyze_references(self):
        """Test file reference analysis."""
        # Create test files with references
        main_content = """
        import os
        from data.processor import process_data
        from utils.helper import format_output
        """
        self._create_test_file("main.py", main_content)

        processor_content = """
        from utils.helper import validate_input
        def process_data(data):
            return validate_input(data)
        """
        self._create_test_file("data/processor.py", processor_content)

    def test_find_redundant_files(self):
        """Test identification of redundant files."""
        # Create test files
        files = [
            ("utils/helper.py", "def helper(): pass"),
            ("data/processor.py", "def process(): pass"),
            ("main.py", "def main(): pass")
        ]
        for path, content in files:
            self._create_test_file(path, content)

    def test_generate_report(self):
        """Test report generation."""
        # Create test files
        files = [
            ("utils/helper.py", "def helper(): pass"),
            ("data/processor.py", "def process(): pass"),
            ("main.py", "def main(): pass")
        ]
        for path, content in files:
            self._create_test_file(path, content)

    def test_path_changes(self):
        """Test impact analysis for specific path changes."""
        # Create test files
        main_content = """
        import os
        from data.processor import process_data
        from utils.helper import format_output
        """
        self._create_test_file("main.py", main_content)

        processor_content = """
        from utils.helper import validate_input
        def process_data(data):
            return validate_input(data)
        """
        self._create_test_file("data/processor.py", processor_content)

    def test_save_report(self):
        """Test report saving functionality."""
        report_dir = Path(self.test_dir) / "reports"
        ensure_directory_exists(report_dir)
        
        # Create a sample report
        report_content = {
            "analyzed_files": ["main.py", "data/processor.py"],
            "import_dependencies": {
                "main.py": ["os", "data.processor", "utils.helper"],
                "data/processor.py": ["utils.helper"]
            }
        }
        
        # Save report
        import json
        report_path = report_dir / f"impact_analysis_{Path(__file__).stem}.json"
        with open(report_path, 'w') as f:
            json.dump(report_content, f, indent=2)
        
        self.assertTrue(report_path.exists())
        with open(report_path) as f:
            loaded_report = json.load(f)
        self.assertEqual(loaded_report, report_content)

if __name__ == '__main__':
    unittest.main()
