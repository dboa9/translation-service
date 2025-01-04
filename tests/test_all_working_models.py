import unittest
import torch
from core.translation.translation_service import TranslationService

class TestAllWorkingModels(unittest.TestCase):
    def test_seamless_model(self):
        torch.device("cpu")
        ts = TranslationService()
        model_name = "AnasAber/seamless-darija-eng"
        text = "كي داير؟ لباس؟"
        translation = ts.translate(model_name, text, 'ary', 'eng')
        self.assertNotIn("API Error", translation)

    def test_atlasia_model(self):
        torch.device("cpu")
        ts = TranslationService()
        model_name = "atlasia/Transliteration-Moroccan-Darija"
        text = "كي داير؟ لباس؟"
        translation = ts.translate(model_name, text, 'ary', 'ary_Latn')
        self.assertNotIn("API Error", translation)

if __name__ == '__main__':
    unittest.main()
