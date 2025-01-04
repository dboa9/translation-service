import unittest
from core.translation.translation.all_models_translation_service import UnifiedTranslationService

class TestNewModels(unittest.TestCase):
    def setUp(self):
        self.unified_service = UnifiedTranslationService()

    def test_anasabernllb_enhanced(self):
        result = self.unified_service.translate("Hello", "en", "darija", "AnasAbernllbEnhanced")
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "Hello")

    def test_bakkaliavoub(self):
        result = self.unified_service.translate("Hello", "en", "darija", "BAKKALIAVOUB")
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "Hello")

    def test_mbzuai_paris_atlas(self):
        result = self.unified_service.translate("Hello", "en", "darija", "MBZUAIParisAtlas")
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "Hello")

    def test_sim_lab_darija_bert(self):
        result = self.unified_service.translate("Hello", "en", "darija", "SimLabDarijaBert")
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "Hello")

    def test_ychafiqui(self):
        result = self.unified_service.translate("Hello", "en", "darija", "Ychafiqui")
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "Hello")

if __name__ == '__main__':
    unittest.main()
