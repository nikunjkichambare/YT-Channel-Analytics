from typing import Dict, List, Optional
from .models import Video

def _to_int(x: Optional[str]) -> Optional[int]:
    try:
        return int(x) if x is not None else None
    except Exception:
        return None

def parse_video_items(items: List[Dict]) -> List[Video]:
    rows: List[Video] = []
    for it in items:
        snip = it.get("snippet", {}) or {}
        stats = it.get("statistics", {}) or {}
        cdet = it.get("contentDetails", {}) or {}

        rows.append(
            Video(
                video_id=it.get("id", ""),
                title=snip.get("title", ""),
                published_at=snip.get("publishedAt", ""),
                view_count=_to_int(stats.get("viewCount")) or 0,
                like_count=_to_int(stats.get("likeCount")),
                comment_count=_to_int(stats.get("commentCount")),
                duration=cdet.get("duration"),
                category_id=snip.get("categoryId"),
                tags=snip.get("tags"),
                definition=cdet.get("definition"),
                caption=cdet.get("caption"),
                channel_title=snip.get("channelTitle"),
                description=snip.get("description"),
            )
        )
    return rows
