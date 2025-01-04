#!/bin/bash

# Activate the conda environment
conda activate dataset_test_deploy_ec2

# Run the streamlit interface with absolute imports
streamlit run core/interfaces/streamlit_interface_absolute.py
