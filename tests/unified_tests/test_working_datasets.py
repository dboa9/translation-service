import unittest
from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

try:
    from core.dataset.integration_checker import IntegrationChecker
except ImportError:
    print("Error importing IntegrationChecker. Make sure the core module is in the Python path.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

try:
    from config.project_paths import ProjectPaths
except ImportError:
    print("Error importing ProjectPaths. Make sure the config module is in the Python path.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

class TestWorkingDatasets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            project_paths = ProjectPaths()
            config_path = project_paths.BASE_DIR / 'config' / 'newest_dataset_loader_debug.yaml'
            print(f"Config path: {config_path}")
            print(f"Config file exists: {config_path.exists()}")
            cls.integration_checker = IntegrationChecker(config_path)
        except Exception as e:
            print(f"Error in setUpClass: {e}")
            sys.exit(1)

    def test_atlasia_darija_english(self):
        dataset_name = "atlasia/darija_english"
        subsets = ["web_data", "comments", "stories", "doda", "transliteration"]
        for subset in subsets:
            with self.subTest(subset=subset):
                result = self.integration_checker.check_integration(dataset_name, subset)
                self.assertTrue(result, f"Integration check failed for {dataset_name}/{subset}")

    def test_imomayiz_darija_english(self):
        dataset_name = "imomayiz/darija-english"
        subset = "sentences"
        result = self.integration_checker.check_integration(dataset_name, subset)
        self.assertTrue(result, f"Integration check failed for {dataset_name}/{subset}")

    def test_mad_darija_bridge(self):
        dataset_name = "M-A-D/DarijaBridge"
        subset = "default"
        result = self.integration_checker.check_integration(dataset_name, subset)
        self.assertTrue(result, f"Integration check failed for {dataset_name}/{subset}")

    def test_bounhar_english_to_moroccan_darija(self):
        dataset_name = "BounharAbdelaziz/English-to-Moroccan-Darija"
        subset = "default"
        result = self.integration_checker.check_integration(dataset_name, subset)
        self.assertTrue(result, f"Integration check failed for {dataset_name}/{subset}")

if __name__ == "__main__":
    unittest.main()
