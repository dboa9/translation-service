import importlib
import logging
import time
import os
from typing import Any, Dict, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MODEL_INFO = {
    "AnasAber-seamless-darija-eng": {
        "module_path": "core.translation.translation.anas_aber_seamless_service",
        "class_name": "AnasAberSeamlessTranslationService"
    },
    "AnasAbernllb-enhanced-darija-eng_v1-1": {
        "module_path": "core.translation.AnasAbernllb_enhanced_darija_eng_v1_1.model",
        "class_name": "AnasAberNllbEnhancedTranslationService"
    },
    "AnasskMoroccanDarija-Llama-3-1-8B": {
        "module_path": "core.translation.AnasskMoroccanDarija_Llama_3_1_8B.model",
        "class_name": "AnasskMoroccanDarijaLlamaTranslationService"
    },
    "atlasiaTransliteration-Moroccan-Darija": {
        "module_path": "core.translation.atlasiaTransliteration_Moroccan_Darija.model",
        "class_name": "AtlasiaTransliterationService"
    },
    "BAKKALIAYOUBDarijaTranslation-V1": {
        "module_path": "core.translation.BAKKALIAYOUBDarijaTranslation_V1.model",
        "class_name": "BAKKALIAYOUBDarijaTranslationService"
    },
    "centino00darija-to-english": {
        "module_path": "core.translation.centino00darija_to_english.model",
        "class_name": "Centino00DarijaToEnglishService"
    },
    "hananeChabdarija_englishV2-1": {
        "module_path": "core.translation.hananeChabdarija_englishV2_1.model",
        "class_name": "HananeChabDarijaEnglishService"
    },
    "lachkarsalimHelsinki-translation-English_Moroccan-Arabic": {
        "module_path": "core.translation.lachkarsalimHelsinki_translation_English_Moroccan_Arabic.model",
        "class_name": "LachkarsalimHelsinkiTranslationService"
    },
    "lachkarsalimLatinDarija_English-v2": {
        "module_path": "core.translation.lachkarsalimLatinDarija_English_v2.model",
        "class_name": "LachkarsalimLatinDarijaEnglishService"
    },
    "MBZUAI-ParisAtlas-Chat-9B": {
        "module_path": "core.translation.MBZUAI_ParisAtlas_Chat_9B.model",
        "class_name": "MBZUAIParisAtlasChatService"
    },
    "sim-lab-darijabert": {
        "module_path": "core.translation.sim_lab_darijabert.model",
        "class_name": "SimLabDarijaBertService"
    },
    "ychafiquidarija-to-english-2": {
        "module_path": "core.translation.ychafiquidarija_to_english_2.model",
        "class_name": "YchafiquiDarijaToEnglishService"
    },
    "seamless": {
        "module_path": "core.translation.translation.seamless_darija_translation_service",
        "class_name": "SeamlessDarijaTranslationService"
    }
}

def safe_import(module_path: str, class_name: str) -> Optional[Any]:
    try:
        # Check if the module file exists
        module_file = module_path.replace('.', '/') + '.py'
        if not os.path.exists(module_file):
            logger.warning(f"Module file {module_file} does not exist")
            return None

        module = importlib.import_module(module_path)
        service_class = getattr(module, class_name)
        
        # Check if the class has a translate method
        if not hasattr(service_class, 'translate'):
            logger.warning(f"{class_name} does not have a translate method")
            return None
        
        # Try to instantiate the class
        instance = service_class()
        
        # Check if the instance has a translate method (in case it's added dynamically)
        if not hasattr(instance, 'translate'):
            logger.warning(f"{class_name} instance does not have a translate method")
            return None
        
        # Try to use the translate method with a dummy input
        try:
            instance.translate("test", "en", "fr")
        except Exception as e:
            logger.warning(f"Failed to use translate method of {class_name}: {e}")
            return None
        
        return instance
    except Exception as e:
        logger.warning(f"Failed to import or instantiate {class_name} from {module_path}: {e}")
        return None

def get_translation_services():
    services = {}
    for name, info in MODEL_INFO.items():
        service_instance = safe_import(info["module_path"], info["class_name"])
        if service_instance:
            services[name] = service_instance
        else:
            logger.warning(f"Failed to load model: {name}")
    return services

class UnifiedTranslationService:
    def __init__(self):
        self.services = get_translation_services()
        self.available_models = list(self.services.keys())
        self.unavailable_models = [name for name in MODEL_INFO.keys() if name not in self.services]
        logger.info(f"UnifiedTranslationService initialized with models: {', '.join(self.available_models)}")
        logger.info(f"Unavailable models: {', '.join(self.unavailable_models)}")

    def get_service(self, model: str):
        if model not in self.services:
            raise ValueError(f"Model {model} not found")
        return self.services[model]

    def translate(self, text: str, source_lang: str, target_lang: str, model: str = "AnasAber-seamless-darija-eng") -> str:
        max_retries = 3
        retry_delay = 5  # seconds

        if model not in self.services:
            logger.warning(f"Model {model} not available. Falling back to AnasAber-seamless-darija-eng.")
            model = "AnasAber-seamless-darija-eng"

        for attempt in range(max_retries):
            try:
                service = self.get_service(model)
                translation = service.translate(text, source_lang, target_lang)
                return translation
            except Exception as e:
                logger.error(f"Error translating with {model} model (attempt {attempt + 1}): {str(e)}")
                if "503 Server Error: Service Unavailable" in str(e) and attempt < max_retries - 1:
                    logger.info(f"Model is loading. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                if attempt == max_retries - 1:
                    if "400 Client Error: Bad Request" in str(e):
                        return f"[{model}] API request failed after {max_retries} attempts: {str(e)}"
                    if model != "AnasAber-seamless-darija-eng":
                        logger.info("Falling back to AnasAber-seamless-darija-eng model.")
                        return self.translate(text, source_lang, target_lang, "AnasAber-seamless-darija-eng")
                    else:
                        return f"Translation error: {str(e)}"
        
        return f"Translation failed after {max_retries} attempts"

    def batch_translate(self, texts: list, source_lang: str, target_lang: str, model: str = "AnasAber-seamless-darija-eng") -> list:
        return [self.translate(text, source_lang, target_lang, model) for text in texts]

    def get_available_models(self) -> List[str]:
        return self.available_models

    def get_unavailable_models(self) -> List[str]:
        return self.unavailable_models

__all__ = [
    "UnifiedTranslationService",
    "get_translation_services",
    "MODEL_INFO"
]
