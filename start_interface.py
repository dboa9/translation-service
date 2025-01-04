"""
Launch script for the translation interface
"""
import os
import sys
from pathlib import Path
import logging
import streamlit as st
import torch
import warnings

# Add project root to Python path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from core.interfaces.components.main_interface import MainInterface

def initialize_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.translation_history = []
        st.session_state.selected_model = None
        st.session_state.device = "cuda" if torch.cuda.is_available() else "cpu"

def setup_torch():
    """Setup torch environment"""
    if not st.session_state.initialized:
        try:
            # Initialize torch backend first
            torch.backends.cudnn.enabled = True if torch.cuda.is_available() else False
            
            # Log torch configuration
            logger.info(f"PyTorch version: {torch.__version__}")
            if torch.cuda.is_available():
                logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
                logger.info(f"CUDA capability: {torch.cuda.get_device_capability()}")
                logger.info(f"CUDA device count: {torch.cuda.device_count()}")
            else:
                logger.info("CUDA not available, using CPU")
                
            # Verify basic torch operations
            test_tensor = torch.zeros(1)
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            test_tensor = test_tensor.to(device)
            logger.info(f"Torch initialization successful on {device}")
            
        except Exception as e:
            logger.warning(f"Error setting up torch: {str(e)}")
            logger.info("Continuing with CPU-only mode")

def setup_streamlit():
    """Configure streamlit settings"""
    if not st.session_state.initialized:
        try:
            # Mark initialization as complete
            st.session_state.initialized = True
            
        except Exception as e:
            logger.warning(f"Error configuring streamlit: {str(e)}")

if __name__ == "__main__":
    try:
        # Initialize session state
        initialize_session_state()
        
        # Setup environment only once
        setup_torch()
        setup_streamlit()
        
        # Set page config
        st.set_page_config(
            page_title="Translation Service",
            page_icon="🌐",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Hide streamlit menu and footer
        hide_menu = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
        st.markdown(hide_menu, unsafe_allow_html=True)
        
        # Add custom CSS for text color
        custom_css = """
        <style>
        .custom-text {
            color: red; /* Change this to your desired color */
        }
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)
        
        # Create and render interface
        interface = MainInterface()
        interface.render()
        
        # Example of where the error might be
        text = st.text_area("Enter text", value="", height=200, key="text_area")  # Ensure no 'class_' argument is used
        st.markdown(f'<p class="custom-text">{text}</p>', unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error launching interface: {str(e)}")
        st.error(f"Application error: {str(e)}")
        sys.exit(1)
