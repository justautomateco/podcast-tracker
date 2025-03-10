#!/usr/bin/env python3
"""
Constants used throughout the podcast tracker application
"""

# Global constants
REQUEST_TIMEOUT = 10  # Timeout for HTTP requests in seconds
MAX_EPISODES_PER_PODCAST = 5  # Maximum number of episodes to process per podcast
MAX_WORKERS = 4  # Maximum number of concurrent threads

# Default file paths
DEFAULT_PODCASTS_CSV = "podcasts.csv"
DEFAULT_IGNORED_CSV = "ignored_podcasts.csv"
DEFAULT_OUTPUT_JSON = "recent_episodes.json"
DEFAULT_OUTPUT_MARKDOWN = "recent_episodes.md"

# ... existing code ... 