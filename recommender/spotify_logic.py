import re
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_playlist_features(playlist_url):
    pattern = r'https?://open\.spotify\.com/playlist/([a-zA-Z0-9]+)'
    match = re.match(pattern, playlist_url)
    if not match:
        logging.error(f"Invalid Spotify playlist URL format: {playlist_url}")
        return None
    playlist_id = match.group(1)

    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv('SPOTIPY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        results = sp.playlist_tracks(playlist_id)
        if not results or 'items' not in results:
            logging.error(f"Could not retrieve tracks for playlist ID: {playlist_id}")
            return None

        tracks = []
        track_items = results['items']

        while results['next']:
            results = sp.next(results)
            track_items.extend(results['items'])

        for item in track_items:
            track_data = item.get('track')
            if not track_data or not track_data.get('id') or not track_data.get('name'):
                continue
            artist_names = [
                artist.get('name')
                for artist in track_data.get('artists', [])
                if artist.get('name') \
            ]
            tracks.append({
                'id': track_data['id'],
                'name': track_data['name'],
                'artist': ', '.join(artist_names) if artist_names else "Unknown Artist",
            })

        logging.info(f"Successfully fetched {len(tracks)} tracks from playlist {playlist_id}")
        return tracks

    except spotipy.exceptions.SpotifyException as e:
        logging.error(f"Spotify API error for playlist {playlist_id}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None