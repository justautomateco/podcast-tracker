#!/usr/bin/env python3
"""
Git utilities for the podcast tracker application
"""

import subprocess
from utils.logging_config import logger

def commit_and_push_changes(files_to_commit):
    """
    Commit and push changes to the repository.
    
    Args:
        files_to_commit (list): List of files to commit
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Configure Git user
        subprocess.run(["git", "config", "--global", "user.name", "Podcast Tracker Bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "bot@example.com"], check=True)
        
        # Add files
        for file in files_to_commit:
            subprocess.run(["git", "add", file], check=True)
        
        # Commit changes
        commit_message = f"Update podcast data ({len(files_to_commit)} files)"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push changes
        subprocess.run(["git", "push"], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Error in commit_and_push_changes: {e}")
        return False 