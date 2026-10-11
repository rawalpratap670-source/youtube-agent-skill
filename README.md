# YouTube Agent Skill

A lightweight Python tool for discovering YouTube videos, channels, playlists, and transcript content through the YouTube Data API v3.

This project is built for agent-style tooling and real-time research workflows. It helps you search YouTube, fetch metadata, and retrieve transcript text in a clean JSON-friendly format.

## Why this project

This repo is optimized for a different use case than creator workflow packs like `youtube-agent-skill` built around local video editing and lifecycle tooling.

This project focuses on:
- live search of YouTube videos
- metadata lookup for individual videos
- transcript retrieval when captions exist
- channel and playlist discovery
- structured output for AI/agent usage

## Features
- search videos by keyword
- fetch rich metadata for a video or list of videos
- look up channels and playlists
- retrieve transcripts for video IDs when available
- clean JSON output for agent/tool use
- CLI and Python import support

## Installation

```bash
git clone https://github.com/rawalpratap670-source/youtube-agent-skill.git
cd youtube-agent-skill
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Setup

Create a `.env` file from the sample:

```bash
cp .env.example .env
```

Then add your YouTube Data API key:

```env
YOUTUBE_API_KEY=your_api_key_here
```

## Python usage

```python
from youtube_skill import YouTubeSkill

skill = YouTubeSkill()

results = skill.search_videos("python tutorials", max_results=5)
print(results)

video_details = skill.get_video_details([results[0]["video_id"]])
print(video_details)

transcript = skill.get_video_transcript(results[0]["video_id"])
print(transcript[:3])
```

## CLI usage

```bash
python -m youtube_skill "python tutorials" --max-results 5 --include-details --include-transcript
```

## Example output

```json
{
  "query": "python tutorials",
  "total_results": 5,
  "results": [
    {
      "video_id": "abc123",
      "title": "Python Tutorial for Beginners",
      "channel": "freeCodeCamp.org",
      "channel_id": "UC...",
      "published_at": "2024-01-15T10:00:00Z",
      "description": "Learn Python from scratch",
      "thumbnail_url": "https://i.ytimg.com/vi/abc123/hqdefault.jpg",
      "watch_url": "https://www.youtube.com/watch?v=abc123",
      "channel_url": "https://www.youtube.com/channel/UC...",
      "details": {
        "duration": "PT15M20S",
        "view_count": "1234567",
        "like_count": "45678"
      },
      "transcript": [
        {"text": "Welcome to this Python tutorial", "start": "0", "duration": "3.5"}
      ]
    }
  ]
}
```

## Package structure

```text
youtube-agent-skill/
├── .env.example
├── README.md
├── requirements.txt
├── pyproject.toml
├── youtube_skill.py
├── youtube_skill/
│   ├── __init__.py
│   ├── __main__.py
│   ├── client.py
│   └── __pycache__/
└── tests/
    └── test_basic.py
```

## Notes
- YouTube API usage is subject to quota limits.
- Transcript retrieval depends on availability of captions for the target video.
- This is intentionally focused on live discovery and agent-friendly output, not creator workflow automation.

## License

MIT
