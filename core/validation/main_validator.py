#tests/core/validation/main_validator.py
import logging
import json
from core.config_analysis.column_mapping_analyzer import analyze_column_mapping
from core.dataset_integration.integration_checker import check_all_datasets

logger = logging.getLogger(__name__)

CACHE_FILE = 'validation_results_cache.json'

def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def validate_all():
    cache = load_cache()
    
    # Phase 1: Structure Check
    if 'column_mapping_valid' not in cache:
        cache['column_mapping_valid'] = analyze_column_mapping()
        save_cache(cache)
    
    if not cache['column_mapping_valid']:
        logger.error("Column mapping validation failed. Stopping further validation.")
        return False
    
    # Phase 2: Dataset Integration
    if 'dataset_integration' not in cache:
        cache['dataset_integration'] = check_all_datasets()
        save_cache(cache)
    
    all_datasets_valid = all(cache['dataset_integration'].values())
    
    if all_datasets_valid:
        logger.info("All datasets passed integration checks.")
    else:
        logger.warning("Some datasets failed integration checks. Check logs for details.")
    
    return all_datasets_valid

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = validate_all()
    print(f"Validation {'succeeded' if result else 'failed'}.")
