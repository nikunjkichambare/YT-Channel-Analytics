# src/config/settings.py
import os
import streamlit as st
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    yt_api_key: str = st.secrets.get("YT_API_KEY", os.getenv("YT_API_KEY", ""))
    base_url: str = "https://www.googleapis.com/youtube/v3"
    timeout_s: int = 30
    batch_size: int = 50

settings = Settings()

# Optional: fail fast if absent in prod
if not settings.yt_api_key:
    raise RuntimeError("Missing YT_API_KEY. Set it in Streamlit Secrets or .env.")
