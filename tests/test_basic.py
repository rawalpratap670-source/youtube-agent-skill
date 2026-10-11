import pytest


def test_import_smoke():
    from youtube_skill import YouTubeSkill
    assert YouTubeSkill is not None


def test_package_main_import():
    import youtube_skill.__main__
    assert youtube_skill.__main__ is not None
