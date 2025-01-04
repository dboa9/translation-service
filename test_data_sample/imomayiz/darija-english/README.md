#test_data_sample/imomayiz/darija-english/README.md

metadata
language:
  - ar
  - en
license: cc
task_categories:
  - translation
configs:
  - config_name: sentences
    data_files:
      - split: sentences
        path: sentences.csv
    sep: ','
  - config_name: submissions
    data_files:
      - split: submissions
        path: submissions/submissions*.json