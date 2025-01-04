#test_data_sample/BounharAbdelaziz/English-to-Moroccan-Darija/README.md
metadata
language:
  - ar
size_categories:
  - 10K<n<100K
task_categories:
  - translation
dataset_info:
  features:
    - name: english
      dtype: string
    - name: darija
      dtype: string
    - name: includes_arabizi
      dtype: bool
  splits:
    - name: train
      num_bytes: 2898935
      num_examples: 16089
  download_size: 1704472
  dataset_size: 2898935
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train-*