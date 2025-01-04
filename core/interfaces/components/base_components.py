"""
Base interface components
"""
from typing import Dict, Any, Optional
import streamlit as st
import logging
from pathlib import Path
import sys

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logger = logging.getLogger(__name__)

class BaseInterface:
    """Base interface class"""
    def render(self) -> None:
        """Render interface"""
        raise NotImplementedError

class ModelInterface:
    """Model interface component"""
    def __init__(self, model_name: str, capabilities: Dict[str, Any]):
        self.model_name = model_name
        self.capabilities = capabilities
        
    def render_controls(self) -> Dict[str, str]:
        """Render model controls"""
        return {
            "model_name": self.model_name,
            "source_lang": "eng",
            "target_lang": "ary"
        }

class MonitoringInterface:
    """Monitoring interface component"""
    def render_training_progress(self) -> None:
        """Render training progress"""
        st.info("Training monitoring not implemented")
        
    def render_deployment_status(self) -> None:
        """Render deployment status"""
        st.info("Deployment monitoring not implemented")

class TranslationInterface:
    """Base translation interface"""
    def __init__(self, translation_service):
        self.translation_service = translation_service
        
    def render_input(self) -> str:
        """Render text input section"""
        return st.text_area(
            "Enter text to translate",
            height=150,
            key="translation_input"
        )
        
    def render_output(self, translation: str) -> None:
        """Render translation output"""
        st.text_area(
            "Translation",
            value=translation,
            height=150,
            key="translation_output",
            disabled=True
        )
        
    def render_controls(
        self,
        source_lang: str,
        target_lang: str,
        model_name: str
    ) -> None:
        """Render translation controls"""
        raise NotImplementedError
        
    def render_bidirectional(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model_name: str
    ) -> Optional[Dict[str, str]]:
        """Handle bidirectional translation"""
        raise NotImplementedError
