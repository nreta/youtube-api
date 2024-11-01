from flask import Flask, request, jsonify, render_template
import requests
import re

app = Flask(__name__)

YOUTUBE_API_KEY = "AIzaSyAw_8W5Kk-vhFAm4z7cGvgxqUTJfPLXIJs"

def get_playlist_id(playlist_url):
    """Extracts the playlist ID from a YouTube playlist URL."""
    match = re.search(r"list=([^&]+)", playlist_url)
    return match.group(1) if match else None

def fetch_playlist_videos(playlist_id):
    """Fetches all videos in a playlist using pagination with the YouTube Data API."""
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    videos = []
    next_page_token = None

    while True:
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": YOUTUBE_API_KEY,
            "pageToken": next_page_token
        }
        
        response = requests.get(url, params=params)
        data = response.json()

        if "error" in data:
            print("Error in YouTube API response:", data["error"]["message"])
            return []

        for item in data.get("items", []):
            title = item["snippet"]["title"]
            video_id = item["snippet"]["resourceId"]["videoId"]
            thumbnails = item["snippet"]["thumbnails"]
            thumbnail_url = thumbnails.get("medium", thumbnails.get("default", {"url": "https://via.placeholder.com/320x180"}))["url"]

            video_data = {
                "title": title,
                "videoId": video_id,
                "thumbnail": thumbnail_url
            }
            videos.append(video_data)

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return videos

def search_videos(query):
    """Searches for videos on YouTube using the YouTube Data API."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 10,
        "key": YOUTUBE_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    if "error" in data:
        print("Error in YouTube API response:", data["error"]["message"])
        return []

    videos = []
    for item in data.get("items", []):
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        thumbnails = item["snippet"]["thumbnails"]
        thumbnail_url = thumbnails.get("medium", thumbnails.get("default", {"url": "https://via.placeholder.com/320x180"}))["url"]

        video_data = {
            "title": title,
            "videoId": video_id,
            "thumbnail": thumbnail_url
        }
        videos.append(video_data)

    return videos

@app.route('/api/get_playlist', methods=['POST'])
def get_playlist():
    data = request.get_json()
    playlist_url = data.get("playlist_url")
    
    playlist_id = get_playlist_id(playlist_url)
    if not playlist_id:
        return jsonify({"error": "Invalid playlist URL format"}), 400
    
    videos = fetch_playlist_videos(playlist_id)
    if not videos:
        return jsonify({"error": "Failed to fetch videos or empty playlist"}), 500

    return jsonify(videos), 200

@app.route('/api/search_video', methods=['POST'])
def search_video():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "No search query provided"}), 400

    videos = search_videos(query)
    return jsonify(videos), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
