import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube"]

CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "youtube_token.pickle")


def _get_authenticated_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(
                    "[!] YouTube OAuth client_secret.json not found.\n"
                    "    To enable YouTube upload:\n"
                    "    1. Go to https://console.cloud.google.com/apis/credentials\n"
                    "    2. Create OAuth 2.0 Client ID (Desktop app)\n"
                    "    3. Download JSON and save as 'client_secret.json'\n"
                    "    4. Place it in the ai-news-bot folder"
                )
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path,
    title,
    description="",
    tags=None,
    category_id="28",
    privacy_status="public",
):
    youtube = _get_authenticated_service()
    if youtube is None:
        print("[!] YouTube upload skipped (no auth)")
        return None

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": (tags or [])[:500],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    import mimetypes
    mime_type, _ = mimetypes.guess_type(video_path)
    media = MediaFileUpload(video_path, mimetype=mime_type or "video/mp4", resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"[+] Uploading '{title}' to YouTube ({privacy_status})...")
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
        except Exception as e:
            print(f"[!] Upload chunk error: {e}")
            return None
        if status:
            pct = int(status.progress() * 100)
            print(f"    Upload progress: {pct}%")

    video_id = response.get("id")
    if not video_id:
        print(f"[!] Upload returned no video ID. Response: {response}")
        return None

    # Verify the video was created
    try:
        verify = youtube.videos().list(part="status,snippet", id=video_id).execute()
        items = verify.get("items", [])
        if items:
            v = items[0]
            print(f"    Verified: '{v['snippet']['title']}' ({v['status']['privacyStatus']})")
        else:
            print(f"[!] Warning: video ID {video_id} not found after upload")
    except Exception as e:
        print(f"[!] Could not verify upload: {e}")

    print(f"[+] Upload complete! Video ID: {video_id}")
    print(f"    URL: https://youtu.be/{video_id}")
    return video_id


def upload_thumbnail(video_id, thumbnail_path):
    if not os.path.exists(thumbnail_path):
        print(f"[!] Thumbnail not found: {thumbnail_path}")
        return False
    youtube = _get_authenticated_service()
    if youtube is None:
        return False
    try:
        media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=media,
        ).execute()
        print(f"[+] Thumbnail uploaded for video {video_id}")
        return True
    except Exception as e:
        print(f"[!] Thumbnail upload failed: {e}")
        return False
