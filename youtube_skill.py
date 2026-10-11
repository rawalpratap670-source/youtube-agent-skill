import argparse
import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from googleapiclient.discovery import build


load_dotenv()


class YouTubeSkill:
    """A simple skill for searching YouTube videos using the Data API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "YOUTUBE_API_KEY is missing. Set it in your environment or .env file."
            )
        self.service = build("youtube", "v3", developerKey=self.api_key)

    def search_videos(
        self,
        query: str,
        max_results: int = 5,
        region_code: str = "US",
        order: str = "relevance",
        safe_search: str = "moderate",
        video_duration: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for YouTube videos and return normalized metadata."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        request = (
            self.service.search()
            .list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                regionCode=region_code,
                order=order,
                safeSearch=safe_search,
                videoDuration=video_duration,
            )
        )

        response = request.execute()
        items = response.get("items", [])

        results: List[Dict[str, Any]] = []
        for item in items:
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue

            results.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "channel": snippet.get("channelTitle"),
                    "channel_id": snippet.get("channelId"),
                    "published_at": snippet.get("publishedAt"),
                    "thumbnail_url": (
                        snippet.get("thumbnails", {})
                        .get("high", {})
                        .get("url")
                        or snippet.get("thumbnails", {})
                        .get("medium", {})
                        .get("url")
                        or snippet.get("thumbnails", {})
                        .get("default", {})
                        .get("url")
                    ),
                    "watch_url": f"https://www.youtube.com/watch?v={video_id}",
                    "channel_url": (
                        f"https://www.youtube.com/channel/{snippet.get('channelId')}"
                        if snippet.get("channelId")
                        else None
                    ),
                }
            )

        return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Search YouTube videos")
    parser.add_argument("query", help="Search query to run against YouTube")
    parser.add_argument("--max-results", type=int, default=5, help="Number of results to return")
    parser.add_argument("--region-code", default="US", help="Region code for results")
    parser.add_argument("--order", default="relevance", help="YouTube result ordering")
    parser.add_argument("--safe-search", default="moderate", help="YouTube safe search level")
    parser.add_argument("--video-duration", default=None, help="Optional video duration filter: any, short, medium, long")
    args = parser.parse_args()

    skill = YouTubeSkill()
    results = skill.search_videos(
        query=args.query,
        max_results=args.max_results,
        region_code=args.region_code,
        order=args.order,
        safe_search=args.safe_search,
        video_duration=args.video_duration,
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
