#!/usr/bin/env python3
"""
RSS feed processing for the podcast tracker application
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from utils.logging_config import logger
from utils.constants import REQUEST_TIMEOUT

def extract_mp3_url_from_feed(feed_url, episode_guid=None):
    """
    Extract MP3 URLs from a podcast RSS feed.
    
    Args:
        feed_url (str): URL of the podcast RSS feed
        episode_guid (str, optional): GUID of a specific episode to extract
        
    Returns:
        list: List of dictionaries containing episode information
    """
    try:
        # Get feed content
        response = requests.get(feed_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Find namespace
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        
        # Extract channel information
        channel = root.find('channel')
        if channel is None:
            logger.error(f"Invalid feed format: {feed_url}")
            return []
        
        # Process episodes
        episodes = []
        for item in channel.findall('item'):
            # Extract episode GUID
            guid_elem = item.find('guid')
            guid = guid_elem.text if guid_elem is not None else None
            
            # Skip if we're looking for a specific episode and this isn't it
            if episode_guid and guid != episode_guid:
                continue
            
            # Extract episode title
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None else "Untitled Episode"
            
            # Extract publication date
            pub_date_elem = item.find('pubDate')
            pub_date = None
            if pub_date_elem is not None and pub_date_elem.text:
                try:
                    pub_date = parser.parse(pub_date_elem.text)
                    pub_date = pub_date.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pub_date = "Unknown"
            
            # Extract enclosure URL (MP3)
            enclosure = item.find('enclosure')
            mp3_url = None
            if enclosure is not None:
                mp3_url = enclosure.get('url')
            
            # Add episode to list if we found an MP3 URL
            if mp3_url:
                episodes.append({
                    'guid': guid,
                    'episode_title': title,
                    'release_date': pub_date,
                    'mp3_url': mp3_url
                })
            
            # If we found the specific episode we were looking for, we're done
            if episode_guid and guid == episode_guid:
                break
        
        return episodes
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching feed {feed_url}: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"Error parsing feed {feed_url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error processing feed {feed_url}: {e}")
        return []

def is_recent_episode(release_date, hours_ago):
    """
    Check if an episode was released within the specified time window.
    
    Args:
        release_date (str): Release date string in format 'YYYY-MM-DD HH:MM:SS'
        hours_ago (int): Number of hours to look back
        
    Returns:
        bool: True if the episode is recent, False otherwise
    """
    if not release_date or release_date == "Unknown":
        return False
    
    try:
        # Parse release date
        episode_date = parser.parse(release_date)
        
        # Ensure timezone awareness
        if episode_date.tzinfo is None:
            episode_date = pytz.utc.localize(episode_date)
        
        # Calculate time window
        now = datetime.now(pytz.utc)
        time_window = now - timedelta(hours=hours_ago)
        
        # Check if episode is within time window
        return episode_date >= time_window
    except Exception as e:
        logger.error(f"Error checking if episode is recent: {e}")
        return False 