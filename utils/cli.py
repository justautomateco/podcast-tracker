#!/usr/bin/env python3
"""
Command-line interface for the podcast tracker application
"""

import argparse
from utils.constants import (
    DEFAULT_PODCASTS_CSV,
    DEFAULT_IGNORED_CSV,
    DEFAULT_OUTPUT_JSON,
    MAX_EPISODES_PER_PODCAST
)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Track new podcast episodes')
    parser.add_argument(
        '--hours', 
        type=int, 
        default=168,  # 1 week
        help='Number of hours to look back for new episodes (default: 168, which is 1 week)'
    )
    parser.add_argument(
        '--max-episodes', 
        type=int, 
        default=MAX_EPISODES_PER_PODCAST,
        help=f'Maximum number of episodes to process per podcast (default: {MAX_EPISODES_PER_PODCAST})'
    )
    parser.add_argument(
        '--csv', 
        type=str, 
        default=DEFAULT_PODCASTS_CSV,
        help=f'Path to CSV file containing podcast list (default: {DEFAULT_PODCASTS_CSV})'
    )
    parser.add_argument(
        '--ignored-csv', 
        type=str, 
        default=DEFAULT_IGNORED_CSV,
        help=f'Path to CSV file containing ignored podcasts (default: {DEFAULT_IGNORED_CSV})'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default=DEFAULT_OUTPUT_JSON,
        help=f'Path to output JSON file (default: {DEFAULT_OUTPUT_JSON})'
    )
    parser.add_argument(
        '--update-feeds', 
        action='store_true',
        help='Update feed URLs in the podcasts CSV file'
    )
    parser.add_argument(
        '--commit-changes', 
        action='store_true',
        help='Commit and push changes to the repository'
    )
    parser.add_argument(
        '--email', 
        action='store_true',
        help='Send email update with recent episodes'
    )
    parser.add_argument(
        '--email-address', 
        type=str,
        help='Email address to send updates to'
    )
    parser.add_argument(
        '--email-password', 
        type=str,
        help='Email password or app password for authentication'
    )
    
    return parser.parse_args() 