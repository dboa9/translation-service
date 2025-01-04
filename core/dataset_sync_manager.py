import os
from datasets import load_dataset_builder
from huggingface_hub import HfApi
import json

class DatasetSyncManager:
    def __init__(self, cache_dir, datasets_config):
        self.cache_dir = cache_dir
        self.datasets_config = datasets_config
        self.hf_api = HfApi()

    def check_and_sync_datasets(self):
        for dataset_name, configs in self.datasets_config.items():
            for config in configs['subsets']:
                self._check_and_sync_dataset(dataset_name, config)

    def _check_and_sync_dataset(self, dataset_name, config):
        try:
            # Check if the dataset is already in the cache
            builder = load_dataset_builder(dataset_name, config, cache_dir=self.cache_dir)
            if not builder.cache_dir:
                print(f"Downloading {dataset_name} ({config}) to cache...")
                builder.download_and_prepare()
            
            # Check if the local version is up to date
            repo_info = self.hf_api.repo_info(repo_id=dataset_name, repo_type="dataset")
            local_info_path = os.path.join(self.cache_dir, dataset_name, config, "dataset_info.json")
            
            if os.path.exists(local_info_path):
                with open(local_info_path, 'r') as f:
                    local_info = json.load(f)
                
                if local_info.get('version') != repo_info.sha:
                    print(f"Updating {dataset_name} ({config})...")
                    builder.download_and_prepare(ignore_verifications=True)
            else:
                print(f"Local info not found for {dataset_name} ({config}). Downloading...")
                builder.download_and_prepare(ignore_verifications=True)
            
            print(f"{dataset_name} ({config}) is up to date.")
        except Exception as e:
            print(f"Error syncing {dataset_name} ({config}): {str(e)}")

# Usage example
if __name__ == "__main__":
    cache_dir = "/path/to/your/cache/directory"
    datasets_config = {
        "atlasia/darija_english": {
            "subsets": ["web_data", "comments", "stories", "doda", "transliteration"]
        },
        "imomayiz/darija-english": {
            "subsets": ["sentences", "submissions"]
        },
        "M-A-D/DarijaBridge": {
            "subsets": [None]
        },
        "BounharAbdelaziz/English-to-Moroccan-Darija": {
            "subsets": [None]
        }
    }
    
    sync_manager = DatasetSyncManager(cache_dir, datasets_config)
    sync_manager.check_and_sync_datasets()
