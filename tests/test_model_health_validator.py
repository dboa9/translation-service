import unittest
import logging
from datetime import datetime
from core.dataset.validators.model_health_validator import ModelHealthValidator
from core.translation.enhanced_translation_service import EnhancedTranslationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestModelHealthValidator(unittest.TestCase):
    def setUp(self):
        logger.info("Initializing test environment")
        self.validator = ModelHealthValidator()
        self.translation_service = EnhancedTranslationService()
        
        # Test phrases for translation verification
        self.test_phrases = {
            "en": [
                "Hello, how are you?",
                "What is your name?",
                "Good morning",
                "Thank you very much"
            ],
            "ary": [
                "سلام، كيف داير؟",
                "شنو سميتك؟",
                "صباح الخير",
                "شكرا بزاف"
            ]
        }

    def test_unhealthy_model_validation(self):
        """Test validation of unhealthy model state with detailed logging"""
        logger.info("Testing unhealthy model validation")
        
        # Create sample health data for an unhealthy model
        unhealthy_data = {
            "status": "unhealthy",
            "success_rate": 0.3,
            "total_attempts": 100,
            "recent_errors": 5,
            "fallback_count": 0,
            "last_successful": None
        }
        
        logger.info(f"Validating unhealthy model data: {unhealthy_data}")
        
        # Validate unhealthy model data
        validation_result = self.validator.validate_model_health(unhealthy_data, is_healthy=False)
        logger.info(f"Validation result for unhealthy model: {validation_result}")
        self.assertTrue(validation_result, "Unhealthy model validation should pass with correct data")

        # Test with incorrect last_successful value
        unhealthy_data["last_successful"] = datetime.now().isoformat()
        logger.info(f"Testing with invalid last_successful: {unhealthy_data}")
        validation_result = self.validator.validate_model_health(unhealthy_data, is_healthy=False)
        logger.info(f"Validation result with invalid last_successful: {validation_result}")
        self.assertFalse(validation_result, "Unhealthy model validation should fail when last_successful is not None")

    def test_healthy_model_validation(self):
        """Test validation of healthy model state with translation verification"""
        logger.info("Testing healthy model validation with translations")
        
        # Create sample health data for a healthy model
        healthy_data = {
            "status": "healthy",
            "success_rate": 0.9,
            "total_attempts": 100,
            "recent_errors": 0,
            "fallback_count": 0,
            "last_successful": datetime.now().isoformat()
        }
        
        logger.info(f"Validating healthy model data: {healthy_data}")
        validation_result = self.validator.validate_model_health(healthy_data, is_healthy=True)
        logger.info(f"Validation result for healthy model: {validation_result}")
        self.assertTrue(validation_result, "Healthy model validation should pass with correct data")
        
        # Test translations with healthy model
        logger.info("Testing translations with healthy model")
        for en_phrase in self.test_phrases["en"]:
            try:
                translation = self.translation_service.translate(
                    en_phrase, 
                    source_lang="en", 
                    target_lang="ary",
                    model_name="AnasAber-seamless-darija-eng"
                )
                logger.info(f"English -> Darija: '{en_phrase}' -> '{translation}'")
            except Exception as e:
                logger.error(f"Translation failed: {str(e)}")

    def test_degraded_model_validation(self):
        """Test validation of degraded model state with detailed metrics"""
        logger.info("Testing degraded model validation")
        
        # Create sample health data for a degraded model
        degraded_data = {
            "status": "degraded",
            "success_rate": 0.6,
            "total_attempts": 100,
            "recent_errors": 2,
            "fallback_count": 1,
            "last_successful": datetime.now().isoformat()
        }
        
        logger.info(f"Validating degraded model data: {degraded_data}")
        validation_result = self.validator.validate_model_health(degraded_data, is_healthy=True)
        logger.info(f"Validation result for degraded model: {validation_result}")
        self.assertTrue(validation_result, "Degraded model validation should pass as it's considered healthy")
        
        # Log detailed metrics
        logger.info(f"Degraded model metrics:")
        logger.info(f"Success rate: {degraded_data['success_rate']*100:.1f}%")
        logger.info(f"Total attempts: {degraded_data['total_attempts']}")
        logger.info(f"Recent errors: {degraded_data['recent_errors']}")
        logger.info(f"Fallback count: {degraded_data['fallback_count']}")

    def test_integration_with_translation_service(self):
        """Test integration with EnhancedTranslationService and translation verification"""
        logger.info("Testing integration with translation service")
        
        # Get health report from translation service
        health_report = self.translation_service.get_model_health()
        logger.info(f"Retrieved health report for {len(health_report)} models")
        
        # Test translations and validate health for each model
        for model_name, health_data in health_report.items():
            logger.info(f"\nTesting model: {model_name}")
            logger.info(f"Health data: {health_data}")
            
            is_healthy = health_data["status"] in ["healthy", "degraded"]
            validation_result = self.validator.validate_model_health(health_data, is_healthy)
            logger.info(f"Validation result: {validation_result}")
            
            if validation_result:
                # Test translation if model is valid
                try:
                    test_text = self.test_phrases["en"][0]
                    translation = self.translation_service.translate(
                        test_text,
                        source_lang="en",
                        target_lang="ary",
                        model_name=model_name
                    )
                    logger.info(f"Translation test: '{test_text}' -> '{translation}'")
                except Exception as e:
                    logger.error(f"Translation failed for {model_name}: {str(e)}")
            
            self.assertTrue(validation_result, f"Validation failed for model {model_name}")

if __name__ == '__main__':
    unittest.main()
