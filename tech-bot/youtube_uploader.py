#!/usr/bin/env python3

import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "credentials", "youtube_credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "credentials", "token.pickle")

RESUMABLE_UPLOAD = True
MAX_RETRIES = 10
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


def _get_authenticated_service():
    credentials = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"[!] YouTube credentials not found: {CLIENT_SECRETS_FILE}")
                print("    Download credentials from Google Cloud Console and place them here.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)


def upload_video(video_path, title, description, tags=None, category_id="28",
                 privacy_status="public", playlist_id=None):
    if not os.path.exists(video_path):
        print(f"[!] Video file not found: {video_path}")
        return None

    youtube = _get_authenticated_service()
    if not youtube:
        return None

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or [],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    if playlist_id:
        body["status"]["privacyStatus"] = "private"

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=RESUMABLE_UPLOAD,
    )

    print(f"    Uploading: {os.path.basename(video_path)}")
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    retry = 0
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"    Upload progress: {pct}%")
        except Exception as e:
            if hasattr(e, "resp") and hasattr(e.resp, "status"):
                status_code = e.resp.status
                if status_code in RETRIABLE_STATUS_CODES and retry < MAX_RETRIES:
                    retry += 1
                    print(f"    Retrying upload (attempt {retry}/{MAX_RETRIES})...")
                else:
                    print(f"[!] Upload failed: {e}")
                    return None
            else:
                print(f"[!] Upload failed: {e}")
                return None

    video_id = response.get("id")
    if video_id:
        print(f"    Video uploaded: https://youtu.be/{video_id}")

        if playlist_id:
            try:
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id,
                            },
                        },
                    },
                ).execute()
                print(f"    Added to playlist: {playlist_id}")
            except Exception as e:
                print(f"    Failed to add to playlist: {e}")

    return video_id


def upload_thumbnail(video_id, thumbnail_path):
    if not os.path.exists(thumbnail_path):
        print(f"[!] Thumbnail not found: {thumbnail_path}")
        return False

    youtube = _get_authenticated_service()
    if not youtube:
        return False

    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
        ).execute()
        print(f"    Thumbnail set for video: {video_id}")
        return True
    except Exception as e:
        print(f"[!] Thumbnail upload failed: {e}")
        return False


def list_uploads(max_results=10):
    youtube = _get_authenticated_service()
    if not youtube:
        return []

    try:
        response = youtube.channels().list(
            part="contentDetails",
            mine=True,
        ).execute()

        uploads_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        videos = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_id,
            maxResults=max_results,
        ).execute()

        return videos.get("items", [])
    except Exception as e:
        print(f"[!] Failed to list uploads: {e}")
        return []
