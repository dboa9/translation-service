"""
Main Streamlit application entry point
"""
import logging
import sys
import os
from pathlib import Path

import streamlit as st

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import components using relative imports
from interfaces.components.model_interface import ModelInterface
from interfaces.components.monitoring_interface import MonitoringInterface
from interfaces.components.translation_interface import TranslationInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'model_interface' not in st.session_state:
        st.session_state.model_interface = ModelInterface()
    if 'monitoring_interface' not in st.session_state:
        st.session_state.monitoring_interface = MonitoringInterface()
    if 'translation_interface' not in st.session_state:
        st.session_state.translation_interface = TranslationInterface()

def main():
    """Main application entry point"""
    try:
        # Set page config
        st.set_page_config(
            page_title="Enhanced Translation Service",
            page_icon="🌐",
            layout="wide"
        )
        
        # Initialize session state
        initialize_session_state()
        
        # Add custom CSS for text color
        custom_css = """
        <style>
        .custom-text {
            color: red; /* Change this to your desired color */
        }
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)
        
        # Create sidebar for model selection and monitoring
        with st.sidebar:
            st.header("Model Settings")
            st.session_state.model_interface.render()
            
            # Add system monitoring below model selection
            st.header("System Monitoring")
            st.session_state.monitoring_interface.render()
        
        # Main translation interface
        st.session_state.translation_interface.render()

        # Example of where the error might be
        text = st.text_area("Enter text", value="", height=200, key="text_area")  # Ensure no 'class_' argument is used
        st.markdown(f'<p class="custom-text">{text}</p>', unsafe_allow_html=True)

        # Update interfaces
        st.session_state.model_interface.update()
        st.session_state.monitoring_interface.update()
        st.session_state.translation_interface.update()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
