#!/usr/bin/env python3
"""
Podcast Tracker - Fetches recent episodes from favorite podcasts using iTunes API
and extracts the actual MP3 file URLs for direct playback
"""

import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import utility modules
from utils.logging_config import logger
from utils.constants import MAX_WORKERS
from utils.cli import parse_arguments
from utils.git_utils import commit_and_push_changes
from utils.email_utils import send_email_update

# Import core modules
from core.data import (
    load_podcasts,
    load_ignored_podcasts,
    save_podcasts_csv,
    save_results_to_json
)
from core.processor import process_podcast

def main():
    """Main function to track recent podcast episodes."""
    start_time = time.time()
    args = parse_arguments()
    
    logger.info(f"Starting podcast tracker (looking back {args.hours} hours)")
    
    # Load podcasts from CSV
    podcasts_df = load_podcasts(args.csv)
    if podcasts_df.empty:
        logger.error("No podcasts found in CSV file. Exiting.")
        return
    
    # Load ignored podcasts
    ignored_podcasts_df = load_ignored_podcasts(args.ignored_csv)
    
    # Get list of active podcasts (not in ignored list)
    active_podcasts = []
    for podcast in podcasts_df['podcast_name'].tolist():
        if ignored_podcasts_df.empty or podcast not in ignored_podcasts_df['podcast_name'].values:
            active_podcasts.append(podcast)
    
    logger.info(f"Loaded {len(active_podcasts)} active podcasts from {args.csv}")
    if not ignored_podcasts_df.empty:
        logger.info(f"Ignoring {len(ignored_podcasts_df)} podcasts from {args.ignored_csv}")
    
    # Track recent episodes using parallel processing
    recent_episodes = []
    feed_urls_updated = False
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tasks for each podcast
        future_to_podcast = {}
        for podcast in active_podcasts:
            future = executor.submit(
                process_podcast, 
                podcast, 
                args.hours, 
                args.max_episodes,
                podcasts_df if args.update_feeds else None,
                args.update_feeds
            )
            future_to_podcast[future] = podcast
        
        # Process results as they complete
        for future in as_completed(future_to_podcast):
            podcast = future_to_podcast[future]
            try:
                podcast_episodes, feed_updated = future.result()
                recent_episodes.extend(podcast_episodes)
                if feed_updated:
                    feed_urls_updated = True
                logger.info(f"Processed podcast: {podcast} - Found {len(podcast_episodes)} recent episodes")
            except Exception as e:
                logger.error(f"Error processing podcast {podcast}: {e}")
    
    # Save updated podcasts CSV if feed URLs were updated
    files_to_commit = []
    if args.update_feeds and feed_urls_updated:
        if save_podcasts_csv(podcasts_df, args.csv):
            files_to_commit.append(args.csv)
    
    # Save results to JSON
    if recent_episodes:
        if save_results_to_json(recent_episodes, args.output):
            logger.info(f"Found {len(recent_episodes)} recent episodes. Saved to {args.output}")
            files_to_commit.append(args.output)
        else:
            logger.error(f"Error saving results to {args.output}")
    else:
        logger.info(f"No recent episodes found in the last {args.hours} hours")
        # Create empty file
        try:
            with open(args.output, 'w') as f:
                json.dump([], f)
            files_to_commit.append(args.output)
        except Exception as e:
            logger.error(f"Error creating empty output file {args.output}: {e}")
    
    # Commit and push changes if requested
    if args.commit_changes and files_to_commit:
        commit_success = commit_and_push_changes(files_to_commit)
        if commit_success:
            logger.info("Changes committed and pushed to repository")
        else:
            logger.warning("Failed to commit changes to repository")
    
    # Send email update if requested
    if args.email or (args.email_address and args.email_password):
        logger.info("Sending email update...")
        email_sent = send_email_update(recent_episodes, args.email_address, args.email_password)
        if email_sent:
            logger.info("Email update sent successfully")
        else:
            logger.warning("Failed to send email update")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Podcast tracker completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main() 