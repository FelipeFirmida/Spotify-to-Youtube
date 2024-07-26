import spotipy
from spotipy.oauth2 import SpotifyOAuth

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import google.oauth2.credentials
from googleapiclient.errors import HttpError

import json
import os
import os.path
import time

from flask import Flask, request, url_for, session, redirect, render_template
from flask_session import Session

import clientinfo # File containing all the info necessary to login the web APP to the Spotify and youtube APIs

""" requirements [
    Flask,
    Spotipy,
    Spotify OAuth,
    Google/Youtube OAuth,
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
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.environ['SPOTIFY_CLIENT_ID'],
        client_secret = os.environ['SPOTIFY_CLIENT_SECRET'],
        redirect_uri = url_for('redirectSite', _external=True),
        scope = "user-read-private playlist-read-private playlist-read-collaborative",
        cache_handler=cache_handler,
        show_dialog=True
    )

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
@app.route('/', methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    

# Log in user to the web app using Spotify OAuth
@app.route("/login")
def login():
     # Forget any user_id
    session.clear()

    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Logout user
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index", _external=True))

# After login, redirect user to the page with the correct authorization token
@app.route("/redirect")
def redirectSite():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)

    session["token_info"] = token_info

    return redirect(url_for("redirectYT", _external=True))

# Redirect Page to the YouTube OAuth
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

# Callback page to check Google OAuth
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

# Web page where the Spotify Playlists are listed
@app.route('/getPlaylists')
def getPlaylists():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        print("User not authorized!")
        return redirect('/')
    credentialscheck()

    sp = spotipy.Spotify(auth = session.get('token_info').get('access_token'))
    user = sp.current_user()
    username = user['display_name']
    
    # Getting all playlists (since the current_user_playlists max limit is 50, we need a 'for' loop)
    allPlaylists = []
    i = 0
    while True:
        fiftyplaylists = sp.current_user_playlists(limit=50, offset=i * 50)['items']
        i += 1
        allPlaylists += fiftyplaylists
        if (len(fiftyplaylists)< 50):
            break

    # Filtering the data we actually need in each playlist and sorting them alphabetically)
    playlists = [{'name': playlist['name'], 'id': playlist['id']} for playlist in allPlaylists]
    playlists.sort(key=lambda x: x['name'])

    return render_template("getPlaylists.html", playlists=playlists, username=username)

def get_token(session):
    token_valid = False
    token_info = session.get("token_info", None)

    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid
    
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))
    
    token_valid = True
    return token_info, token_valid

# Convert the playlist to youtube:
@app.route('/convertPlaylist', methods=['GET', 'POST'])
def convertPlaylist():
    
    def get_token(session):
            token_valid = False
            token_info = session.get("token_info", None)

            if not (session.get('token_info', False)):
                token_valid = False
                return token_info, token_valid
        
            now = int(time.time())
            is_token_expired = session.get('token_info').get('expires_at') - now < 60

            if (is_token_expired):
                sp_oauth = create_spotify_oauth()
                token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))
        
            token_valid = True
            return token_info, token_valid

    # Check credentials (Spotify)
    try: 
        session['token_info'], authorized = get_token(session)
        session.modified = True
        if not authorized:
            print("User not authorized!")
            return redirect('/')
        
    except Exception as e:
        print(f"Exception: {e}")
        return redirect(url_for("login", _external=True))

    sp = spotipy.Spotify(auth = session.get('token_info').get('access_token'))
    
    # Check for credentials (Youtube)
    json_credentials = session.get('credentials')
    
    if 'credentials' in session:
        dict_credentials = json.loads(json_credentials)
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(dict_credentials)
        

        if credentials.expired:
            credentials.refresh(Request())

    else:
        return redirect(url_for('redirectYT'))

    # Create youtube variable to use youtube related methods
    youtube = build("youtube", "v3", credentials=credentials)
            
    try:

        # Get Spotify playlist name
        playlistid = request.form['playlistid']
        playlist = sp.playlist(playlist_id = playlistid)
        playlistname = playlist['name']

        # Create an empty playlist in Youtube using Spotify playlist name and get it's ID
        yt_request_newpl = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                "title": playlistname,
                "description": "Playlist automatically created with BEAT Labs!",
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
        # # I will limit this to 50 because of YouTube API terrible quota system (only 10k quota)
        while True:
            hundredtracks = sp.playlist_tracks(playlistid, limit=50, offset=i * 100)['items']
            i += 1
            allTracks += hundredtracks
            if(len(hundredtracks) <= 50):
                break

        track_artist_dict = {}
            
        for track in allTracks:
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            track_artist_dict[track_name] = artist_name
            
        # Use the dictionaire to search for each track/artist and get its video ID
        for track in track_artist_dict:
            max_retries = 5
            retry_count = 0
            backoff_time = 1 # In seconds

            while retry_count < max_retries:
                try:
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
                    break

                except HttpError as e:
                    if e.resp.status == 409 and 'SERVICE_UNAVAILABLE' in str(e):
                        retry_count += 1
                        print(f"Attempt {retry_count} failed. Retrying in (backoff_time) seconds...")
                        time.sleep(backoff_time)
                        backoff_time *= 2 #Exponential backoff
                    else:
                        raise
            else:
                raise Exception("Failed to add the song to the playlist after multiple retries.")    

        return render_template('success.html')
        
    except Exception as e:
        print(e) # Print the error message for debugging
        return render_template('failure.html')
    
###########################    (CODE NOT YET IMPLEMENTED) Here starting the New Tool - Convert URL process ###########################################

### @app.route("/redirectYT2")
def redirectYT2():
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

@app.route('/callback2')
def callback2():
    # Verify the request state
    if request.args.get('state') != session['state']:
        raise Exception('Invalid state')
    
    # Create the OAUth flow object
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
        state=session['state'])
    flow.redirect_uri = url_for('callback2', _external=True)

    # Exchange the authorization code for an access token
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Save credentials to the session
    credentials = flow.credentials
    session['credentials'] = credentials.to_json()

    return redirect(url_for('convertPlaylistUrl'))

# Convert playlist from the Spotify URL input located in the index.    
# @app.route('/convertPlaylistUrl', methods=['GET', 'POST'])
# def convertPlaylistUrl():
#     # OAuth Youtube
#  # Check for credentials (Youtube)
#     json_credentials = session.get('credentials')
    
#     if 'credentials' in session:
#         dict_credentials = json.loads(json_credentials)
#         credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(dict_credentials)
        

#         if credentials.expired:
#             credentials.refresh(Request())

#     else:
#         return redirect(url_for('redirectYT'))

#     # Create
#     youtube = build("youtube", "v3", credentials=credentials)
            
#     try:

#          # Get Spotify Playlist ID
#         playlisturl = request.form('url')
#         parts = playlisturl.split('/')
#         playlistid = parts[-1]

#         # Get Spotify playlist name
#         playlist = sp.playlist(playlist_id = playlistid)
#         playlistname = playlist['name']
#         print(playlistname)

#         # Create an empty playlist in Youtube using Spotify playlist name and get it's ID
#         yt_request_newpl = youtube.playlists().insert(
#             part="snippet,status",
#             body={
#                 "snippet": {
#                 "title": playlistname,
#                 "description": "Playlist automatically created with BEAT Labs!",
#                 },
#                 "status": {
#                     "privacyStatus": "public"
#                 }})
#         response = yt_request_newpl.execute()
#         playlist_id = response['id']


#         # Put all tracks in the Spotify playlist in a dictionaire
#         allTracks = []
#         i = 0
#         # A loop is needed here because the playlist_tracks method only has a limit of 100 tracks.
#         while True:
#             hundredtracks = sp.playlist_tracks(playlistid, limit=100, offset=i * 100)['items']
#             i += 1
#             allTracks += hundredtracks
#             if(len(hundredtracks) < 100):
#                 break

#         track_artist_dict = {}
            
#         for track in allTracks:
#             track_name = track['track']['name']
#             artist_name = track['track']['artists'][0]['name']
#             track_artist_dict[track_name] = artist_name
            
#         # Use the dictionaire to search for each track/artist and get its video ID
#         for track in track_artist_dict:
#             yt_request_search = youtube.search().list(
#                 part="snippet",
#                 maxResults=1,
#                 order="relevance",
#                 q = track + " " + track_artist_dict[track]
#                 )
#             response = yt_request_search.execute()
#             video_id = response['items'][0]['id']['videoId']
                
#              # Add the video of the track in the playlist using the videoID
#             yt_request_insert_track = youtube.playlistItems().insert(
#                     part="snippet",
#                     body={
#                         "snippet": {
#                             "playlistId": playlist_id,
#                             "resourceId": {
#                                 "kind": "youtube#video",
#                                 "videoId": video_id
#                             }
#                         }
#                     }
#                 )
#             response = yt_request_insert_track.execute()

#         return render_template('success.html')
        
#     except Exception as e:
#         print(e) # Print the error message for debugging
#         return render_template('failure.html') ###
