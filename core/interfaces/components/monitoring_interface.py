"""
Monitoring interface component for system metrics
"""
import streamlit as st
import logging
import psutil
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class MonitoringInterface:
    """Interface component for system monitoring"""
    
    def __init__(self):
        """Initialize interface"""
        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()
            
    def get_system_metrics(self):
        """Get current system metrics"""
        return {
            "CPU Usage": f"{psutil.cpu_percent()}%",
            "Memory Usage": f"{psutil.virtual_memory().percent}%",
            "Uptime": self.get_uptime(),
            "Last Updated": datetime.now().strftime("%H:%M:%S")
        }
        
    def get_uptime(self):
        """Calculate uptime"""
        uptime = time.time() - st.session_state.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    def render(self):
        """Render the monitoring interface"""
        metrics = self.get_system_metrics()
        
        st.write("System Metrics:")
        for metric, value in metrics.items():
            st.text(f"{metric}: {value}")
            
        # Add refresh button
        if st.button("Refresh Metrics"):
            st.rerun()
    
    def update(self):
        """Update interface state"""
        pass
