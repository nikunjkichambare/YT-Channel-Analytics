import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load variables from .env at project root
load_dotenv()

@dataclass(frozen=True)
class Settings:
    yt_api_key: str = os.getenv("YT_API_KEY", "")
    base_url: str = "https://www.googleapis.com/youtube/v3"

    # network and paging
    timeout_s: int = 30
    batch_size: int = 50  # YouTube supports up to 50 ids per videos.list call

settings = Settings()
