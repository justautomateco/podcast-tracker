#!/usr/bin/env python3
"""
Podcast Tracker - Fetches recent episodes from favorite podcasts using iTunes API
and extracts the actual MP3 file URLs for direct playback
"""

import os
import csv
import json
import logging
import argparse
import re
import time
from datetime import datetime, timedelta
import requests
import pandas as pd
from dateutil import parser
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('podcast_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global constants
REQUEST_TIMEOUT = 10  # Timeout for HTTP requests in seconds
MAX_EPISODES_PER_PODCAST = 5  # Maximum number of episodes to process per podcast
MAX_WORKERS = 4  # Maximum number of concurrent threads

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Track new podcast episodes')
    parser.add_argument(
        '--hours', 
        type=int, 
        default=168,  # Changed from 24 to 168 (1 week)
        help='Number of hours to look back for new episodes (default: 168, which is 1 week)'
    )
    parser.add_argument(
        '--csv', 
        type=str, 
        default='podcasts.csv',
        help='Path to CSV file containing podcast names (default: podcasts.csv)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='recent_episodes.json',
        help='Path to output JSON file (default: recent_episodes.json)'
    )
    parser.add_argument(
        '--max-episodes', 
        type=int, 
        default=MAX_EPISODES_PER_PODCAST,
        help=f'Maximum number of episodes to process per podcast (default: {MAX_EPISODES_PER_PODCAST})'
    )
    return parser.parse_args()

def load_podcasts(csv_path):
    """Load podcast names from CSV file."""
    try:
        df = pd.read_csv(csv_path)
        if 'podcast_name' not in df.columns:
            logger.error(f"CSV file {csv_path} must contain a 'podcast_name' column")
            return []
        return df['podcast_name'].tolist()
    except Exception as e:
        logger.error(f"Error loading podcasts from {csv_path}: {e}")
        return []

def search_podcast(podcast_name):
    """Search for a podcast in iTunes API."""
    url = "https://itunes.apple.com/search"
    params = {
        "term": podcast_name,
        "entity": "podcast",
        "limit": 1
    }
    
    try:
        logger.info(f"Searching for podcast: {podcast_name}")
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if data["resultCount"] > 0:
            return data["results"][0]
        else:
            logger.warning(f"No podcast found for: {podcast_name}")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"Timeout searching for podcast '{podcast_name}'")
        return None
    except Exception as e:
        logger.error(f"Error searching for podcast '{podcast_name}': {e}")
        return None

def get_podcast_feed(podcast_id):
    """Get podcast feed with episodes from iTunes API."""
    url = f"https://itunes.apple.com/lookup"
    params = {
        "id": podcast_id,
        "entity": "podcastEpisode",
        "limit": 10  # Reduced from 20 to 10 for faster processing
    }
    
    try:
        logger.info(f"Fetching episodes for podcast ID: {podcast_id}")
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if data["resultCount"] > 0:
            return data["results"]
        else:
            logger.warning(f"No episodes found for podcast ID: {podcast_id}")
            return []
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching episodes for podcast ID {podcast_id}")
        return []
    except Exception as e:
        logger.error(f"Error fetching episodes for podcast ID {podcast_id}: {e}")
        return []

def get_feed_url(podcast_data):
    """Extract the RSS feed URL from podcast data."""
    if "feedUrl" in podcast_data:
        return podcast_data["feedUrl"]
    return None

def extract_mp3_url_from_feed(feed_url, episode_guid=None):
    """Extract MP3 URL from podcast RSS feed."""
    if not feed_url:
        return None
    
    try:
        logger.info(f"Extracting MP3 URL from feed: {feed_url}")
        response = requests.get(feed_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        feed_content = response.text
        
        # If we have a specific episode GUID, try to find that episode
        if episode_guid:
            # Find the item with the matching GUID
            item_pattern = re.compile(r'<item>.*?<guid.*?>.*?' + re.escape(episode_guid) + r'.*?</guid>.*?</item>', re.DOTALL)
            item_match = item_pattern.search(feed_content)
            
            if item_match:
                item_content = item_match.group(0)
                # Extract enclosure URL (MP3 file)
                enclosure_pattern = re.compile(r'<enclosure.*?url="(.*?)".*?type="audio/mpeg".*?/>', re.DOTALL)
                enclosure_match = enclosure_pattern.search(item_content)
                
                if enclosure_match:
                    return enclosure_match.group(1)
                
                # Try alternative pattern
                alt_pattern = re.compile(r'<enclosure.*?url="(.*?\.mp3)".*?/>', re.DOTALL)
                alt_match = alt_pattern.search(item_content)
                
                if alt_match:
                    return alt_match.group(1)
        
        # If no specific episode or couldn't find it, just get the most recent MP3
        enclosure_pattern = re.compile(r'<enclosure.*?url="(.*?\.mp3)".*?/>', re.DOTALL)
        enclosure_matches = enclosure_pattern.findall(feed_content)
        
        if enclosure_matches:
            return enclosure_matches[0]  # Return the first MP3 URL found
            
        # Try another pattern for MP3 URLs
        media_pattern = re.compile(r'<media:content.*?url="(.*?\.mp3)".*?/>', re.DOTALL)
        media_matches = media_pattern.findall(feed_content)
        
        if media_matches:
            return media_matches[0]
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout extracting MP3 URL from feed {feed_url}")
    except Exception as e:
        logger.error(f"Error extracting MP3 URL from feed {feed_url}: {e}")
    
    return None

def is_recent_episode(release_date, hours_ago):
    """Check if episode was released within the specified time window."""
    try:
        episode_date = parser.parse(release_date)
        # Make sure the date is timezone-aware
        if episode_date.tzinfo is None:
            episode_date = pytz.UTC.localize(episode_date)
            
        cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=hours_ago)
        return episode_date >= cutoff_time
    except Exception as e:
        logger.error(f"Error parsing date {release_date}: {e}")
        return False

def process_podcast(podcast_name, hours_ago, max_episodes):
    """Process a single podcast and return its recent episodes."""
    recent_episodes = []
    
    # Search for the podcast
    podcast = search_podcast(podcast_name)
    if not podcast:
        return recent_episodes
    
    podcast_id = podcast["collectionId"]
    podcast_title = podcast["collectionName"]
    feed_url = get_feed_url(podcast)
    
    logger.info(f"Found podcast: {podcast_title} (ID: {podcast_id})")
    
    # Get episodes
    results = get_podcast_feed(podcast_id)
    if not results:
        return recent_episodes
        
    # The first result is the podcast itself, the rest are episodes
    episodes = results[1:]
    
    # Filter recent episodes
    episode_count = 0
    for episode in episodes:
        if episode_count >= max_episodes:
            logger.info(f"Reached maximum of {max_episodes} episodes for {podcast_title}")
            break
            
        if "releaseDate" in episode and is_recent_episode(episode["releaseDate"], hours_ago):
            # Try to get the episode GUID if available
            episode_guid = episode.get("episodeGuid", "")
            
            # Get the MP3 URL from the RSS feed
            mp3_url = None
            if feed_url:
                mp3_url = extract_mp3_url_from_feed(feed_url, episode_guid)
            
            episode_info = {
                "podcast_name": podcast_title,
                "episode_title": episode.get("trackName", "Unknown"),
                "release_date": episode.get("releaseDate", "Unknown"),
                "duration": episode.get("trackTimeMillis", 0),
                "description": episode.get("description", ""),
                "episode_url": episode.get("trackViewUrl", ""),
                "mp3_url": mp3_url,
                "feed_url": feed_url
            }
            recent_episodes.append(episode_info)
            episode_count += 1
            
            logger.info(f"Recent episode: {episode_info['episode_title']} ({episode_info['release_date']})")
            if mp3_url:
                logger.info(f"MP3 URL: {mp3_url}")
            else:
                logger.warning(f"Could not extract MP3 URL for episode: {episode_info['episode_title']}")
    
    return recent_episodes

def main():
    """Main function to track recent podcast episodes."""
    start_time = time.time()
    args = parse_arguments()
    
    logger.info(f"Starting podcast tracker (looking back {args.hours} hours)")
    
    # Load podcasts from CSV
    podcasts = load_podcasts(args.csv)
    if not podcasts:
        logger.error("No podcasts found in CSV file. Exiting.")
        return
    
    logger.info(f"Loaded {len(podcasts)} podcasts from {args.csv}")
    
    # Track recent episodes using parallel processing
    recent_episodes = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tasks for each podcast
        future_to_podcast = {
            executor.submit(process_podcast, podcast, args.hours, args.max_episodes): podcast 
            for podcast in podcasts
        }
        
        # Process results as they complete
        for future in as_completed(future_to_podcast):
            podcast = future_to_podcast[future]
            try:
                podcast_episodes = future.result()
                recent_episodes.extend(podcast_episodes)
                logger.info(f"Processed podcast: {podcast} - Found {len(podcast_episodes)} recent episodes")
            except Exception as e:
                logger.error(f"Error processing podcast {podcast}: {e}")
    
    # Save results to JSON
    if recent_episodes:
        try:
            with open(args.output, 'w') as f:
                json.dump(recent_episodes, f, indent=2)
            logger.info(f"Found {len(recent_episodes)} recent episodes. Saved to {args.output}")
        except Exception as e:
            logger.error(f"Error saving results to {args.output}: {e}")
    else:
        logger.info(f"No recent episodes found in the last {args.hours} hours")
        # Create empty file
        try:
            with open(args.output, 'w') as f:
                json.dump([], f)
        except Exception as e:
            logger.error(f"Error creating empty output file {args.output}: {e}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Podcast tracker completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main() 