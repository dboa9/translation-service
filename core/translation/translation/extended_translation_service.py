import logging
import requests
from typing import Dict, Any
import importlib

from core.translation.translation.seamless_darija_translation_service import SeamlessDarijaTranslationService
from core.translation.translation.anas_aber_seamless_service import AnasAberSeamlessTranslationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_import(module_path, class_name):
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import {class_name} from {module_path}: {e}")
        return None

class ExtendedTranslationService:
    def __init__(self):
        self.services = {
            "seamless": SeamlessDarijaTranslationService(),
            "anasaber": AnasAberSeamlessTranslationService(),
        }
        
        # Dynamically import other services
        service_imports = [
            ("AnasAberNllbEnhancedTranslationService", "core.translation.AnasAbernllb_enhanced_darija_eng_v1_1.model"),
            ("BAKKALIAYOUBDarijaTranslationService", "core.translation.BAKKALIAYOUBDarijaTranslation_V1.model"),
            ("MBZUAIParisAtlasChatService", "core.translation.MBZUAI_ParisAtlas_Chat_9B.model"),
            ("SimLabDarijaBertService", "core.translation.sim_lab_darijabert.model"),
            ("YchafiquiDarijaToEnglishService", "core.translation.ychafiquidarija_to_english_2.model"),
            ("AnasskLlamaTranslationService", "core.translation.AnasskMoroccanDarija_Llama_3_1_8B.model"),
            ("AtlasiaTransliterationService", "core.translation.atlasiaTransliteration_Moroccan_Darija.model"),
            ("CentinoDarijaToEnglishService", "core.translation.centino00darija_to_english.model"),
            ("HananeChabDarijaEnglishService", "core.translation.hananeChabdarija_englishV2_1.model"),
            ("LachkarsalimHelsinkiTranslationService", "core.translation.lachkarsalimHelsinki_translation_English_Moroccan_Arabic.model"),
            ("LachkarsalimLatinDarijaEnglishService", "core.translation.lachkarsalimLatinDarija_English_v2.model"),
        ]

        for class_name, module_path in service_imports:
            service_class = safe_import(module_path, class_name)
            if service_class:
                service_name = class_name.replace("TranslationService", "").replace("Service", "").lower()
                self.services[service_name] = service_class()

        self.model_urls = {
            "seamless": "https://api-inference.huggingface.co/models/AnasAber/seamless-darija-eng",
            "anasaber": "https://api-inference.huggingface.co/models/AnasAber/seamless-darija-eng",
            "anassk": "https://api-inference.huggingface.co/models/Anassk/MoroccanDarija-Llama-3.1-8B",
            "atlasia": "https://api-inference.huggingface.co/models/BounharAbdelaziz/Transliteration-Moroccan-Darija",
            "centino": "https://api-inference.huggingface.co/models/centino00/darija-to-english-new",
            "hanane": "https://api-inference.huggingface.co/models/hananeChab/darija_englishV2.1",
            "helsinki": "https://api-inference.huggingface.co/models/lachkarsalim/Helsinki-translation-English_Moroccan-Arabic",
            "latin_darija": "https://api-inference.huggingface.co/models/lachkarsalim/LatinDarija_English-v2",
            "anasaber_nllb": "https://api-inference.huggingface.co/models/AnasAber/seamless-darija-eng",
            "bakkali": "https://api-inference.huggingface.co/models/BAKKALIAVOUB/DarijaTranslation-V1",
            "mbzuai": "https://api-inference.huggingface.co/models/MBZUAI/ParisAtlas-Chat-9B",
            "sim_lab": "https://api-inference.huggingface.co/models/sim-lab/darijabert",
            "ychafiqui": "https://api-inference.huggingface.co/models/ychafiqui/darija-to-english-2"
        }
        self.headers = {"Authorization": "Bearer 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"}

    def translate_with_api(self, text: str, model: str) -> str:
        api_url = self.model_urls.get(model)
        if not api_url:
            logger.error(f"No API URL found for model: {model}")
            return f"Error: No API URL for model {model}"

        payload = {"inputs": text}
        try:
            response = requests.post(api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            else:
                logger.error(f"Unexpected API response format for model {model}: {result}")
                return f"Error: Unexpected response from {model} API"
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for model {model}: {str(e)}")
            return f"Error: API request failed for {model}"

    def translate(self, text: str, source_lang: str, target_lang: str, model: str = "seamless") -> str:
        try:
            if model not in self.services:
                raise ValueError(f"Model {model} not found in services.")
            translation = self.services[model].translate(text, source_lang, target_lang)
            if translation.startswith("Translation error") or translation.startswith("[Fallback]"):
                logger.warning(f"Service translation failed for {model}, attempting API translation")
                translation = self.translate_with_api(text, model)
            return translation
        except Exception as e:
            logger.error(f"Error in extended translate method: {str(e)}")
            return f"Extended translation error: {str(e)}"

    def batch_translate(self, texts: list, source_lang: str, target_lang: str, model: str = "seamless") -> list:
        return [self.translate(text, source_lang, target_lang, model) for text in texts]

# Example usage
if __name__ == "__main__":
    service = ExtendedTranslationService()
    
    print("English to Darija (using seamless model):")
    result = service.translate("Hello, how are you?", "English", "Darija")
    print(f"Input: Hello, how are you?\nOutput: {result}\n")

    print("Darija to English (using anassk model):")
    result = service.translate("كيف داير؟", "Darija", "English", model="anassk")
    print(f"Input: كيف داير؟\nOutput: {result}\n")

    print("Batch translation (English to Darija, using seamless model):")
    texts = ["Hello", "How are you?", "Good morning"]
    results = service.batch_translate(texts, "English", "Darija")
    for input_text, output_text in zip(texts, results):
        print(f"Input: {input_text}\nOutput: {output_text}")
