#test_data_sample/M-A-D/DarijaBridge/README.md
metadata
dataset_info:
  features:
    - name: sentence
      dtype: string
    - name: translation
      dtype: string
    - name: translated
      dtype: bool
    - name: corrected
      dtype: bool
    - name: correction
      dtype: string
    - name: quality
      dtype: int64
    - name: metadata
      struct:
        - name: config
          dtype: string
        - name: dataset
          dtype: string
        - name: language
          dtype: string
        - name: split
          dtype: string
        - name: template
          dtype: string
  splits:
    - name: train
      num_bytes: 343412514
      num_examples: 1235091
  download_size: 133902523
  dataset_size: 343412514
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train-*
license: apache-2.0
language:
  - ar
  - en
task_categories:
  - translation
pretty_name: DarijaBridge
size_categories:
  - 1M<n<10M