import requests
import csv
import sys

API_KEY = "YOUR API KEY"
CHANNEL_ID = "YT CHANNEL ID"
OUTPUT_FILE = "OUTPUT FILE NAME"
MAX_VIDEOS = 100

def get_latest_videos(channel_id, api_key, max_results=100):
    videos = []
    next_page_token = None
    base_url = "https://www.googleapis.com/youtube/v3/search"

    while len(videos) < max_results:
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "type": "video",
            "maxResults": min(50, max_results - len(videos)),
        }
        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(base_url, params=params)
        data = response.json()

        if "error" in data:
            print(f"API Error: {data['error']['message']}")
            sys.exit(1)

        items = data.get("items", [])
        for item in items:
            videos.append({
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"][:10],  
            })

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return videos

def get_view_counts(video_ids, api_key):
    view_counts = {}
    base_url = "https://www.googleapis.com/youtube/v3/videos"

    
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        params = {
            "key": api_key,
            "id": ",".join(batch),
            "part": "statistics",
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if "error" in data:
            print(f"API Error: {data['error']['message']}")
            sys.exit(1)

        for item in data.get("items", []):
            vid_id = item["id"]
            views = item["statistics"].get("viewCount", "N/A")
            view_counts[vid_id] = views

    return view_counts

def main():
    print(f"Fetching latest {MAX_VIDEOS} videos from channel {CHANNEL_ID}...")
    videos = get_latest_videos(CHANNEL_ID, API_KEY, MAX_VIDEOS)
    print(f"Found {len(videos)} videos. Fetching view counts...")

    video_ids = [v["video_id"] for v in videos]
    view_counts = get_view_counts(video_ids, API_KEY)

    print(f"Writing results to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Title", "Views", "Published Date", "URL"])
        for v in videos:
            vid_id = v["video_id"]
            writer.writerow([
                v["title"],
                view_counts.get(vid_id, "N/A"),
                v["published_at"],
                f"https://www.youtube.com/watch?v={vid_id}",
            ])

    print(f"Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
