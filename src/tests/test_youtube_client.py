import json
from unittest.mock import patch, Mock, ANY
import pytest

from src.youtube_api.client import (
    get_channel_and_uploads,
    list_upload_video_ids,
    fetch_video_items,
)
from src.config.settings import settings

# Helpers to build fake responses
def _mock_response(json_body, status=200):
    m = Mock()
    m.status_code = status
    m.json.return_value = json_body
    # requests.get(...).raise_for_status() should be a no-op for 2xx
    if status >= 400:
        def _raise():
            from requests import HTTPError
            raise HTTPError(f"HTTP {status}")
        m.raise_for_status.side_effect = _raise
    return m

def test_get_channel_and_uploads_for_handle_success():
    fake = {
        "items": [
            {
                "id": "UC_demo_channel",
                "contentDetails": {
                    "relatedPlaylists": {"uploads": "UU_demo_uploads"}
                },
            }
        ]
    }
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(fake, 200)
        channel_id, uploads = get_channel_and_uploads("@DemoHandle")

        # Assert parsed values
        assert channel_id == "UC_demo_channel"
        assert uploads == "UU_demo_uploads"

        # Validate URL and params used
        called_url = mock_get.call_args.kwargs["url"]
        called_params = mock_get.call_args.kwargs["params"]
        assert called_url == f"{settings.base_url}/channels"
        # Must include forHandle and parts
        assert called_params["forHandle"] == "@DemoHandle"
        assert "contentDetails" in called_params["part"]
        assert called_params["key"] == settings.yt_api_key

def test_get_channel_and_uploads_no_items_raises():
    fake = {"items": []}
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(fake, 200)
        with pytest.raises(ValueError):
            get_channel_and_uploads("@MissingHandle")

def test_list_upload_video_ids_paginates():
    # First page with nextPageToken
    page1 = {
        "items": [
            {"contentDetails": {"videoId": "v1"}},
            {"contentDetails": {"videoId": "v2"}},
        ],
        "nextPageToken": "TOKEN_2",
    }
    # Second page final
    page2 = {
        "items": [
            {"contentDetails": {"videoId": "v3"}},
        ]
    }

    def side_effect(url, params, timeout):
        # Simulate two sequential GETs with and without pageToken
        if "pageToken" not in params:
            return _mock_response(page1, 200)
        else:
            assert params["pageToken"] == "TOKEN_2"
            return _mock_response(page2, 200)

    with patch("requests.get", side_effect=side_effect) as mock_get:
        ids = list_upload_video_ids("UU_demo_uploads")
        assert ids == ["v1", "v2", "v3"]

        # Verify base URL and params for first call
        first_call_params = mock_get.call_args_list[0].kwargs["params"]
        assert first_call_params["playlistId"] == "UU_demo_uploads"
        assert first_call_params["part"] == "contentDetails"
        assert first_call_params["maxResults"] == 50
        assert first_call_params["key"] == settings.yt_api_key

def test_fetch_video_items_batches_50_ids():
    # Build 120 IDs to force 3 batches: 50 + 50 + 20
    ids = [f"vid{i}" for i in range(120)]

    # Respond with items reflecting the requested ids in each batch
    def side_effect(url, params, timeout):
        id_param = params["id"]
        batch_ids = id_param.split(",")
        items = []
        for vid in batch_ids:
            items.append({
                "id": vid,
                "snippet": {
                    "title": f"title_{vid}",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "categoryId": "10",
                    "channelTitle": "Demo Channel",
                    "description": f"desc_{vid}",
                },
                "statistics": {
                    "viewCount": "123",
                    "likeCount": "4",
                    "commentCount": "1",
                },
                "contentDetails": {
                    "duration": "PT2M10S",
                    "definition": "hd",
                    "caption": "false",
                },
            })
        return _mock_response({"items": items}, 200)

    with patch("requests.get", side_effect=side_effect) as mock_get:
        items = fetch_video_items(ids)
        # Ensure the same number of items returned as requested
        assert len(items) == len(ids)
        # Ensure requests were made in 3 batches
        assert len(mock_get.call_args_list) == 3

        # Validate first call params
        first_params = mock_get.call_args_list[0].kwargs["params"]
        assert first_params["part"] == "snippet,statistics,contentDetails"
        assert first_params["key"] == settings.yt_api_key
        first_batch_ids = first_params["id"].split(",")
        assert len(first_batch_ids) == 50
        assert first_batch_ids[0] == "vid0"

        # Validate last batch size
        last_params = mock_get.call_args_list[-1].kwargs["params"]
        last_batch_ids = last_params["id"].split(",")
        assert len(last_batch_ids) == 20
        assert last_batch_ids[-1] == "vid119"
