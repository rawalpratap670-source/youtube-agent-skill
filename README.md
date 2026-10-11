# YouTube Agent Skill

A lightweight Python skill for searching YouTube videos using the YouTube Data API v3.

## Features
- Search for videos by keyword or phrase
- Return top results with title, description, channel, published date, thumbnail, and direct watch URL
- Built for simple agent integration or CLI usage

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
```

### CLI

```bash
python youtube_skill.py "python tutorials" --max-results 5
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
    "watch_url": "https://www.youtube.com/watch?v=abc123"
  }
]
```

## Notes

- YouTube API usage is subject to quota limits.
- Search results are best-effort and depend on the query and API quota available.
- This skill focuses on video discovery and metadata retrieval.
