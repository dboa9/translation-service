import os
from datasets import load_dataset, Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from typing import Optional, Union

def load_imomayiz_darija_english_submissions(cache_dir: str) -> Optional[Dataset]:
    try:
        # Construct the path to the dataset directory
        dataset_dir = os.path.join(cache_dir, "imomayiz___darija-english")
        
        # Check if the directory exists
        if not os.path.exists(dataset_dir):
            print(f"Dataset directory not found: {dataset_dir}")
            return None

        # Look for the submissions directory
        submissions_dir = None
        for root, dirs, files in os.walk(dataset_dir):
            if "submissions" in dirs:
                submissions_dir = os.path.join(root, "submissions")
                break

        if not submissions_dir:
            print(f"Submissions directory not found in: {dataset_dir}")
            return None

        # Find the arrow file in the submissions directory
        arrow_file = None
        for file in os.listdir(submissions_dir):
            if file.endswith('.arrow'):
                arrow_file = os.path.join(submissions_dir, file)
                break

        if not arrow_file:
            print(f"Arrow file not found in: {submissions_dir}")
            return None

        # Load the dataset using the datasets library
        result = load_dataset('arrow', data_files=arrow_file, split='train')

        # Ensure we have a Dataset object
        if isinstance(result, Dataset):
            print(f"Successfully loaded dataset with {len(result)} rows")
            return result
        elif isinstance(result, DatasetDict):
            # If we got a DatasetDict, try to get the 'train' split
            if 'train' in result:
                print(f"Successfully loaded dataset with {len(result['train'])} rows")
                return result['train']
            # If no 'train' split, get the first available split
            first_split = next(iter(result.values()))
            if isinstance(first_split, Dataset):
                print(f"Successfully loaded dataset with {len(first_split)} rows")
                return first_split
        
        print(f"Unexpected dataset type: {type(result)}")
        return None

    except Exception as e:
        print(f"Error loading dataset: {str(e)}")
        return None

# You can add more functions here for loading other datasets if needed
