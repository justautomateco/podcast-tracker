#!/usr/bin/env python3
"""
Logging configuration for the podcast tracker application
"""

import logging

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('podcast_tracker.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Create a logger that can be imported by other modules
logger = setup_logging() 