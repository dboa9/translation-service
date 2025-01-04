# File: core/interfaces/web_interface.py
"""
Enhanced Translation Web Interface
Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/core/interfaces/web_interface.py
Author: dboa9 (danielalchemy9@gmail.com)
"""

import logging
import os
from pathlib import Path
import sys
import json
from datetime import datetime

import streamlit as st
import torch
from typing import Dict, Any, Optional

from core.translation.translation_service import TranslationService
from core.monitoring.resource_monitor import ResourceMonitor
from core.utils.logging_utils import setup_logger

# Setup logging
LOG_DIR = Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "web_interface.log"

logger = setup_logger(__name__)

class TranslationUI:
    def __init__(self):
        self.translation_service = TranslationService()
        self.monitor = ResourceMonitor()
        self.load_deployment_status()
        
    def load_deployment_status(self):
        """Load deployment status from file or initialize defaults"""
        try:
            status_file = LOG_DIR / "deployment_status.json"
            if status_file.exists():
                with open(status_file, 'r') as f:
                    self.deployment_status = json.load(f)
            else:
                self.deployment_status = {
                    "status": "In Progress",
                    "last_attempt": datetime.now().isoformat(),
                    "version": "v0.1.0"
                }
        except Exception as e:
            logger.error(f"Error loading deployment status: {e}")
            self.deployment_status = {
                "status": "Error",
                "last_attempt": datetime.now().isoformat(),
                "version": "unknown"
            }
        
    def render_system_status(self):
        """Display system resource status"""
        metrics = self.monitor.get_system_metrics()
        
        st.sidebar.header("System Status")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.metric("CPU Usage", f"{metrics.cpu_usage:.1f}%")
            st.metric("Memory Usage", f"{metrics.memory_usage:.1f}%")
        
        with col2:
            st.metric("Disk Usage", f"{metrics.disk_usage:.1f}%")
            if metrics.gpu_metrics:
                for gpu_id, gpu_info in metrics.gpu_metrics.items():
                    memory_used = gpu_info['memory_allocated'] / 1024**3
                    st.metric(f"GPU {gpu_id} Memory", f"{memory_used:.1f}GB")

    def render_translation_form(self):
        """Render translation interface"""
        st.title("🌐 Darija-English Translation Service")
        
        # Model selection
        available_models = {
            name: info for name, info in 
            self.translation_service.model_paths.items()
            if "translation" in info.get("use_case", [])
        }
        
        selected_model = st.sidebar.selectbox(
            "Select Model:",
            list(available_models.keys()),
            format_func=lambda x: f"{x.split('/')[-1]}",
            help="Choose the model that best suits your needs"
        )
        
        model_info = available_models[selected_model]
        st.sidebar.info(
            f"""
            Model Type: {model_info['model_family'].upper()}
            Direction: {model_info.get('direction', 'both')}
            Trusted: {'Yes' if model_info.get('trusted', False) else 'No'}
            """
        )
        
        # Language selection
        source_lang = st.radio(
            "Select source language:",
            ("English", "Darija"),
            key="source_lang",
            horizontal=True
        )
        target_lang = "Darija" if source_lang == "English" else "English"
        
        # Input text area
        input_text = st.text_area(
            f"Enter {source_lang} text:",
            height=150,
            key="input_text",
            help=f"Enter the text you want to translate (max {self.translation_service.max_input_length} characters)"
        )
        
        if input_text:
            st.caption(f"Character count: {len(input_text)}/{self.translation_service.max_input_length}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Translate", use_container_width=True):
                if input_text:
                    with st.spinner("Translating..."):
                        # Log resource usage before translation
                        start_metrics = self.monitor.get_system_metrics()
                        logger.info(f"Starting translation. Memory usage: {start_metrics.memory_usage}%")
                        
                        # Perform translation
                        translation = self.translation_service.translate(
                            input_text, source_lang, target_lang, selected_model
                        )
                        
                        # Log resource usage after translation
                        end_metrics = self.monitor.get_system_metrics()
                        logger.info(
                            f"Translation completed. Memory change: "
                            f"{end_metrics.memory_usage - start_metrics.memory_usage}%"
                        )
                        
                        if translation:
                            st.success("Translation complete!")
                            st.markdown(f"**{translation}**")
                        else:
                            st.error("Translation failed. Please try again.")
                else:
                    st.warning("Please enter text to translate.")
                    
        with col2:
            if source_lang == "Darija" and st.button("Get Transliteration", use_container_width=True):
                if input_text:
                    with st.spinner("Processing..."):
                        transliteration = self.translation_service.transliterate(input_text)
                        if transliteration:
                            st.success("Transliteration:")
                            st.markdown(f"**{transliteration}**")
                else:
                    st.warning("Please enter text to transliterate.")

        # Display system metrics
        self.render_system_status()

        # Add information about the service
        st.markdown("---")
        with st.expander("About this service", expanded=False):
            st.markdown("""
            ### Features
            - **Translation**: Bidirectional translation between English and Darija
            - **Transliteration**: Convert Darija text to Latin script
            - **Resource Monitoring**: Real-time system resource tracking
            
            ### Models Used
            - Translation: Multiple models including Helsinki-NLP and specialized Darija models
            - Transliteration: atlasia/Transliteration-Moroccan-Darija
            
            ### System Requirements
            - GPU acceleration when available
            - Minimum 4GB RAM recommended
            - Python 3.11+
            """)

def main():
    st.set_page_config(
        page_title="Darija-English Translation Service",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    try:
        ui = TranslationUI()
        ui.render_translation_form()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
