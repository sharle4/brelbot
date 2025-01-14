import requests
import lyricsgenius
import re
import time
import logging


def _get(path, params=None, headers=None):
    """Send a GET request to the Genius API and return the response in JSON format."""
    requrl = '/'.join([BASE_URL, path])
    token = f"Bearer {CLIENT_ACCESS_TOKEN}"
    headers = headers or {}
    headers['Authorization'] = token

    try:
        response = requests.get(url=requrl, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


def get_artist_songs(artist_id):
    """Retrieve the most popular songs of the artist by their ID."""
    top_song_ids = []
    page = 1

    while len(top_song_ids) < MAX_SONGS:
        path = f"artists/{artist_id}/songs"
        params = {'per_page': 20, 'sort': 'popularity', 'page': page}
        data = _get(path=path, params=params)

        if not data or 'songs' not in data['response'] or not data['response']['songs']:
            break

        song_ids = [song['id'] for song in data['response']['songs'] if ARTIST_NAME in song['artist_names']]
        top_song_ids.extend(song_ids)
        page += 1

    return top_song_ids[:MAX_SONGS]


def get_lyrics(song_id):
    """Retrieve the lyrics of a song by its ID."""
    time.sleep(1)
    try:
        return genius.lyrics(song_id)
    except Exception as e:
        logging.error(f"Failed to get lyrics for song ID {song_id}: {e}")
        return None


def save_lyrics(song_id, lyrics):
    """Save the lyrics of a song to a text file."""
    try:
        title = _get(f"songs/{song_id}")["response"]["song"]["title"]
        title = re.sub(r'[\\/:"*?<>|]', '', title)
        with open(f"{FOLDER}{title}.txt", "w", encoding="utf-8") as f:
            f.write(lyrics)
    except Exception as e:
        logging.error(f"Failed to save lyrics for song ID {song_id}: {e}")


def main():
    logging.info(f"Searching for {ARTIST_NAME}'s artist ID.")
    find_id = _get("search", {'q': ARTIST_NAME})
    artist_id = None

    for hit in find_id["response"]["hits"]:
        if hit["result"]["primary_artist"]["name"] == ARTIST_NAME:
            artist_id = hit["result"]["primary_artist"]["id"]
            break

    if not artist_id:
        logging.error(f"Artist ID for {ARTIST_NAME} not found.")
        return

    logging.info(f"-> {ARTIST_NAME}'s ID is {artist_id}")
    logging.info("Retrieving song IDs.")
    song_ids = get_artist_songs(artist_id)
    logging.info(f"-> Retrieved {len(song_ids)} song IDs.")

    logging.info("Retrieving lyrics for each song.")
    for song_id in song_ids:
        logging.info(f"Processing song ID {song_id}")
        lyrics = get_lyrics(song_id)
        
        if lyrics:
            lines = lyrics.split('\n', 1)
            lyrics = re.sub(r'\[.*?\]', '', lines[1])
            lyrics = re.sub(r'\(.*?\)', '', lyrics) 
            lyrics = re.sub(r'\n\s*\n', '\n', lyrics)
            lyrics = lyrics.lstrip('\n')
            save_lyrics(song_id, lyrics)

    logging.info("-> Finished! Check the lyrics folder.")


if __name__ == "__main__":
    with open('genius_api_key.txt', 'r') as file:
        CLIENT_ACCESS_TOKEN = file.readline().strip()

    genius = lyricsgenius.Genius(CLIENT_ACCESS_TOKEN)
    BASE_URL = "https://api.genius.com"
    ARTIST_NAME = "Jacques Brel"
    FOLDER = "lyrics/"
    MAX_SONGS = 1001

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    main()