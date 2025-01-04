#!/bin/bash
# Note: This code should be saved with the current GMT date and time in the format:
# enhanced_streamlit_runner.sh
# Location: /home/ubuntu/darija_project_new/deployment/scripts/enhanced_streamlit_runner.sh
# Author: dboa9 (danielalchemy9@gmail.com)

# Base paths
EC2_PROJECT_DIR="/home/ubuntu/darija_project_new"
VENV_NAME="venv_new_2"
LOG_DIR="${EC2_PROJECT_DIR}/logs"
STREAMLIT_LOG="${LOG_DIR}/streamlit.log"
STREAMLIT_PORT=8501
STREAMLIT_PID_FILE="/tmp/streamlit.pid"

# Enhanced logging
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $level: $message" | tee -a "$STREAMLIT_LOG"
}

# Process management
check_process() {
    if [ -f "$STREAMLIT_PID_FILE" ]; then
        local pid=$(cat "$STREAMLIT_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

stop_streamlit() {
    log "INFO" "Stopping Streamlit process..."
    if [ -f "$STREAMLIT_PID_FILE" ]; then
        local pid=$(cat "$STREAMLIT_PID_FILE")
        kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
        rm -f "$STREAMLIT_PID_FILE"
    fi
}

# Environment checks
check_environment() {
    log "INFO" "Checking environment..."
    
    # Check virtual environment
    if [ ! -d "$EC2_PROJECT_DIR/$VENV_NAME" ]; then
        log "ERROR" "Virtual environment not found"
        exit 1
    fi
    
    # Verify Streamlit installation
    source "$EC2_PROJECT_DIR/$VENV_NAME/bin/activate"
    if ! command -v streamlit &> /dev/null; then
        log "ERROR" "Streamlit not installed"
        exit 1
    }
}

# Port handling
check_port() {
    if lsof -Pi :$STREAMLIT_PORT -sTCP:LISTEN -t >/dev/null; then
        log "WARN" "Port $STREAMLIT_PORT is already in use"
        return 1
    fi
    return 0
}

# Streamlit optimizations
configure_streamlit() {
    log "INFO" "Configuring Streamlit..."
    
    mkdir -p ~/.streamlit
    cat > ~/.streamlit/config.toml << EOF
[server]
port = $STREAMLIT_PORT
address = "0.0.0.0"
baseUrlPath = ""
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200
maxMessageSize = 200

[browser]
serverAddress = "localhost"
gatherUsageStats = false

[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOF
}

# Main execution
main() {
    log "INFO" "Starting Streamlit runner..."
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Check and stop existing process
    if check_process; then
        stop_streamlit
    fi
    
    # Verify environment and port
    check_environment
    if ! check_port; then
        log "ERROR" "Port conflict detected"
        exit 1
    fi
    
    # Configure and start Streamlit
    configure_streamlit
    
    cd "$EC2_PROJECT_DIR"
    source "$VENV_NAME/bin/activate"
    
    # Start Streamlit with optimizations
    streamlit run streamlit_app.py \
        --server.port $STREAMLIT_PORT \
        --server.address 0.0.0.0 \
        --server.maxUploadSize 200 \
        --browser.serverAddress localhost \
        --logger.level info \
        > "$STREAMLIT_LOG" 2>&1 &
    
    echo $! > "$STREAMLIT_PID_FILE"
    log "INFO" "Streamlit started with PID $(cat $STREAMLIT_PID_FILE)"
}

# Execute main function
main