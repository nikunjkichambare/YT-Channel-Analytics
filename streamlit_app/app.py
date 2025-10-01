# streamlit_app/app.py
# 1) Ensure Python can import the 'src' package by adding the PROJECT ROOT to sys.path
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # project root
SRC = os.path.join(ROOT, "src")  # sanity check path
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Optional diagnostics; safe to remove once imports work
import pkgutil
print("ROOT in sys.path:", ROOT in sys.path, ROOT)
print("SRC exists:", os.path.isdir(SRC), SRC)
print("FINDER src:", pkgutil.find_loader("src"))
print("FINDER src.services:", pkgutil.find_loader("src.services"))

# 2) App imports (now that sys.path includes the project root)
import streamlit as st
from src.services.videos import fetch_channel_df

# 3) UI
st.set_page_config(page_title="YouTube Channel Video Analytics", layout="wide")
st.title("YouTube Channel Video Analytics")

default_handle = "@CoComelon"
handle = st.text_input("Enter channel handle (e.g., @CoComelon):", value=default_handle)

if st.button("Fetch Videos"):
    with st.spinner("Fetching..."):
        try:
            df = fetch_channel_df(handle.strip())
            if df.empty:
                st.warning("No videos found or failed to fetch.")
            else:
                df = df.sort_values("published_at", ascending=False).reset_index(drop=True)
                st.success(f"Fetched {len(df)} videos.")
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    label="Download CSV",
                    data=df.to_csv(index=False),
                    file_name=f"{handle.strip('@')}_videos.csv",
                    mime="text/csv",
                )
        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)
