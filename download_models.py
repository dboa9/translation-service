import os
from pathlib import Path
import yaml
import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from tqdm import tqdm
import requests
import warnings

# Filter out specific warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Get absolute path to project root
PROJECT_ROOT = Path(__file__).parent.absolute()

# Set cache directory to local project path
CACHE_DIR = PROJECT_ROOT / "model_cache"
os.environ["TRANSFORMERS_CACHE"] = str(CACHE_DIR)
os.environ["HF_HOME"] = str(CACHE_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("model_download.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def download_models():
    """Download and cache translation models locally."""
    try:
        # Create cache directory
        CACHE_DIR.mkdir(exist_ok=True, parents=True)
        
        # Load model configuration
        config_path = PROJECT_ROOT / "config" / "model_config.yaml"
        if not config_path.exists():
            logger.error(f"Config file not found at: {config_path}")
            return False
            
        with open(config_path) as f:
            config = yaml.safe_load(f)
            
        if not isinstance(config, dict) or 'translation_models' not in config:
            logger.error("Invalid configuration format")
            return False
            
        # Load HuggingFace token
        from config.credentials import HUGGINGFACE_TOKEN
            
        # Download each model
        total_models = len(config['translation_models'])
        successful_downloads = 0
        
        for model_name in tqdm(config['translation_models'], desc="Downloading models"):
            try:
                logger.info(f"Downloading model: {model_name}")
                model_dir = CACHE_DIR / model_name.replace("/", "_")
                model_dir.mkdir(exist_ok=True, parents=True)
                
                if model_dir.exists():
                    # Verify model files exist
                    if (model_dir / "pytorch_model.bin").exists() or \
                       (model_dir / "model.safetensors").exists():
                        logger.info(f"Model {model_name} already cached")
                        successful_downloads += 1
                        continue
                
                # Force CPU usage to avoid CUDA issues
                device_map = "cpu"
                
                # Download model and tokenizer
                logger.info("Downloading model files...")
                model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    token=HUGGINGFACE_TOKEN,
                    cache_dir=str(model_dir),
                    local_files_only=False,
                    device_map=device_map
                )
                
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    token=HUGGINGFACE_TOKEN,
                    cache_dir=str(model_dir),
                    local_files_only=False
                )
                
                # Save locally
                logger.info("Saving model files...")
                model.save_pretrained(
                    str(model_dir),
                    safe_serialization=True
                )
                tokenizer.save_pretrained(str(model_dir))
                
                logger.info(f"Successfully downloaded and cached model: {model_name}")
                successful_downloads += 1
                
            except Exception as e:
                logger.error(f"Error downloading model {model_name}: {str(e)}")
                continue
                
        logger.info(f"Model download complete. Successfully downloaded {successful_downloads}/{total_models} models")
        return successful_downloads > 0
        
    except Exception as e:
        logger.error(f"Error during model download: {str(e)}")
        return False

if __name__ == "__main__":
    # Disable CUDA to avoid warnings and issues
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    success = download_models()
    exit(0 if success else 1)
