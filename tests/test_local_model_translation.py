import unittest
import sys
import os
from pathlib import Path
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

class TestLocalModelTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_name = "AnasAber/seamless-darija-eng"
        print("Loading tokenizer...")
        cls.tokenizer = AutoTokenizer.from_pretrained(cls.model_name)
        print("Loading model...")
        cls.model = AutoModelForSeq2SeqLM.from_pretrained(cls.model_name)
        if torch.cuda.is_available():
            cls.model = cls.model.to("cuda")
            print("Model moved to CUDA")
        print("Setup complete")

    def test_english_to_darija(self):
        english_text = "Hello, how are you?"
        print(f"\nTesting English to Darija: '{english_text}'")
        
        inputs = self.tokenizer(english_text, return_tensors="pt", padding=True)
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
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
        print(f"Translation: '{darija_translation}'")
        
        self.assertIsNotNone(darija_translation)
        self.assertNotEqual(darija_translation, english_text)

    def test_darija_to_english(self):
        darija_text = "كيف داير؟"
        print(f"\nTesting Darija to English: '{darija_text}'")
        
        inputs = self.tokenizer(darija_text, return_tensors="pt", padding=True)
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
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
        print(f"Translation: '{english_translation}'")
        
        self.assertIsNotNone(english_translation)
        self.assertNotEqual(english_translation, darija_text)

    def test_batch_translation(self):
        texts = [
            ("Hello", "eng", "ary"),
            ("كيف حالك", "ary", "eng"),
            ("Good morning", "eng", "ary"),
            ("صباح الخير", "ary", "eng")
        ]
        
        print("\nTesting batch translation:")
        for text, src_lang, tgt_lang in texts:
            print(f"\nTranslating '{text}' from {src_lang} to {tgt_lang}")
            
            inputs = self.tokenizer(text, return_tensors="pt", padding=True)
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            outputs = self.model.generate(
                **inputs,
                max_length=128,
                num_beams=5,
                temperature=0.7,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                tgt_lang=tgt_lang
            )
            
            translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            print(f"Translation: '{translation}'")
            
            self.assertIsNotNone(translation)
            self.assertNotEqual(translation, text)

if __name__ == '__main__':
    unittest.main(verbosity=2)
