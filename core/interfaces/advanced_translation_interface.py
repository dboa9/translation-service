"""
Advanced Translation Interface with model-specific capabilities and monitoring
"""
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import streamlit as st
from datetime import datetime

from core.translation.translation_service import TranslationService
from core.monitoring.resource_monitor import ResourceMonitor
from core.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class ModelCapabilityManager:
    """Manages model-specific translation capabilities"""
    
    def __init__(self):
        self.model_capabilities = {
            "AnasAber-seamless-darija-eng": {
                "direction": "bidirectional",
                "source_langs": ["darija", "english"],
                "target_langs": ["darija", "english"],
                "features": ["translation"]
            },
            "AnasskMoroccanDarija-Llama-3-1-8B": {
                "direction": "unidirectional",
                "source_langs": ["darija"],
                "target_langs": ["english"],
                "features": ["translation", "analysis"]
            },
            # Add other models here
        }
        
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get capabilities for a specific model"""
        return self.model_capabilities.get(model_name, {})
        
    def get_compatible_models(self, source_lang: str, target_lang: str) -> List[str]:
        """Get models compatible with the given language pair"""
        compatible = []
        for model, caps in self.model_capabilities.items():
            if (source_lang.lower() in caps["source_langs"] and 
                target_lang.lower() in caps["target_langs"]):
                compatible.append(model)
        return compatible

class TrainingMonitor:
    """Monitors model training progress"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.current_epoch: int = 0
        self.total_epochs: int = 0
        
    def update_metrics(self, metrics: Dict[str, Any]):
        """Update training metrics"""
        self.metrics = metrics
        
    def get_progress(self) -> Dict[str, Any]:
        """Get current training progress"""
        return {
            "current_epoch": self.current_epoch,
            "total_epochs": self.total_epochs,
            "metrics": self.metrics
        }

class DeploymentMonitor:
    """Monitors EC2 deployment status"""
    
    def __init__(self):
        self.status: str = "Not Started"
        self.logs: List[str] = []
        
    def update_status(self, status: str, log_message: str):
        """Update deployment status"""
        self.status = status
        self.logs.append(f"{datetime.now().isoformat()}: {log_message}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        return {
            "status": self.status,
            "logs": self.logs[-10:]  # Last 10 logs
        }

class AdvancedTranslationUI:
    """Advanced Translation Interface with model-specific features"""
    
    def __init__(self):
        self.translation_service = TranslationService()
        self.resource_monitor = ResourceMonitor()
        self.capability_manager = ModelCapabilityManager()
        self.training_monitor = TrainingMonitor()
        self.deployment_monitor = DeploymentMonitor()
        
    def render_model_selection(self) -> str:
        """Render model selection interface"""
        st.sidebar.header("Model Selection")
        
        source_lang = st.sidebar.selectbox(
            "Source Language",
            ["Darija", "English"],
            key="source_lang"
        )
        
        target_lang = st.sidebar.selectbox(
            "Target Language",
            ["English", "Darija"],
            key="target_lang"
        )
        
        compatible_models = self.capability_manager.get_compatible_models(
            source_lang, target_lang
        )
        
        selected_model = st.sidebar.selectbox(
            "Select Model",
            compatible_models,
            key="model"
        )
        
        if selected_model:
            model_info = self.capability_manager.get_model_info(selected_model)
            st.sidebar.info(
                f"""
                **Model Capabilities**
                Direction: {model_info['direction']}
                Features: {', '.join(model_info['features'])}
                """
            )
            
        return selected_model
        
    def render_translation_interface(self, model: str):
        """Render translation interface for selected model"""
        st.header("Translation")
        
        input_text = st.text_area(
            "Enter text to translate",
            height=150,
            key="translation_input"
        )
        
        if st.button("Translate", key="translate_btn"):
            if input_text:
                with st.spinner("Translating..."):
                    # Get model capabilities
                    model_info = self.capability_manager.get_model_info(model)
                    
                    # Perform translation based on model capabilities
                    translation = self.translation_service.translate(
                        text=input_text,
                        source_lang=st.session_state.source_lang,
                        target_lang=st.session_state.target_lang
                    )
                    
                    if translation:
                        st.success("Translation:")
                        st.write(translation)
                        
                        # Show additional analysis if supported
                        if "analysis" in model_info["features"]:
                            st.info("Model Analysis:")
                            # Add model-specific analysis here
                            
    def render_training_monitor(self):
        """Render training monitoring interface"""
        st.header("Model Training Monitor")
        
        progress = self.training_monitor.get_progress()
        
        # Display training progress
        progress_bar = st.progress(0)
        if progress["total_epochs"] > 0:
            progress_value = progress["current_epoch"] / progress["total_epochs"]
            progress_bar.progress(progress_value)
            
        # Display metrics
        if progress["metrics"]:
            st.subheader("Training Metrics")
            metrics_df = pd.DataFrame(progress["metrics"])
            st.line_chart(metrics_df)
            
    def render_deployment_monitor(self):
        """Render EC2 deployment monitoring interface"""
        st.header("EC2 Deployment Monitor")
        
        status = self.deployment_monitor.get_status()
        
        st.info(f"Status: {status['status']}")
        
        # Display deployment logs
        st.subheader("Deployment Logs")
        for log in status["logs"]:
            st.text(log)
            
    def render(self):
        """Render the complete interface"""
        st.title("🌐 Advanced Translation Service")
        
        # Create tabs for different functionalities
        tabs = st.tabs([
            "Translation",
            "Training Monitor",
            "Deployment Monitor"
        ])
        
        with tabs[0]:
            selected_model = self.render_model_selection()
            if selected_model:
                self.render_translation_interface(selected_model)
                
        with tabs[1]:
            self.render_training_monitor()
            
        with tabs[2]:
            self.render_deployment_monitor()
            
        # Display system metrics
        self.render_system_metrics()
        
    def render_system_metrics(self):
        """Render system resource metrics"""
        st.sidebar.header("System Metrics")
        
        metrics = self.resource_monitor.get_system_metrics()
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("CPU Usage", f"{metrics.cpu_usage:.1f}%")
            st.metric("Memory Usage", f"{metrics.memory_usage:.1f}%")
        with col2:
            st.metric("Disk Usage", f"{metrics.disk_usage:.1f}%")
            if hasattr(metrics, "gpu_usage"):
                st.metric("GPU Usage", f"{metrics.gpu_usage:.1f}%")

def main():
    """Main entry point for the advanced translation interface"""
    st.set_page_config(
        page_title="Advanced Translation Service",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    try:
        ui = AdvancedTranslationUI()
        ui.render()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
