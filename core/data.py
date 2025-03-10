#!/usr/bin/env python3
"""
Data loading and saving functions for the podcast tracker application
"""

import csv
import json
import pandas as pd
from utils.logging_config import logger

def load_podcasts(csv_path):
    """
    Load podcasts from a CSV file.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: DataFrame containing podcast data
    """
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        logger.error(f"Error loading podcasts from {csv_path}: {e}")
        return pd.DataFrame(columns=['podcast_name', 'feed_url'])

def load_ignored_podcasts(csv_path):
    """
    Load ignored podcasts from a CSV file.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: DataFrame containing ignored podcast data
    """
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        logger.warning(f"Error loading ignored podcasts from {csv_path}: {e}")
        return pd.DataFrame(columns=['podcast_name'])

def update_feed_url(podcasts_df, podcast_name, feed_url):
    """
    Update the feed URL for a podcast in the DataFrame.
    
    Args:
        podcasts_df (pandas.DataFrame): DataFrame containing podcast data
        podcast_name (str): Name of the podcast to update
        feed_url (str): New feed URL
        
    Returns:
        bool: True if updated, False otherwise
    """
    if podcast_name in podcasts_df['podcast_name'].values:
        podcasts_df.loc[podcasts_df['podcast_name'] == podcast_name, 'feed_url'] = feed_url
        return True
    return False

def save_podcasts_csv(podcasts_df, csv_path):
    """
    Save podcasts DataFrame to a CSV file.
    
    Args:
        podcasts_df (pandas.DataFrame): DataFrame containing podcast data
        csv_path (str): Path to the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        podcasts_df.to_csv(csv_path, index=False)
        logger.info(f"Updated podcasts saved to {csv_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving podcasts to {csv_path}: {e}")
        return False

def save_results_to_json(recent_episodes, output_path):
    """
    Save recent episodes to a JSON file.
    
    Args:
        recent_episodes (list): List of recent episodes
        output_path (str): Path to the output JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(recent_episodes, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving results to {output_path}: {e}")
        return False

def save_results_to_markdown(recent_episodes, output_path):
    """
    Save recent episodes to a Markdown file for easy clicking and viewing.
    
    Args:
        recent_episodes (list): List of recent episodes
        output_path (str): Path to the output Markdown file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(output_path, 'w') as f:
            f.write("# Recent Podcast Episodes\n\n")
            f.write("Last updated: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
            
            # Group episodes by podcast
            podcasts = {}
            for episode in recent_episodes:
                podcast_name = episode.get('podcast_name', 'Unknown Podcast')
                if podcast_name not in podcasts:
                    podcasts[podcast_name] = []
                podcasts[podcast_name].append(episode)
            
            # Write episodes grouped by podcast
            for podcast_name, episodes in podcasts.items():
                f.write(f"## {podcast_name}\n\n")
                
                for episode in episodes:
                    title = episode.get('episode_title', 'Untitled Episode')
                    release_date = episode.get('release_date', 'Unknown date')
                    mp3_url = episode.get('mp3_url', '')
                    
                    f.write(f"### {title}\n\n")
                    f.write(f"**Released:** {release_date}\n\n")
                    f.write(f"**Listen:** [Direct MP3 Link]({mp3_url})\n\n")
                    f.write("---\n\n")
            
        logger.info(f"Markdown file generated at {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving markdown to {output_path}: {e}")
        return False 