from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Video:
    video_id: str
    title: str
    published_at: str
    view_count: int
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration: Optional[str] = None         # ISO 8601, e.g., PT2M13S
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    definition: Optional[str] = None       # hd/sd
    caption: Optional[str] = None          # true/false
    channel_title: Optional[str] = None
    description: Optional[str] = None
