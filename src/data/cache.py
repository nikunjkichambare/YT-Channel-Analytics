import json
import os
import time
from typing import Any, Optional

DEFAULT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "cache")
DEFAULT_TTL_SECONDS = 3600  # 1 hour

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _safe_key(key: str) -> str:
    # Make a filesystem-safe file name from a cache key (e.g., '@CoComelon')
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)

def _cache_path(cache_dir: str, key: str) -> str:
    fname = f"{_safe_key(key)}.json"
    return os.path.join(cache_dir, fname)

def get_cache(
    key: str,
    cache_dir: str = DEFAULT_DIR,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> Optional[Any]:
    """
    Return cached JSON if present and not expired, else None.
    { "saved_at": epoch_seconds, "payload": <any JSON-serializable> }
    """
    path = _cache_path(cache_dir, key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            blob = json.load(f)
        saved_at = blob.get("saved_at", 0)
        if time.time() - saved_at > ttl_seconds:
            return None
        return blob.get("payload", None)
    except Exception:
        return None

def set_cache(
    key: str,
    payload: Any,
    cache_dir: str = DEFAULT_DIR,
) -> None:
    _ensure_dir(cache_dir)
    path = _cache_path(cache_dir, key)
    blob = {"saved_at": int(time.time()), "payload": payload}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(blob, f, ensure_ascii=False)

def clear_cache(key: str, cache_dir: str = DEFAULT_DIR) -> None:
    path = _cache_path(cache_dir, key)
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass

def clear_all(cache_dir: str = DEFAULT_DIR) -> None:
    if not os.path.isdir(cache_dir):
        return
    for name in os.listdir(cache_dir):
        if name.endswith(".json"):
            try:
                os.remove(os.path.join(cache_dir, name))
            except OSError:
                pass
