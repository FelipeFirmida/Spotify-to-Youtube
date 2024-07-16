import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

from flask import Flask, request, url_for, session, redirect

import clientinfo # File containing all the info necessary to login the web APP to the Spotify API

""" requirements [
    Flask,
    Spotipy,
    OS,
    time,
    clientinfo
]"""

app = Flask(__name__)

app.secret_key = os.environ['FLASK_S_KEY']
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

TOKEN_INFO = "token_info"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.environ['SPOTIFY_CLIENT_ID'],
        client_secret = os.environ['SPOTIFY_CLIENT_SECRET'],
        redirect_uri = url_for('redirectSite', _external=True),
        scope = "user-library-read"
    )

def get_token():
    token_info = session.get(TOKEN_INFO)
    if not token_info:
        raise Exception("Token not found in session")
    
    sp_oauth = create_spotify_oauth()

    if sp_oauth.is_token_expired(token_info):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    
    return token_info

# Endpoint Index
@app.route('/')
def index():
    return "Spotify to Youtube Webpage!"

# Log in user to the web app using OAuth
@app.route("/login")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# After login, redirect user to the page with the correct authorization token
@app.route("/redirect")
def redirectSite():
    sp_oauth = create_spotify_oauth()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("getTracks", _external=True))

@app.route('/getTracks')
def getTracks():
    try: 
        token_info = get_token()
    except Exception as e:
        print(f"Exception: {e}")
        return redirect(url_for("login", _external=True))
        

    sp = spotipy.Spotify(auth = token_info['access_token'])
    all_songs = []
    i = 0
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset= i * 50)['items']
        i += 1
        all_songs += items
        if (len(items) < 50):
            break

    return str(all_songs)
# Checks if the token exists and if its available. If not, it refreshes to get another token.


