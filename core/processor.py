#!/usr/bin/env python3
"""
Podcast processing for the podcast tracker application
"""

from utils.logging_config import logger
from utils.constants import MAX_EPISODES_PER_PODCAST
from core.itunes import search_podcast, get_podcast_feed, get_feed_url
from core.feed import extract_mp3_url_from_feed, is_recent_episode
from core.data import update_feed_url
import pandas as pd

def process_podcast(podcast_name, hours_ago, max_episodes=MAX_EPISODES_PER_PODCAST, podcasts_df=None, update_feeds=False):
    """
    Process a podcast to find recent episodes.
    
    Args:
        podcast_name (str): Name of the podcast to process
        hours_ago (int): Number of hours to look back for new episodes
        max_episodes (int, optional): Maximum number of episodes to process
        podcasts_df (pandas.DataFrame, optional): DataFrame containing podcast data
        update_feeds (bool, optional): Whether to update feed URLs
        
    Returns:
        tuple: (list of recent episodes, bool indicating if feed URL was updated)
    """
    logger.info(f"Processing podcast: {podcast_name}")
    recent_episodes = []
    feed_url_updated = False
    
    try:
        # Get feed URL from DataFrame if available
        feed_url = None
        if podcasts_df is not None and podcast_name in podcasts_df['podcast_name'].values:
            feed_url = podcasts_df.loc[podcasts_df['podcast_name'] == podcast_name, 'feed_url'].iloc[0]
            if pd.isna(feed_url) or not feed_url:
                feed_url = None
        
        # If no feed URL or update_feeds is True, search for podcast
        if feed_url is None or update_feeds:
            logger.info(f"Searching for podcast: {podcast_name}")
            podcast_data = search_podcast(podcast_name)
            
            if podcast_data:
                # Get podcast ID
                podcast_id = podcast_data.get('collectionId')
                
                if podcast_id:
                    # Get podcast feed data
                    feed_data = get_podcast_feed(podcast_id)
                    
                    if feed_data:
                        # Get feed URL
                        new_feed_url = get_feed_url(feed_data)
                        
                        if new_feed_url:
                            # Update feed URL if it's different
                            if feed_url != new_feed_url:
                                feed_url = new_feed_url
                                
                                # Update feed URL in DataFrame if requested
                                if update_feeds and podcasts_df is not None:
                                    if update_feed_url(podcasts_df, podcast_name, feed_url):
                                        feed_url_updated = True
                                        logger.info(f"Updated feed URL for {podcast_name}")
                                    else:
                                        logger.warning(f"Failed to update feed URL for {podcast_name}")
                        else:
                            logger.warning(f"No feed URL found for {podcast_name}")
                    else:
                        logger.warning(f"No feed data found for {podcast_name}")
                else:
                    logger.warning(f"No podcast ID found for {podcast_name}")
            else:
                logger.warning(f"No podcast data found for {podcast_name}")
        
        # If we have a feed URL, extract episodes
        if feed_url:
            logger.info(f"Extracting episodes from feed: {feed_url}")
            episodes = extract_mp3_url_from_feed(feed_url)
            
            # Process episodes
            for episode in episodes[:max_episodes]:
                # Add podcast name to episode info
                episode['podcast_name'] = podcast_name
                
                # Check if episode is recent
                if is_recent_episode(episode.get('release_date'), hours_ago):
                    recent_episodes.append(episode)
                    logger.info(f"Found recent episode: {episode.get('episode_title')}")
        else:
            logger.warning(f"No feed URL available for {podcast_name}")
    
    except Exception as e:
        logger.error(f"Error processing podcast {podcast_name}: {e}")
    
    return recent_episodes, feed_url_updated 