from abc import ABC, abstractmethod

class BaseTranslationService(ABC):
    @abstractmethod
    def translate(self, text, source_lang, target_lang):
        pass
