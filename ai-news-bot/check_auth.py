import os, pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "youtube_token.pickle")
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")

creds = None
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)

youtube = build("youtube", "v3", credentials=creds)

# Get channel info
channels = youtube.channels().list(part="snippet", mine=True).execute()
for ch in channels.get("items", []):
    print(f"Channel: {ch['snippet']['title']} ({ch['id']})")

# Check if our video exists
try:
    video = youtube.videos().list(part="status,snippet", id="xEjzhAqD5Kg").execute()
    items = video.get("items", [])
    if items:
        v = items[0]
        print(f"Video found: {v['snippet']['title']} - Status: {v['status']['privacyStatus']}")
    else:
        print("Video xEjzhAqD5Kg NOT found on this channel")
except Exception as e:
    print(f"Error checking video: {e}")
