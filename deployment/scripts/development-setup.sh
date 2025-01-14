# !/bin/bash
# development_setup.sh
# Location: /home/ubuntu/darija_project_new/deployment/scripts/development_setup.sh

# Base directories
BASE_DIR="/home/ubuntu/darija_project_new"
VENV_NAME="venv_new_2"
LOG_DIR="${BASE_DIR}/logs"
MONITORING_DIR="${BASE_DIR}/monitoring"

# Create necessary directories
mkdir -p "${BASE_DIR}"/{core,web,monitoring,logs,models/checkpoints}
mkdir -p "${BASE_DIR}/web/components/monitoring/metrics"
mkdir -p "${BASE_DIR}/web/hooks"
mkdir -p "${LOG_DIR}"/{training,monitoring,system}

# Python environment setup
python3 -m venv "${BASE_DIR}/${VENV_NAME}"
source "${BASE_DIR}/${VENV_NAME}/bin/activate"

# Install Python dependencies
pip install -r requirements.txt
pip install fastapi uvicorn psutil tensorboard torch

# Install Node.js and npm for monitoring dashboard
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Set up monitoring dashboard
cd "${BASE_DIR}/web"
npm install @tremor/react lucide-react cors

# Create supervisor configs for parallel processes
sudo tee /etc/supervisor/conf.d/darija_training.conf <<EOF
[program:darija_training]
command=${BASE_DIR}/${VENV_NAME}/bin/python ${BASE_DIR}/core/train_and_evaluate.py
directory=${BASE_DIR}
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=${LOG_DIR}/training/training.err.log
stdout_logfile=${LOG_DIR}/training/training.out.log
EOF

sudo tee /etc/supervisor/conf.d/darija_monitoring.conf <<EOF
[program:darija_monitoring]
command=${BASE_DIR}/${VENV_NAME}/bin/uvicorn core.api.metrics_api:app --host 0.0.0.0 --port 8000
directory=${BASE_DIR}
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=${LOG_DIR}/monitoring/monitoring.err.log
stdout_logfile=${LOG_DIR}/monitoring/monitoring.out.log
EOF

# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Create environment variables file
tee "${BASE_DIR}/.env" <<EOF
PYTHONPATH=${BASE_DIR}
MODEL_DIR=${BASE_DIR}/models/checkpoints
MONITORING_INTERVAL=5
LOG_LEVEL=DEBUG
EOF

# Set up monitoring dashboard development server
cd "${BASE_DIR}/web"
npm run dev &

echo "Development environment setup complete!"
echo "Training logs: ${LOG_DIR}/training/"
echo "Monitoring dashboard: http://localhost:3000"
echo "Metrics API: http://localhost:8000/api/metrics"
