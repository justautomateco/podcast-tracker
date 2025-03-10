#!/usr/bin/env python3
"""
iTunes API interactions for the podcast tracker application
"""

import requests
import time
from utils.logging_config import logger
from utils.constants import REQUEST_TIMEOUT

def search_podcast(podcast_name):
    """
    Search for a podcast using the iTunes API.
    
    Args:
        podcast_name (str): Name of the podcast to search for
        
    Returns:
        dict: Podcast data from iTunes API, or None if not found
    """
    try:
        # Encode podcast name for URL
        encoded_name = requests.utils.quote(podcast_name)
        
        # Search iTunes API
        search_url = f"https://itunes.apple.com/search?term={encoded_name}&entity=podcast&limit=1"
        response = requests.get(search_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        if data['resultCount'] > 0:
            return data['results'][0]
        else:
            logger.warning(f"No podcast found for: {podcast_name}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching for podcast {podcast_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error searching for podcast {podcast_name}: {e}")
        return None

def get_podcast_feed(podcast_id):
    """
    Get podcast feed data from iTunes API.
    
    Args:
        podcast_id (int): iTunes podcast ID
        
    Returns:
        dict: Podcast feed data, or None if not found
    """
    try:
        # Get podcast feed data
        lookup_url = f"https://itunes.apple.com/lookup?id={podcast_id}&entity=podcast"
        response = requests.get(lookup_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        if data['resultCount'] > 0:
            return data['results'][0]
        else:
            logger.warning(f"No podcast feed found for ID: {podcast_id}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting podcast feed for ID {podcast_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting podcast feed for ID {podcast_id}: {e}")
        return None

def get_feed_url(podcast_data):
    """
    Extract feed URL from podcast data.
    
    Args:
        podcast_data (dict): Podcast data from iTunes API
        
    Returns:
        str: Feed URL, or None if not found
    """
    return podcast_data.get('feedUrl') if podcast_data else None 