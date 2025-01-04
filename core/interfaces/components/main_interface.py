"""
Main interface component that coordinates all other interface components
"""
import streamlit as st
from .base_interface import BaseInterface
from .model_interface import ModelInterface
from .monitoring_interface import MonitoringInterface
from .translation_interface import TranslationInterface
from .utils import initialize_interface
import logging

logger = logging.getLogger(__name__)

class MainInterface(BaseInterface):
    """Main interface component that coordinates all other components"""
    
    def __init__(self):
        """Initialize main interface"""
        super().__init__()
        self.model_interface = ModelInterface()
        self.monitoring_interface = MonitoringInterface()
        self.translation_interface = TranslationInterface()
        
        # Store interfaces in session state for cross-component access
        st.session_state.model_interface = self.model_interface
        st.session_state.monitoring_interface = self.monitoring_interface
        st.session_state.translation_interface = self.translation_interface
    
    def render(self):
        """Render all interface components"""
        try:
            # Initialize streamlit interface
            initialize_interface()
            
            # Render model selection in sidebar
            self.model_interface.render()
            
            # Render monitoring interface in sidebar
            self.monitoring_interface.render()
            
            # Render main translation interface
            self.translation_interface.render()
            
        except Exception as e:
            logger.error(f"Error rendering interface: {str(e)}")
            st.error(f"Interface error: {str(e)}")
    
    def update(self):
        """Update all interface components"""
        if not self.initialized:
            self.initialize()
            
        try:
            # Update all components
            self.model_interface.update()
            self.monitoring_interface.update()
            self.translation_interface.update()
            
        except Exception as e:
            logger.error(f"Error updating interface: {str(e)}")
            st.error(f"Update error: {str(e)}")
    
    def _setup(self):
        """Setup main interface configurations"""
        try:
            # Initialize all components
            self.model_interface.initialize()
            self.monitoring_interface.initialize()
            self.translation_interface.initialize()
            logger.info("All interface components initialized")
            
        except Exception as e:
            logger.error(f"Error setting up interface: {str(e)}")
            st.error("Failed to setup interface components")
