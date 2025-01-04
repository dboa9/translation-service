from core.translation.translation_service import TranslationService

class ExtendedTranslationService(TranslationService):
    def get_available_models(self):
        return list(self.config.get("translation_models", {}).keys())
