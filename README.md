import argparse
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Sequence

from dotenv import load_dotenv
from googleapiclient.discovery import build


load_dotenv()


class YouTubeSkill:
    """A simple YouTube agent skill for searching videos and retrieving metadata."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "YOUTUBE_API_KEY is missing. Set it in your environment or .env file."
            )
        self.service = build("youtube", "v3", developerKey=self.api_key)

    def _normalize_search_result(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        snippet = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            return None

        thumbnail = (
            snippet.get("thumbnails", {})
            .get("high", {})
            .get("url")
            or snippet.get("thumbnails", {})
            .get("medium", {})
            .get("url")
            or snippet.get("thumbnails", {})
            .get("default", {})
            .get("url")
        )

        return {
            "video_id": video_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "published_at": snippet.get("publishedAt"),
            "thumbnail_url": thumbnail,
            "watch_url": f"https://www.youtube.com/watch?v={video_id}",
            "channel_url": (
                f"https://www.youtube.com/channel/{snippet.get('channelId')}"
                if snippet.get("channelId")
                else None
            ),
        }

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

        params: Dict[str, Any] = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "regionCode": region_code,
            "order": order,
            "safeSearch": safe_search,
        }
        if video_duration is not None:
            params["videoDuration"] = video_duration

        response = self.service.search().list(**params).execute()
        items = response.get("items", [])

        results: List[Dict[str, Any]] = []
        for item in items:
            normalized = self._normalize_search_result(item)
            if normalized:
                results.append(normalized)
        return results

    def get_video_details(
        self,
        video_ids: Sequence[str] | str,
        part: str = "snippet,statistics,contentDetails",
    ) -> List[Dict[str, Any]]:
        """Fetch detailed metadata for one or more YouTube video IDs."""
        if isinstance(video_ids, str):
            ids = [video_ids]
        else:
            ids = [str(video_id) for video_id in video_ids if str(video_id).strip()]

        if not ids:
            return []

        response = self.service.videos().list(part=part, id=",".join(ids)).execute()
        items = response.get("items", [])

        results: List[Dict[str, Any]] = []
        for item in items:
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            details = item.get("contentDetails", {})
            video_id = item.get("id")
            if not video_id:
                continue

            results.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "channel": snippet.get("channelTitle"),
                    "channel_id": snippet.get("channelId"),
                    "description": snippet.get("description"),
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
                    "duration": details.get("duration"),
                    "view_count": stats.get("viewCount"),
                    "like_count": stats.get("likeCount"),
                    "comment_count": stats.get("commentCount"),
                    "watch_url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )
        return results

    def search_channels(
        self,
        query: str,
        max_results: int = 5,
        region_code: str = "US",
    ) -> List[Dict[str, Any]]:
        """Search for channels when the agent needs broader discovery."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        response = (
            self.service.search()
            .list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=max_results,
                regionCode=region_code,
            )
            .execute()
        )

        results: List[Dict[str, Any]] = []
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            channel_id = item.get("id", {}).get("channelId")
            if not channel_id:
                continue

            results.append(
                {
                    "channel_id": channel_id,
                    "channel_name": snippet.get("title"),
                    "description": snippet.get("description"),
                    "thumbnail_url": (
                        snippet.get("thumbnails", {})
                        .get("high", {})
                        .get("url")
                        or snippet.get("thumbnails", {})
                        .get("medium", {})
                        .get("url")
                    ),
                    "channel_url": f"https://www.youtube.com/channel/{channel_id}",
                }
            )
        return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Search and inspect YouTube videos")
    parser.add_argument("query", help="Search query to run against YouTube")
    parser.add_argument("--max-results", type=int, default=5, help="Number of results to return")
    parser.add_argument("--region-code", default="US", help="Region code for results")
    parser.add_argument("--order", default="relevance", help="YouTube result ordering")
    parser.add_argument("--safe-search", default="moderate", help="YouTube safe search level")
    parser.add_argument("--video-duration", default=None, help="Filter: any, short, medium, long")
    parser.add_argument("--include-details", action="store_true", help="Fetch full metadata for each returned video")
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

    if args.include_details:
        video_ids = [result["video_id"] for result in results]
        detail_map = {
            item["video_id"]: item
            for item in skill.get_video_details(video_ids)
        }
        for result in results:
            result["details"] = detail_map.get(result["video_id"], {})

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

