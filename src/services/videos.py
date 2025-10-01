import pandas as pd
from src.youtube_api.client import (
    get_channel_and_uploads,
    list_upload_video_ids,
    fetch_video_items,
)
from src.youtube_api.parsers import parse_video_items
from src.data.io import videos_to_df
from src.data.cache import get_cache, set_cache

CACHE_TTL_SECONDS = 3600  # 1 hour

def fetch_channel_df(handle: str) -> pd.DataFrame:
    # 0) try cache by handle
    cached = get_cache(handle, ttl_seconds=CACHE_TTL_SECONDS)
    if cached:
        return pd.DataFrame(cached)

    # 1) resolve channel handle and uploads playlist
    _, uploads = get_channel_and_uploads(handle)
    # 2) list all video IDs
    ids = list_upload_video_ids(uploads)
    if not ids:
        return pd.DataFrame(columns=[
            "video_id","title","published_at","view_count",
            "like_count","comment_count","duration","category_id",
            "tags","definition","caption","channel_title","description"
        ])
    # 3) fetch details in batches
    items = fetch_video_items(ids)
    videos = parse_video_items(items)
    df = videos_to_df(videos)

    # 4) save to cache (as list of dicts)
    set_cache(handle, df.to_dict(orient="records"))
    return df
