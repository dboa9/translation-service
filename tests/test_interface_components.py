"""
Tests for interface components
"""
import pytest
import sys
from pathlib import Path
import streamlit as st
from unittest.mock import MagicMock, patch

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

def test_imports():
    """Test that all interface components can be imported"""
    try:
        from core.interfaces.components.base_interface import BaseInterface
        from core.interfaces.components.model_interface import ModelInterface
        from core.interfaces.components.monitoring_interface import MonitoringInterface
        from core.interfaces.components.translation_interface import TranslationInterface
        from core.interfaces.components.main_interface import MainInterface
        
        assert BaseInterface is not None
        assert ModelInterface is not None
        assert MonitoringInterface is not None
        assert TranslationInterface is not None
        assert MainInterface is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import interface components: {str(e)}")

@pytest.fixture
def mock_streamlit():
    """Mock streamlit components"""
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.tabs') as mock_tabs:
        
        mock_tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        yield {
            'title': mock_title,
            'sidebar': mock_sidebar,
            'tabs': mock_tabs
        }

def test_base_interface(mock_streamlit):
    """Test BaseInterface functionality"""
    from core.interfaces.components.base_interface import BaseInterface
    
    interface = BaseInterface()
    interface.setup_page("Test Page")
    interface.render_header("Test Header")
    
    mock_streamlit['title'].assert_called_once()

def test_model_interface():
    """Test ModelInterface functionality"""
    from core.interfaces.components.model_interface import ModelInterface
    
    capabilities = {
        "direction": "bidirectional",
        "source_langs": ["darija", "english"],
        "target_langs": ["darija", "english"],
        "features": ["translation"]
    }
    
    interface = ModelInterface("test_model", capabilities)
    assert interface.model_name == "test_model"
    assert interface.capabilities == capabilities

def test_monitoring_interface():
    """Test MonitoringInterface functionality"""
    from core.interfaces.components.monitoring_interface import MonitoringInterface
    
    interface = MonitoringInterface()
    
    # Test training metrics update
    metrics = {"loss": 0.5, "accuracy": 0.8}
    interface.update_training(metrics)
    assert interface.training_metrics["loss"][-1] == 0.5
    assert interface.training_metrics["accuracy"][-1] == 0.8
    
    # Test deployment logging
    interface.log_deployment("Test message")
    assert len(interface.deployment_logs) == 1
    assert "Test message" in interface.deployment_logs[0]

def test_translation_interface():
    """Test TranslationInterface functionality"""
    from core.interfaces.components.translation_interface import TranslationInterface
    from core.translation.translation_service import TranslationService
    
    translation_service = TranslationService()
    interface = TranslationInterface(translation_service)
    
    # Test bidirectional translation
    results = interface.render_bidirectional(
        text="Hello",
        source_lang="english",
        target_lang="darija",
        models={
            "english_to_darija": "model1",
            "darija_to_english": "model2"
        }
    )
    
    assert results is not None

def test_main_interface(mock_streamlit):
    """Test MainInterface functionality"""
    from core.interfaces.components.main_interface import MainInterface
    
    interface = MainInterface()
    interface.render()
    
    mock_streamlit['tabs'].assert_called_once()
    assert len(mock_streamlit['tabs'].return_value) == 3

if __name__ == "__main__":
    pytest.main([__file__])
