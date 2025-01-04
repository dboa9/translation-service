import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.translation.translation import ExtendedUnifiedTranslationService, MODEL_INFO

class TestModelConfigurations(unittest.TestCase):

    def setUp(self):
        self.translation_service = ExtendedUnifiedTranslationService()

    def test_model_initialization(self):
        self.assertEqual(len(self.translation_service.all_models), len(MODEL_INFO))
        self.assertGreater(len(self.translation_service.available_models), 0)
        self.assertLess(len(self.translation_service.available_models), len(MODEL_INFO))

    def test_available_and_unavailable_models(self):
        available_models = self.translation_service.get_available_models()
        unavailable_models = self.translation_service.get_unavailable_models()
        
        self.assertGreater(len(available_models), 0)
        self.assertGreater(len(unavailable_models), 0)
        self.assertEqual(len(available_models) + len(unavailable_models), len(MODEL_INFO))

    @patch('core.translation.translation.all_models_translation_service.UnifiedTranslationService.get_service')
    def test_translation_for_available_models(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.translate.return_value = "Translated text"
        mock_get_service.return_value = mock_service

        for model_name in self.translation_service.get_available_models():
            result = self.translation_service.translate("Test text", "en", "ar", model_name)
            self.assertEqual(result, "Translated text")

    @patch('core.translation.translation.all_models_translation_service.UnifiedTranslationService.get_service')
    def test_api_request_failure(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.translate.side_effect = Exception("400 Client Error: Bad Request")
        mock_get_service.return_value = mock_service

        for model_name in self.translation_service.get_available_models():
            result = self.translation_service.translate("Hello", "en", "ar", model_name)
            self.assertTrue(result.startswith(f"[{model_name}] API request failed after 3 attempts"))

    @patch('core.translation.translation.all_models_translation_service.UnifiedTranslationService.get_service')
    def test_fallback_to_anasaber_seamless(self, mock_get_service):
        def side_effect(model):
            if model == "AnasAber-seamless-darija-eng":
                mock = MagicMock()
                mock.translate.return_value = "Fallback translation"
                return mock
            raise Exception("Model not available")

        mock_get_service.side_effect = side_effect

        for model_name in self.translation_service.get_available_models():
            if model_name != "AnasAber-seamless-darija-eng":
                result = self.translation_service.translate("Hello", "en", "ar", model_name)
                self.assertEqual(result, "Fallback translation")

    @patch('core.translation.translation.all_models_translation_service.UnifiedTranslationService.get_service')
    def test_retry_mechanism(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.translate.side_effect = [
            Exception("503 Server Error: Service Unavailable"),
            Exception("503 Server Error: Service Unavailable"),
            "Successful translation"
        ]
        mock_get_service.return_value = mock_service

        result = self.translation_service.translate("Hello", "en", "ar", "AnasAber-seamless-darija-eng")
        self.assertEqual(result, "Successful translation")
        self.assertEqual(mock_service.translate.call_count, 3)

    def test_get_model_info(self):
        model_info = self.translation_service.get_model_info()
        self.assertEqual(model_info, MODEL_INFO)

if __name__ == '__main__':
    unittest.main()
