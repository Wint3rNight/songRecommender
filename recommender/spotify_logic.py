import os
import re
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_playlist_features(playlist_url):

    