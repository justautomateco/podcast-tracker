# Podcast Tracker

A Python application that tracks new episodes from your favorite podcasts using the iTunes API. The tracker runs automatically via GitHub Actions on a daily schedule or can be triggered manually.

Repository: [https://github.com/justautomateco/postcast_tracker](https://github.com/justautomateco/postcast_tracker)

## Features

- Track new podcast episodes from a list of your favorite podcasts
- Extract direct MP3 file URLs for each episode
- Configurable time window (last 24 hours, 48 hours, etc.)
- Automated daily checks via GitHub Actions
- Manual trigger option
- CSV-based podcast list management

## Setup

1. Fork this repository from [https://github.com/justautomateco/postcast_tracker](https://github.com/justautomateco/postcast_tracker)
2. Edit `podcasts.csv` to include your favorite podcasts
3. Push changes to GitHub to activate the workflow

## Running with GitHub Actions

The workflow is configured to run:
- Automatically every day at midnight UTC
- Manually via the GitHub Actions UI

To trigger the workflow manually:
1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select the "Podcast Tracker" workflow
4. Click "Run workflow"
5. Choose how many hours to look back (24, 48, or 72)
6. Click "Run workflow"

## Output

The script will output new episodes found in the specified time window to:
1. A JSON file (`recent_episodes.json`) committed to the repository with direct MP3 URLs
2. A log file (`podcast_tracker.log`) committed to the repository
3. Workflow artifacts that can be downloaded from the Actions tab 