import pandas as pd
import pytest
from unittest.mock import patch
from pandas.testing import assert_frame_equal

# System under test
from src.services.videos import fetch_channel_df

# Sample fixtures representing minimal real API shapes after parsing
CHANNEL_HANDLE = "@CoComelon"
UPLOADS_PLAYLIST_ID = "UUxxxxUploads"

VIDEO_IDS = ["vid1", "vid2"]

VIDEO_ITEMS = [
    {
        "id": "vid1",
        "snippet": {
            "title": "Video One",
            "publishedAt": "2023-01-01T00:00:00Z",
            "categoryId": "10",
            "tags": ["kids", "song"],
            "channelTitle": "CoComelon - Nursery Rhymes",
            "description": "First video description",
        },
        "statistics": {
            "viewCount": "1000",
            "likeCount": "50",
            "commentCount": "5",
        },
        "contentDetails": {
            "duration": "PT2M10S",
            "definition": "hd",
            "caption": "false",
        },
    },
    {
        "id": "vid2",
        "snippet": {
            "title": "Video Two",
            "publishedAt": "2023-02-02T00:00:00Z",
            "categoryId": "10",
            "tags": ["nursery", "rhymes"],
            "channelTitle": "CoComelon - Nursery Rhymes",
            "description": "Second video description",
        },
        "statistics": {
            "viewCount": "2000",
            "likeCount": "70",
            "commentCount": "7",
        },
        "contentDetails": {
            "duration": "PT3M5S",
            "definition": "hd",
            "caption": "true",
        },
    },
]

def _expected_df() -> pd.DataFrame:
    # Matches the CSV-ready transformation (tags joined with ';')
    rows = [
        {
            "video_id": "vid1",
            "title": "Video One",
            "published_at": "2023-01-01T00:00:00Z",
            "view_count": 1000,
            "like_count": 50,
            "comment_count": 5,
            "duration": "PT2M10S",
            "category_id": "10",
            "tags": "kids;song",
            "definition": "hd",
            "caption": "false",
            "channel_title": "CoComelon - Nursery Rhymes",
            "description": "First video description",
        },
        {
            "video_id": "vid2",
            "title": "Video Two",
            "published_at": "2023-02-02T00:00:00Z",
            "view_count": 2000,
            "like_count": 70,
            "comment_count": 7,
            "duration": "PT3M5S",
            "category_id": "10",
            "tags": "nursery;rhymes",
            "definition": "hd",
            "caption": "true",
            "channel_title": "CoComelon - Nursery Rhymes",
            "description": "Second video description",
        },
    ]
    df = pd.DataFrame(rows)
    # Sort by published_at desc like the app usually does
    return df.sort_values("published_at", ascending=False).reset_index(drop=True)

@pytest.fixture
def patches():
    """
    Patch the low-level client functions and caching so tests run isolated from
    network and without relying on local cache files.
    """
    with patch("src.services.videos.get_channel_and_uploads") as p_get_chan, \
         patch("src.services.videos.list_upload_video_ids") as p_list_ids, \
         patch("src.services.videos.fetch_video_items") as p_fetch_items, \
         patch("src.services.videos.get_cache") as p_get_cache, \
         patch("src.services.videos.set_cache") as p_set_cache:

        # Disable cache hits for deterministic behavior
        p_get_cache.return_value = None

        # Mock channel resolve and uploads playlist
        p_get_chan.return_value = ("UCxxxxChannel", UPLOADS_PLAYLIST_ID)

        # Mock playlist enumeration
        p_list_ids.return_value = VIDEO_IDS

        # Mock videos.list items (raw API items before parsing)
        p_fetch_items.return_value = VIDEO_ITEMS

        yield {
            "get_channel_and_uploads": p_get_chan,
            "list_upload_video_ids": p_list_ids,
            "fetch_video_items": p_fetch_items,
            "get_cache": p_get_cache,
            "set_cache": p_set_cache,
        }

def test_fetch_channel_df_happy_path(patches):
    df = fetch_channel_df(CHANNEL_HANDLE)

    # Build expected DataFrame (after parsing + DataFrame conversion)
    exp = _expected_df()

    # Sort and reset index before compare to ignore ordering diff
    df_sorted = df.sort_values("published_at", ascending=False).reset_index(drop=True)

    # Ensure columns match and values equal
    assert list(df_sorted.columns) == list(exp.columns)
    assert_frame_equal(df_sorted[exp.columns], exp, check_dtype=False)

    # Ensure client functions were called as expected
    patches["get_channel_and_uploads"].assert_called_once_with(CHANNEL_HANDLE)
    patches["list_upload_video_ids"].assert_called_once_with(UPLOADS_PLAYLIST_ID)

    # fetch_video_items should be called with the list of IDs (batched internally by service)
    patches["fetch_video_items"].assert_called_once()
    args, _ = patches["fetch_video_items"].call_args
    assert args[0] == VIDEO_IDS  # first positional arg is the ids list

def test_fetch_channel_df_no_videos(patches):
    # Make playlist empty
    patches["list_upload_video_ids"].return_value = []

    df = fetch_channel_df(CHANNEL_HANDLE)
    # Expect empty DF with the defined columns from services.videos
    expected_cols = [
        "video_id","title","published_at","view_count",
        "like_count","comment_count","duration","category_id",
        "tags","definition","caption","channel_title","description"
    ]
    assert list(df.columns) == expected_cols
    assert df.empty

def test_fetch_channel_df_uses_cache_when_available(patches):
    # Make cache return a pre-built table and ensure network is bypassed
    cached_rows = _expected_df().to_dict(orient="records")
    patches["get_cache"].return_value = cached_rows

    df = fetch_channel_df(CHANNEL_HANDLE)
    assert not df.empty
    # Should not call network functions if cache hit
    patches["get_channel_and_uploads"].assert_not_called()
    patches["list_upload_video_ids"].assert_not_called()
    patches["fetch_video_items"].assert_not_called()
