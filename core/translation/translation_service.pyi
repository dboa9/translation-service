"""Type stub file for TranslationService"""
from typing import Dict, Any, Optional

class TranslationService:
    def __init__(self) -> None: ...
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model: Optional[str] = None
    ) -> str: ...
    
    def get_model_info(self, model: str) -> Dict[str, Any]: ...
    
    def get_supported_languages(self) -> Dict[str, str]: ...
