from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


flow = InstalledAppFlow.from_client_secrets_file(
    "client_secrets.json",
    scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
)

flow.run_local_server(port=5000, prompt="consent")

credentials = flow.credentials

print(credentials.to_json())


# youtube = build('youtube', 'v3', developerKey=yt_api_key)

# request = youtube.channels().list(
#    part='contentDetails', forUsername='lightzin'
#)

#response = request.execute()

#print(response)