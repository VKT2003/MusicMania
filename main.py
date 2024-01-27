from flask import Flask, render_template, request
from pytube import YouTube
import requests

app = Flask(__name__)

API_KEY = "AIzaSyDlTbNGswTDCDjn4tcLynjHPjPtYBj2Q7g"

# Default song names to query initially
DEFAULT_SONG_NAMES = ["as it was", "blinding lights", "main balak tu mata", "tum hi aana", "tum hi ho"]
DEFAULT_SONGS = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global DEFAULT_SONGS

    if not DEFAULT_SONGS:
        # Fetch default songs initially based on song names
        DEFAULT_SONGS = get_youtube_videos(DEFAULT_SONG_NAMES)

    if request.method == 'POST':
        # Handle POST request (search query submitted)
        search_query = request.form.get('search_query')

        if search_query:
            videos = get_youtube_videos([search_query])
            return render_template('index.html', videos=videos)

    # Handle GET request or when no search query is provided
    return render_template('index.html', videos=DEFAULT_SONGS)

@app.route('/play', methods=['GET', 'POST'])
def play():
    if request.method == 'POST':
        # Handle POST request (search query submitted)
        search_query = request.form.get('search_query')

        if search_query:
            videos = get_youtube_videos([search_query])
            return render_template('index.html', videos=videos)

    # Handle GET request or when no search query is provided
    return render_template('index.html', videos=DEFAULT_SONGS)

# ...

def get_youtube_videos(song_names):
    videos = []

    for song_name in song_names:
        try:
            # Fetch videos based on song name using YouTube Data API
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={song_name}&key={API_KEY}"
            response = requests.get(url)
            data = response.json()

            # Process the data
            if 'items' in data:
                for item in data['items']:  # Iterate through all items
                    snippet = item.get('snippet', {})
                    title = snippet.get('title', f'No title available for {song_name}')
                    channel_title = snippet.get('channelTitle', 'Unknown channel')
                    video_id = item.get('id', {}).get('videoId', 'No video ID available')

                    # Fetch the download URL using pytube
                    play_url = f"https://www.youtube.com/watch?v={video_id}"
                    download_url = get_download_url(play_url)

                    # Fetch the thumbnail URL
                    thumbnail_url = snippet.get('thumbnails', {}).get('default', {}).get('url', 'No thumbnail available')

                    videos.append({
                        'title': title,
                        'channel_title': channel_title,
                        'video_id': video_id,
                        'play_url': play_url,
                        'download_url': download_url,
                        'thumbnail_url': thumbnail_url
                    })
        except Exception as e:
            print(f"Error processing data for {song_name}: {e}")

    return videos

# ...

def get_download_url(play_url):
    try:
        yt = YouTube(play_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        return audio_stream.url
    except Exception as e:
        print(f"Error downloading MP3 audio for {play_url}: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
