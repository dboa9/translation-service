#!/bin/bash
# File: start_ui.sh
# Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service/start_ui.sh
# Author: dboa9 (danielalchemy9@gmail.com)

echo "Starting Streamlit UI..."
streamlit run core/interfaces/streamlit_interface.py --server.port 8501 --server.address 0.0.0.0