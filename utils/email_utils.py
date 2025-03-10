#!/usr/bin/env python3
"""
Email utilities for the podcast tracker application
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from utils.logging_config import logger

def send_email_update(recent_episodes, email_address, email_password):
    """
    Send an email update with recent podcast episodes.
    
    Args:
        recent_episodes (list): List of recent episodes
        email_address (str): Email address to send from/to
        email_password (str): Email password or app password
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not email_address or not email_password:
        logger.error("Email address and password are required to send email updates")
        return False
    
    if not recent_episodes:
        logger.info("No recent episodes to include in email update")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = email_address
        msg['Subject'] = f"Podcast Update - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Create email body
        body = "<html><body>"
        body += f"<h1>Podcast Updates - {len(recent_episodes)} New Episodes</h1>"
        
        # Group episodes by podcast
        podcasts = {}
        for episode in recent_episodes:
            podcast_name = episode['podcast_name']
            if podcast_name not in podcasts:
                podcasts[podcast_name] = []
            podcasts[podcast_name].append(episode)
        
        # Add episodes to email body
        for podcast_name, episodes in podcasts.items():
            body += f"<h2>{podcast_name} ({len(episodes)} new episodes)</h2>"
            body += "<ul>"
            for episode in episodes:
                release_date = episode.get('release_date', 'Unknown date')
                episode_title = episode.get('episode_title', 'Untitled episode')
                mp3_url = episode.get('mp3_url', '#')
                
                body += f"<li><strong>{episode_title}</strong> ({release_date})<br>"
                body += f"<a href='{mp3_url}'>Download MP3</a></li>"
            body += "</ul>"
        
        body += "</body></html>"
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_address, email_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        logger.error(f"Error sending email update: {e}")
        return False 