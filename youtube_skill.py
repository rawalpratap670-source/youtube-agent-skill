import argparse
import json
import os
from typing import Any, Dict, List, Optional, Sequence, Union

from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import NoTranscriptFound, VideoUnavailable, YouTubeTranscriptApi


load_dotenv()


class YouTubeSkill:
    """Agent-friendly YouTube client for discovery, metadata, and transcripts."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "YOUTUBE_API_KEY is missing. Set it in your environment or .env file."
            )
        self.service = build("youtube", "v3", developerKey=self.api_key)

    @staticmethod
    def _thumbnail_url(snippet: Dict[str, Any]) -> Optional[str]:
        thumbnails = snippet.get("thumbnails", {})
        return (
            thumbnails.get("high", {}).get("url")
            or thumbnails.get("medium", {}).get("url")
            or thumbnails.get("default", {}).get("url")
        )

    @staticmethod
    def _normalize_item_id(item: Dict[str, Any], key: str) -> Optional[str]:
        node = item.get("id", {})
        return node.get(key)

    def _normalize_video_result(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        snippet = item.get("snippet", {})
        video_id = self._normalize_item_id(item, "videoId")
        if not video_id:
            return None

        return {
            "video_id": video_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "published_at": snippet.get("publishedAt"),
            "thumbnail_url": self._thumbnail_url(snippet),
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
        """Return normalized video metadata for a search query."""
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
            normalized = self._normalize_video_result(item)
            if normalized:
                results.append(normalized)
        return results

    def get_video_details(
        self,
        video_ids: Union[str, Sequence[str]],
        part: str = "snippet,statistics,contentDetails",
    ) -> List[Dict[str, Any]]:
        """Fetch richer metadata for one or more videos."""
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
                    "thumbnail_url": self._thumbnail_url(snippet),
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
        """Search for YouTube channels."""
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
            channel_id = self._normalize_item_id(item, "channelId")
            if not channel_id:
                continue

            results.append(
                {
                    "channel_id": channel_id,
                    "channel_name": snippet.get("title"),
                    "description": snippet.get("description"),
                    "thumbnail_url": self._thumbnail_url(snippet),
                    "channel_url": f"https://www.youtube.com/channel/{channel_id}",
                }
            )
        return results

    def search_playlists(
        self,
        query: str,
        max_results: int = 5,
        region_code: str = "US",
    ) -> List[Dict[str, Any]]:
        """Search YouTube playlists."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        response = (
            self.service.search()
            .list(
                part="snippet",
                q=query,
                type="playlist",
                maxResults=max_results,
                regionCode=region_code,
            )
            .execute()
        )

        results: List[Dict[str, Any]] = []
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            playlist_id = self._normalize_item_id(item, "playlistId")
            if not playlist_id:
                continue

            results.append(
                {
                    "playlist_id": playlist_id,
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "channel": snippet.get("channelTitle"),
                    "thumbnail_url": self._thumbnail_url(snippet),
                    "playlist_url": f"https://www.youtube.com/playlist?list={playlist_id}",
                }
            )
        return results

    def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Return the videos inside a playlist."""
        if not playlist_id or not playlist_id.strip():
            raise ValueError("playlist_id cannot be empty.")

        response = (
            self.service.playlistItems()
            .list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=max_results,
            )
            .execute()
        )

        results: List[Dict[str, Any]] = []
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            video_id = content.get("videoId")
            if not video_id:
                continue

            results.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "channel": snippet.get("channelTitle"),
                    "published_at": snippet.get("publishedAt"),
                    "thumbnail_url": self._thumbnail_url(snippet),
                    "watch_url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )
        return results

    def get_video_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """Retrieve transcript text when available."""
        if not video_id or not video_id.strip():
            raise ValueError("video_id cannot be empty.")

        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=languages or ["en", "en-US"],
            )
            return [
                {
                    "text": entry.get("text", ""),
                    "start": str(entry.get("start", 0)),
                    "duration": str(entry.get("duration", 0)),
                }
                for entry in transcript
            ]
        except (NoTranscriptFound, VideoUnavailable):
            return []

    def search(
        self,
        query: str,
        max_results: int = 5,
        include_details: bool = False,
        include_transcript: bool = False,
    ) -> Dict[str, Any]:
        """Convenience method returning a single structured agent payload."""
        results = self.search_videos(query=query, max_results=max_results)

        if include_details and results:
            video_ids = [item["video_id"] for item in results]
            detail_map = {item["video_id"]: item for item in self.get_video_details(video_ids)}
            for result in results:
                result["details"] = detail_map.get(result["video_id"], {})

        if include_transcript and results:
            first_result = results[0]
            first_result["transcript"] = self.get_video_transcript(first_result["video_id"])

        return {
            "query": query,
            "total_results": len(results),
            "results": results,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Search and inspect YouTube videos")
    parser.add_argument("query", help="Search query to run against YouTube")
    parser.add_argument("--max-results", type=int, default=5, help="Number of results to return")
    parser.add_argument("--region-code", default="US", help="Region code for results")
    parser.add_argument("--order", default="relevance", help="YouTube result ordering")
    parser.add_argument("--safe-search", default="moderate", help="YouTube safe search level")
    parser.add_argument("--video-duration", default=None, help="Filter: any, short, medium, long")
    parser.add_argument("--include-details", action="store_true", help="Fetch metadata for each video")
    parser.add_argument("--include-transcript", action="store_true", help="Fetch transcript for the first result")
    args = parser.parse_args()

    skill = YouTubeSkill()
    payload = skill.search(
        query=args.query,
        max_results=args.max_results,
        include_details=args.include_details,
        include_transcript=args.include_transcript,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
