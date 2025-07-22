#!/usr/bin/env python3
"""
Luzern Bus Monitor Add-on Entry Point
This script runs the API server with add-on configuration
"""

import os
import sys
import logging
from home_assistant_bus_monitor import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the add-on"""
    
    # Get configuration from add-on options
    hours_ahead = int(os.environ.get('hours_ahead', 2))
    scan_interval = int(os.environ.get('scan_interval', 30))
    
    # Set environment variables for the API server
    os.environ['BUS_MONITOR_HOURS'] = str(hours_ahead)
    os.environ['BUS_MONITOR_SCAN_INTERVAL'] = str(scan_interval)
    
    logger.info("🚌 Starting Luzern Bus Monitor Add-on")
    logger.info(f"⏰ Time window: {hours_ahead} hours ahead")
    logger.info(f"🔄 Scan interval: {scan_interval} seconds")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,
        debug=False
    )

if __name__ == '__main__':
    main() 