# Podcast Tracker

A Python application that tracks new episodes from your favorite podcasts using the iTunes API. The tracker runs automatically via GitHub Actions on a daily schedule or can be triggered manually.

Repository: [https://github.com/justautomateco/podcast-tracker](https://github.com/justautomateco/podcast-tracker)

## Features

- Track new podcast episodes from a list of your favorite podcasts
- Extract direct MP3 file URLs for each episode
- Configurable time window (last 24 hours, 48 hours, etc.)
- Automated daily checks via GitHub Actions
- Manual trigger option
- CSV-based podcast list management

## Setup

1. Fork this repository from [https://github.com/justautomateco/podcast-tracker](https://github.com/justautomateco/podcast-tracker)
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
2. A markdown file (`recent_episodes.md`) with clickable links to episodes, organized by podcast
3. A log file (`podcast_tracker.log`) committed to the repository
4. Workflow artifacts that can be downloaded from the Actions tab

## Project Structure

The project has been refactored into a modular structure:

```
podcast-tracker/
├── podcast_tracker.py     # Main script
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── cli.py             # Command-line interface
│   ├── constants.py       # Global constants
│   ├── email_utils.py     # Email functionality
│   ├── git_utils.py       # Git operations
│   └── logging_config.py  # Logging configuration
├── core/                  # Core functionality
│   ├── __init__.py
│   ├── data.py            # Data loading and saving
│   ├── feed.py            # RSS feed processing
│   ├── itunes.py          # iTunes API interactions
│   └── processor.py       # Podcast processing
├── podcasts.csv           # List of podcasts to track
├── ignored_podcasts.csv   # List of podcasts to ignore
└── requirements.txt       # Python dependencies
```

This modular structure makes the code more maintainable and easier to understand. 

## Command-line Options

The podcast tracker supports the following command-line options:

```
--hours HOURS             Number of hours to look back for new episodes (default: 168, which is 1 week)
--max-episodes MAX        Maximum number of episodes to process per podcast (default: 5)
--csv CSV                 Path to CSV file containing podcast list (default: podcasts.csv)
--ignored-csv IGNORED_CSV Path to CSV file containing ignored podcasts (default: ignored_podcasts.csv)
--output OUTPUT           Path to output JSON file (default: recent_episodes.json)
--markdown MARKDOWN       Path to output Markdown file (default: recent_episodes.md)
--generate-markdown       Generate a Markdown file with clickable links to episodes
--update-feeds            Update feed URLs in the podcasts CSV file
--commit-changes          Commit and push changes to the repository
--email                   Send email update with recent episodes
--email-address EMAIL     Email address to send updates to
--email-password PASSWORD Email password or app password for authentication
```

Example usage:

```bash
# Generate a markdown file with recent episodes from the last 24 hours
python podcast_tracker.py --hours 24 --generate-markdown

# Update feed URLs and commit changes to the repository
python podcast_tracker.py --update-feeds --commit-changes --generate-markdown
``` 