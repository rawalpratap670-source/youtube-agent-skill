from youtube_skill import YouTubeSkill


def test_search_videos_normalizes_fields():
    class FakeSearch:
        def list(self, **kwargs):
            class FakeRequest:
                def execute(self):
                    return {
                        "items": [
                            {
                                "id": {"videoId": "abc123"},
                                "snippet": {
                                    "title": "Python tutorial",
                                    "description": "Learn Python",
                                    "channelTitle": "Code Academy",
                                    "channelId": "channel_123",
                                    "publishedAt": "2024-01-01T00:00:00Z",
                                    "thumbnails": {
                                        "high": {"url": "https://example.com/high.jpg"},
                                    },
                                },
                            }
                        ]
                    }

            return FakeRequest()

    skill = YouTubeSkill.__new__(YouTubeSkill)
    skill.api_key = "test-key"
    skill.service = type("FakeService", (), {"search": lambda self: FakeSearch()})()

    results = skill.search_videos("python tutorial", max_results=1)
    assert len(results) == 1
    assert results[0]["video_id"] == "abc123"
    assert results[0]["title"] == "Python tutorial"
    assert results[0]["channel"] == "Code Academy"
    assert results[0]["watch_url"] == "https://www.youtube.com/watch?v=abc123"
