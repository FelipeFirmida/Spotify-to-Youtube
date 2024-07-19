import spotipy
from spotipy.oauth2 import SpotifyOAuth

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import google.oauth2.credentials

import json
import os
import os.path

from flask import Flask, request, url_for, session, redirect, render_template
from flask_session import Session

import clientinfo # File containing all the info necessary to login the web APP to the Spotify and youtube APIs

""" requirements [
    Flask,
    Spotipy,
    OS,
    time,
    clientinfo
]"""

app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)

app.secret_key = os.environ['FLASK_S_KEY']

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

TOKEN_INFO = "token_info"

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.environ['SPOTIFY_CLIENT_ID'],
        client_secret = os.environ['SPOTIFY_CLIENT_SECRET'],
        redirect_uri = url_for('redirectSite', _external=True),
        scope = "user-read-private playlist-read-private playlist-read-collaborative",
        show_dialog=True
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

def credentialscheck():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    json_credentials = session.get('credentials')
    
    if 'credentials' in session:
        dict_credentials = json.loads(json_credentials)
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(dict_credentials)
        

        if credentials.expired:
            credentials.refresh(Request())

    else:
        return redirect(url_for('redirectYT'))

# Endpoint Index
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    else:
        return "TO DO" # Get playlist link from form and convert to youtube playlist

# Log in user to the web app using OAuth
@app.route("/login")
def login():
     # Forget any user_id
    session.clear()

    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index", _external=True))

# After login, redirect user to the page with the correct authorization token
@app.route("/redirect")
def redirectSite():
    sp_oauth = create_spotify_oauth()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info

    return redirect(url_for("redirectYT", _external=True))

@app.route("/redirectYT")
def redirectYT():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

   # Create OAuth flow object
    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"])
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='select_account')
    
    # Save the state so we can verify the request later
    session['state'] = state
    
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # Verify the request state
    if request.args.get('state') != session['state']:
        raise Exception('Invalid state')
    
    # Create the OAUth flow object
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
        state=session['state'])
    flow.redirect_uri = url_for('callback', _external=True)

    # Exchange the authorization code for an access token
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Save credentials to the session
    credentials = flow.credentials
    session['credentials'] = credentials.to_json()

    return redirect(url_for('getPlaylists'))

@app.route('/getPlaylists')
def getPlaylists():
    try: 
        token_info = get_token()
    except Exception as e:
        print(f"Exception: {e}")
        return redirect(url_for("login", _external=True))
    

    sp = spotipy.Spotify(auth = token_info['access_token'])
    credentialscheck()
    user = sp.current_user()
    username = user['display_name']
    
    # Getting all playlists (since the current_user_playlists max limit is 50, we need a 'for' loop)
    allPlaylists = []
    i = 0
    while True:
        fiftyplaylists = sp.current_user_playlists(limit=50, offset=i * 50)['items']
        i += 1
        allPlaylists += fiftyplaylists
        if(len(fiftyplaylists)< 50):
            break

    # Filtering the data we actually need in each playlist and sorting them alphabetically)
    playlists = [{'name': playlist['name'], 'id': playlist['id']} for playlist in allPlaylists]
    playlists.sort(key=lambda x: x['name'])

    return render_template("getPlaylists.html", playlists=playlists, username=username)

# Convert the playlist to youtube:
@app.route('/convertPlaylist', methods=['GET', 'POST'])
def convertPlaylist():
    
    # Check credentials (Spotify and Youtube)
    try: 
        token_info = get_token()
    except Exception as e:
        print(f"Exception: {e}")
        return redirect(url_for("login", _external=True))

    sp = spotipy.Spotify(auth = token_info['access_token'])
    
    # Check for credentials
    json_credentials = session.get('credentials')
    
    if 'credentials' in session:
        dict_credentials = json.loads(json_credentials)
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(dict_credentials)
        

        if credentials.expired:
            credentials.refresh(Request())

    else:
        return redirect(url_for('redirectYT'))

    youtube = build("youtube", "v3", credentials=credentials)
            
    try:

        # Get Spotify playlist name
        playlistid = request.form['playlistid']
        print(playlistid)
        playlist = sp.playlist(playlist_id = playlistid)
        playlistname = playlist['name']
        print(playlistname)

        # Create an empty playlist in Youtube using Spotify playlist name and get it's ID
        yt_request_newpl = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                "title": playlistname,
                "description": "Playlist automatically created with SPOT Labs!",
                },
                "status": {
                    "privacyStatus": "public"
                }})
        response = yt_request_newpl.execute()
        playlist_id = response['id']


        # Put all tracks in the Spotify playlist in a dictionaire
        allTracks = []
        i = 0
        # A loop is needed here because the playlist_tracks method only has a limit of 100 tracks.
        while True:
            hundredtracks = sp.playlist_tracks(playlistid, limit=100, offset=i * 100)['items']
            i += 1
            allTracks += hundredtracks
            if(len(hundredtracks) < 100):
                break

        track_artist_dict = {}
            
        for track in allTracks:
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            track_artist_dict[track_name] = artist_name
            
        # Use the dictionaire to search for each track/artist and get its video ID
        for track in track_artist_dict:
            yt_request_search = youtube.search().list(
                part="snippet",
                maxResults=1,
                order="relevance",
                q = track + " " + track_artist_dict[track]
                )
            response = yt_request_search.execute()
            video_id = response['items'][0]['id']['videoId']
                
             # Add the video of the track in the playlist using the videoID
            yt_request_insert_track = youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                )
            response = yt_request_insert_track.execute()

        return render_template('success.html')
        
    except Exception as e:
        print(e) # Print the error message for debugging
        return render_template('failure.html')

    