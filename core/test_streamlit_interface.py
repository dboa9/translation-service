import pytest
from unittest.mock import patch, MagicMock
import sys

# Mock the entire streamlit module
sys.modules['streamlit'] = MagicMock()

from core.interfaces.streamlit_interface import StreamlitInterface

@pytest.fixture
def streamlit_interface():
    return StreamlitInterface()

def test_load_monitoring_config_success(streamlit_interface):
    mock_config = {"cpu_usage": 50, "memory_usage": 70}
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = '{"cpu_usage": 50, "memory_usage": 70}'
        streamlit_interface.load_monitoring_config()
    assert streamlit_interface.monitoring_config == mock_config

def test_load_monitoring_config_file_not_found(streamlit_interface):
    with patch('builtins.open', side_effect=FileNotFoundError), \
         patch('streamlit.error') as mock_error:
        streamlit_interface.load_monitoring_config()
        mock_error.assert_called_with("Monitoring configuration file not found.")
    assert streamlit_interface.monitoring_config == {}

def test_load_deployment_status(streamlit_interface):
    streamlit_interface.load_deployment_status()
    assert "status" in streamlit_interface.deployment_status
    assert "last_attempt" in streamlit_interface.deployment_status
    assert "version" in streamlit_interface.deployment_status

@patch('streamlit.sidebar.selectbox')
def test_main_menu(mock_selectbox, streamlit_interface):
    mock_selectbox.return_value = "Deployment Status"
    with patch.object(streamlit_interface, 'deployment_status_page') as mock_deployment_page:
        streamlit_interface.main()
        mock_deployment_page.assert_called_once()

@patch('streamlit.write')
def test_deployment_status_page(mock_write, streamlit_interface):
    streamlit_interface.deployment_status_page()
    assert mock_write.call_count == 3

@patch('streamlit.text_input')
@patch('streamlit.button')
def test_model_testing_page(mock_button, mock_text_input, streamlit_interface):
    mock_text_input.return_value = "Test input"
    mock_button.return_value = True
    with patch('streamlit.write') as mock_write:
        streamlit_interface.model_testing_page()
        mock_write.assert_called()

@patch('streamlit.metric')
def test_monitoring_page(mock_metric, streamlit_interface):
    streamlit_interface.monitoring_config = {"cpu_usage": 50, "memory_usage": 70}
    streamlit_interface.monitoring_page()
    assert mock_metric.call_count == 2

@patch('streamlit.slider')
@patch('streamlit.select_slider')
@patch('streamlit.button')
def test_model_training_page(mock_button, mock_select_slider, mock_slider, streamlit_interface):
    mock_slider.return_value = 10
    mock_select_slider.return_value = 0.01
    mock_button.return_value = True
    with patch('streamlit.progress') as mock_progress:
        streamlit_interface.model_training_page()
        mock_progress.assert_called()

@patch('streamlit.text_input')
@patch('streamlit.button')
def test_dataset_validation_page(mock_button, mock_text_input, streamlit_interface):
    mock_text_input.side_effect = ["dataset", "config", "col1", "col2", "1,2,3", "4,5,6"]
    mock_button.return_value = True
    with patch('core.config_analysis.column_validator_core.validate_columns') as mock_validate:
        mock_validate.return_value = {"status": True, "message": "Validation passed"}
        with patch('streamlit.success') as mock_success:
            streamlit_interface.dataset_validation_page()
            mock_success.assert_called_with("Dataset validation passed!")

if __name__ == "__main__":
    pytest.main()
