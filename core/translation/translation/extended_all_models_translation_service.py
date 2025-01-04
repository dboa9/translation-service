import logging
from typing import Dict, Any, List
from .all_models_translation_service import UnifiedTranslationService, MODEL_INFO, safe_import

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtendedUnifiedTranslationService(UnifiedTranslationService):
    def __init__(self):
        super().__init__()
        self.all_models = list(MODEL_INFO.keys())
        self.available_models = self.get_available_models()
        self.unavailable_models = [model for model in self.all_models if model not in self.available_models]
        logger.info(f"Available models: {', '.join(self.available_models)}")
        logger.info(f"Unavailable models: {', '.join(self.unavailable_models)}")

    def get_available_models(self) -> List[str]:
        available_models = []
        for name, info in MODEL_INFO.items():
            service_class = safe_import(info["module_path"], info["class_name"])
            if service_class:
                available_models.append(name)
            else:
                logger.warning(f"Model {name} is not available")
        return available_models

    def get_unavailable_models(self) -> List[str]:
        return self.unavailable_models

    def get_model_info(self) -> Dict[str, Dict[str, Any]]:
        return MODEL_INFO

def get_extended_translation_service() -> ExtendedUnifiedTranslationService:
    return ExtendedUnifiedTranslationService()

__all__ = [
    "ExtendedUnifiedTranslationService",
    "get_extended_translation_service"
]
