import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from core.dataset.config.data_paths import DataPaths
from core.config_analysis.column_mapping_analyzer import ColumnMappingAnalyzer
from core.dataset.hf_base_loader import HFBaseLoader

class TestComprehensiveDatasetValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = project_root
        cls.data_paths = DataPaths(str(cls.base_dir))
        cls.analyzer = ColumnMappingAnalyzer(cls.data_paths)
        cls.loader = HFBaseLoader(base_dir=str(cls.base_dir))

    def test_all_datasets(self):
        datasets = [
            ("atlasia/darija_english", "web_data"),
            ("atlasia/darija_english", "comments"),
            ("atlasia/darija_english", "stories"),
            ("atlasia/darija_english", "doda"),
            ("atlasia/darija_english", "transliteration"),
            ("imomayiz/darija-english", "sentences"),
            ("M-A-D/DarijaBridge", None),
            ("BounharAbdelaziz/English-to-Moroccan-Darija", None),
        ]

        for dataset_name, subset in datasets:
            with self.subTest(dataset=dataset_name, subset=subset):
                dataset = self.loader.load_dataset(dataset_name, subset)
                result = self.analyzer.analyze_column_mapping(dataset_name, dataset, subset)
                self.assertTrue(result["status"], f"Validation failed for {dataset_name} ({subset}): {result['message']}")

    @patch('core.config_analysis.column_mapping_analyzer.load_yaml_config')
    def test_config_consistency(self, mock_load_yaml_config):
        mock_config = {
            'datasets': {
                'atlasia/darija_english': {
                    'subsets': ['web_data', 'comments', 'stories', 'doda', 'transliteration'],
                    'required_columns': {
                        'web_data': ['english', 'darija', 'source'],
                        'comments': ['id', 'english', 'darija', 'source'],
                        'stories': ['ChapterName', 'darija', 'english', 'chunk_id'],
                        'doda': ['id', 'darija', 'en'],
                        'transliteration': ['darija_arabizi', 'darija_arabic']
                    }
                }
            }
        }
        mock_load_yaml_config.return_value = mock_config

        # Reload the analyzer with the mocked config
        self.analyzer = ColumnMappingAnalyzer(self.data_paths)
        
        for dataset_name in mock_config['datasets']:
            with self.subTest(dataset=dataset_name):
                self.assertIn(dataset_name, self.analyzer.config['datasets'], f"Dataset {dataset_name} not found in YAML config")
                
                yaml_subsets = set(mock_config['datasets'][dataset_name]['subsets'])
                config_subsets = set(self.analyzer.config['datasets'][dataset_name]['subsets'])
                self.assertEqual(yaml_subsets, config_subsets, f"Subsets mismatch for {dataset_name}")
                
                for subset in yaml_subsets:
                    yaml_columns = set(mock_config['datasets'][dataset_name]['required_columns'][subset])
                    config_columns = set(self.analyzer.config['datasets'][dataset_name]['required_columns'][subset])
                    self.assertEqual(yaml_columns, config_columns, f"Column mismatch for {dataset_name}/{subset}")

if __name__ == "__main__":
    unittest.main()
