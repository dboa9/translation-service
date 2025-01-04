import unittest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from core.translation.translation.seamless_darija_translation_service import SeamlessDarijaTranslationService

class TestTranslationWithTarget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_name = "AnasAber/seamless-darija-eng"
        cls.tokenizer = AutoTokenizer.from_pretrained(cls.model_name, token=os.getenv('HUGGINGFACE_TOKEN'))
        cls.model = AutoModelForSeq2SeqLM.from_pretrained(cls.model_name, token=os.getenv('HUGGINGFACE_TOKEN'))
        cls.service = SeamlessDarijaTranslationService()

    def test_english_to_darija(self):
        english_text = "Hello, how are you?"
        inputs = self.tokenizer(english_text, return_tensors="pt", padding=True)
        
        # Explicitly set target language to Darija
        outputs = self.model.generate(
            **inputs,
            max_length=128,
            num_beams=5,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            tgt_lang="ary"  # Darija language code
        )
        
        darija_translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        self.assertIsNotNone(darija_translation)
        self.assertNotEqual(darija_translation, english_text)
        print(f"English to Darija: '{english_text}' -> '{darija_translation}'")

    def test_darija_to_english(self):
        darija_text = "كيف داير؟"
        inputs = self.tokenizer(darija_text, return_tensors="pt", padding=True)
        
        # Explicitly set target language to English
        outputs = self.model.generate(
            **inputs,
            max_length=128,
            num_beams=5,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            tgt_lang="eng"  # English language code
        )
        
        english_translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        self.assertIsNotNone(english_translation)
        self.assertNotEqual(english_translation, darija_text)
        print(f"Darija to English: '{darija_text}' -> '{english_translation}'")

    def test_dynamic_target_language(self):
        test_cases = [
            ("Hello, good morning", "eng", "ary"),  # English to Darija
            ("كيف داير؟", "ary", "eng"),  # Darija to English
        ]
        
        for text, source_lang, target_lang in test_cases:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True)
            outputs = self.model.generate(
                **inputs,
                max_length=128,
                num_beams=5,
                temperature=0.7,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                tgt_lang=target_lang
            )
            
            translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            self.assertIsNotNone(translation)
            self.assertNotEqual(translation, text)
            print(f"{source_lang} to {target_lang}: '{text}' -> '{translation}'")

if __name__ == '__main__':
    unittest.main()
