# YouTube Agent Skill

A lightweight Python skill for discovering YouTube videos and retrieving structured metadata using the YouTube Data API v3.

## Features
- Search for videos by keyword or phrase
- Return normalized metadata for each result
- Fetch richer details for a specific video ID
- Search for channels when broader discovery is needed
- Designed for agent workflows and simple CLI usage

## Setup

1. Create a Google Cloud project and enable the YouTube Data API v3.
2. Create an API key.
3. Copy the env file and add your key:

```bash
cp .env.example .env
```

Then update `.env`:

```env
YOUTUBE_API_KEY=your_api_key_here
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Python

```python
from youtube_skill import YouTubeSkill

skill = YouTubeSkill()

results = skill.search_videos("python tutorials", max_results=5)
print(results)

video_details = skill.get_video_details([results[0]["video_id"]])
print(video_details)
```

### CLI

```bash
python youtube_skill.py "python tutorials" --max-results 5 --include-details
```

## Example output

```json
[
  {
    "video_id": "abc123",
    "title": "Python Tutorial for Beginners",
    "channel": "freeCodeCamp.org",
    "channel_id": "UC...",
    "published_at": "2024-01-15T10:00:00Z",
    "description": "Learn Python from scratch",
    "thumbnail_url": "https://i.ytimg.com/vi/abc123/hqdefault.jpg",
    "watch_url": "https://www.youtube.com/watch?v=abc123",
    "channel_url": "https://www.youtube.com/channel/UC..."
  }
]
```

## Notes

- YouTube API usage is subject to quota limits.
- Search results depend on query quality and API quota availability.
- This skill is intentionally focused on discovery, metadata retrieval, and agent-friendly output.
