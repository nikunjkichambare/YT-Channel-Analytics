import pandas as pd
from typing import List
from src.youtube_api.models import Video

def _row(v: Video) -> dict:
    d = v.__dict__.copy()
    if isinstance(d.get("tags"), list):
        d["tags"] = ";".join(d["tags"])
    return d

def videos_to_df(videos: List[Video]) -> pd.DataFrame:
    return pd.DataFrame([_row(v) for v in videos])

def save_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
