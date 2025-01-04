"""
Base interface component for the translation service
"""
import streamlit as st
from abc import ABC, abstractmethod

class BaseInterface(ABC):
    """Abstract base class for interface components"""
    
    def __init__(self):
        """Initialize base interface"""
        self.initialized = False
    
    @abstractmethod
    def render(self):
        """Render the interface component"""
        pass
    
    @abstractmethod
    def update(self):
        """Update the interface state"""
        pass
    
    def initialize(self):
        """Initialize the interface if not already initialized"""
        if not self.initialized:
            try:
                self._setup()
                self.initialized = True
            except Exception as e:
                st.error(f"Error initializing interface: {str(e)}")
    
    def _setup(self):
        """Setup interface-specific configurations"""
        pass
