from .base_translation_service import BaseTranslationService

class AnasAberSeamlessTranslationService(BaseTranslationService):
    def translate(self, text, source_lang, target_lang):
        return f"AnasAberSeamless translation: {text}"
