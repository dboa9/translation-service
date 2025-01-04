"""
Tests for enhanced translation service
"""
import unittest
import torch
from pathlib import Path
import yaml
import logging
from typing import Dict, Any

from core.translation.enhanced_translation_service import EnhancedTranslationService

class TestEnhancedTranslation(unittest.TestCase):
    """Test cases for enhanced translation service"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.service = EnhancedTranslationService()
        
    def test_initialization(self):
        """Test service initialization"""
        self.assertIsNotNone(self.service)
        self.assertIsInstance(self.service.device, torch.device)
        self.assertIsInstance(self.service.config, dict)
        self.assertIsInstance(self.service.model_paths, dict)
        
    def test_device_info(self):
        """Test device information retrieval"""
        info = self.service.get_device_info()
        
        self.assertIn('device_type', info)
        self.assertIn('torch_version', info)
        self.assertIn('cuda_available', info)
        
        if info['cuda_available']:
            self.assertIn('cuda_device', info)
            self.assertIn('cuda_capability', info)
            self.assertIn('cuda_device_count', info)
            
    def test_enhanced_translation(self):
        """Test enhanced translation functionality"""
        result = self.service.translate(
            text="Hello",
            source_lang="english",
            target_lang="darija"
        )
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn('translation', result)
        self.assertIn('model_used', result)
        self.assertIn('confidence', result)
        self.assertIn('device', result)
        self.assertIn('time_taken', result)
        self.assertIn('source_lang', result)
        self.assertIn('target_lang', result)
        self.assertIn('status', result)
        
        # Check value types
        self.assertIsInstance(result['translation'], str)
        self.assertIsInstance(result['confidence'], float)
        self.assertIsInstance(result['time_taken'], float)
        
    def test_error_handling(self):
        """Test error handling in translation"""
        # Test with invalid language
        result = self.service.translate(
            text="Hello",
            source_lang="invalid",
            target_lang="invalid"
        )
        
        self.assertIn('translation', result)
        self.assertIn('Error:', result['translation'])
        self.assertEqual(result['confidence'], 0.0)
        self.assertEqual(result['status'], 'error')
        
    def test_model_capabilities(self):
        """Test model capabilities retrieval"""
        # Test all models
        all_capabilities = self.service.get_model_capabilities()
        self.assertIsInstance(all_capabilities, dict)
        self.assertGreater(len(all_capabilities), 0)
        
        # Test specific model
        model_name = next(iter(self.service.model_paths))
        model_capabilities = self.service.get_model_capabilities(model_name)
        self.assertIsInstance(model_capabilities, dict)
        self.assertIn('model_family', model_capabilities)
        
    def test_model_selection(self):
        """Test model selection logic"""
        # Test Darija to English
        result = self.service.translate(
            text="مرحبا",
            source_lang="darija",
            target_lang="english"
        )
        self.assertIsNotNone(result['model_used'])
        self.assertEqual(result['status'], 'success')
        
        # Test English to Darija
        result = self.service.translate(
            text="Hello",
            source_lang="english",
            target_lang="darija"
        )
        self.assertIsNotNone(result['model_used'])
        self.assertEqual(result['status'], 'success')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
