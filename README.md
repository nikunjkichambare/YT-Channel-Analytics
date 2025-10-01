YouTube Channel Videos Viewer


Fetch all public videos from a YouTube channel handle and export a CSV with enriched metadata (title, published date, views, likes, comments, duration, tags, etc.). Built with Streamlit and the YouTube Data API v3.

Features
Handle input like “@CoComelon” with one‑click fetch.

Efficient pagination and batching of API calls.

CSV download of the full uploads list with rich fields.

Simple on-disk JSON cache (TTL) to reduce API quota.

Clean src/ package layout with tests.

Project structure
text
.
├─ src/
│  ├─ __init__.py
│  ├─ config/
│  │  ├─ __init__.py
│  │  └─ settings.py
│  ├─ youtube_api/
│  │  ├─ __init__.py
│  │  ├─ client.py
│  │  ├─ models.py
│  │  └─ parsers.py
│  ├─ data/
│  │  ├─ __init__.py
│  │  ├─ io.py
│  │  └─ cache.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ videos.py
│  └─ cli/
│     ├─ __init__.py
│     └─ main.py
├─ streamlit_app/
│  └─ app.py
├─ requirements.txt
├─ .env.example
└─ .gitignore
Prerequisites
Python 3.11+.

YouTube Data API v3 API key (enabled in Google Cloud).

Internet access for API requests.

Setup
Create and activate a virtual environment, then install dependencies:

text
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Create .env at the project root (use .env.example as a template):

text
YT_API_KEY=YOUR_REAL_YOUTUBE_API_KEY
Ensure package markers exist:

src/init.py

src/services/init.py

src/youtube_api/init.py

src/data/init.py

Run the app
From the project root:

text
# Windows PowerShell
.venv\Scripts\Activate.ps1
streamlit run streamlit_app\app.py

# macOS/Linux
source .venv/bin/activate
streamlit run streamlit_app/app.py
Open the Local URL (typically http://localhost:8501). Enter a handle (e.g., @CoComelon) and click “Fetch Videos.” Preview the table and download the CSV.

Data fields
snippet: title, publishedAt, categoryId, tags, channelTitle, description.

statistics: viewCount, likeCount, commentCount.

contentDetails: duration (ISO 8601), definition, caption.
Notes:

Tags are joined with “;” in the CSV.

Duration is kept in ISO 8601 (e.g., PT3M5S).

Caching
File-backed JSON cache under cache/ with a default TTL of 1 hour.

Keyed by channel handle to reduce repeated API calls.

CLI usage (optional)
Fetch to CSV via CLI:

text
# after activating the venv
python -m src.cli.main --handle "@CoComelon" --out "videos.csv"
Testing
Run unit tests:

text
pip install pytest
pytest -q
Coverage includes:

Channel handle resolution to channelId and uploads playlist.

Playlist pagination for video IDs.

Batching in videos.list (up to 50 IDs per call).

Service orchestration and cache usage.

Troubleshooting
“ModuleNotFoundError: No module named 'src'”
Ensure streamlit_app/app.py adds the project root to sys.path at the very top:

text
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
Confirm src/ and streamlit_app/ are siblings.

Verify all init.py files exist as listed.

Delete pycache folders and .pyc files, then restart from a fresh terminal.

Always run from the project root with the venv active.

API errors (quotaExceeded, keyInvalid)
Confirm the API key value in .env and that YouTube Data API v3 is enabled for that key.

Quota resets daily at midnight PT; bulk fetches may hit limits.

Blank page or hot‑reload issues
Ensure dependencies are installed in the active venv.

Restart the Streamlit process to clear stale state.

Review terminal logs for exceptions.

Configuration notes
python-dotenv loads .env at startup; do not commit real secrets.

.env is ignored via .gitignore.

Optionally set PYTHONPATH to the project root in the IDE for convenience.

License
Add a license (e.g., MIT) if publishing.

Acknowledgments
Streamlit, YouTube Data API v3.