import argparse
from src.services.videos import fetch_channel_df
from src.data.io import save_csv

def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube channel videos to CSV")
    parser.add_argument("--handle", required=True, help="Channel handle, e.g., @CoComelon")
    parser.add_argument("--out", default="videos.csv", help="Output CSV path")
    args = parser.parse_args()

    df = fetch_channel_df(args.handle)
    if df.empty:
        print("No videos found or failed to fetch.")
        return
    df = df.sort_values("published_at", ascending=False).reset_index(drop=True)
    save_csv(df, args.out)
    print(f"Wrote {len(df)} rows to {args.out}")

if __name__ == "__main__":
    main()
