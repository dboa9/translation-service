#test_data_sample/atlasia/darija_english/README.md
metadata
license: cc-by-nc-4.0
task_categories:
  - translation
language:
  - en
  - ar
size_categories:
  - 100K<n<1M
configs:
  - config_name: web_data
    data_files: atlasia_web_data.csv
  - config_name: comments
    data_files: atlasia_comments.csv
  - config_name: stories
    data_files: atlasia_stories.csv
  - config_name: doda
    data_files: atlasia_doda.csv
  - config_name: transliteration
    data_files: atlasia_atam.csv