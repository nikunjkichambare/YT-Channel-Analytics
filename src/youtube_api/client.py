import requests
from typing import Dict, List, Tuple
from src.config.settings import settings

def _get(path: str, params: Dict) -> Dict:
    url = f"{settings.base_url}/{path}"
    r = requests.get(url, params=params, timeout=settings.timeout_s)
    r.raise_for_status()
    return r.json()

def get_channel_and_uploads(handle: str) -> Tuple[str, str]:
    """
    Resolve channel handle to channelId and uploads playlistId using channels.list.
    parts: id, contentDetails
    """
    data = _get("channels", {
        "part": "id,contentDetails",
        "forHandle": handle,
        "key": settings.yt_api_key
    })
    items = data.get("items", [])
    if not items:
        raise ValueError(f"Channel not found for handle: {handle}")
    item = items[0]
    uploads = item["contentDetails"]["relatedPlaylists"]["uploads"]
    return item["id"], uploads

def list_upload_video_ids(uploads_playlist_id: str) -> List[str]:
    """
    Enumerate all video IDs from uploads playlist via playlistItems.list with pagination.
    """
    video_ids: List[str] = []
    params = {
        "part": "contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": 50,
        "key": settings.yt_api_key
    }
    while True:
        data = _get("playlistItems", params)
        for it in data.get("items", []):
            video_ids.append(it["contentDetails"]["videoId"])
        token = data.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token
    return video_ids

def _chunks(xs: List[str], n: int) -> List[List[str]]:
    return [xs[i:i+n] for i in range(0, len(xs), n)]

def fetch_video_items(video_ids: List[str]) -> List[Dict]:
    """
    Retrieve snippet, statistics, and contentDetails for up to 50 IDs per request via videos.list.
    """
    out: List[Dict] = []
    for chunk in _chunks(video_ids, settings.batch_size):
        data = _get("videos", {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(chunk),
            "key": settings.yt_api_key
        })
        out.extend(data.get("items", []))
    return out
