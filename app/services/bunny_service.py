import hashlib
import time
import requests
from typing import Optional, Dict, Any
from app.config import settings

class BunnyStreamService:
    @classmethod
    def get_base_url(cls) -> str:
        return f"https://video.bunnycdn.com/library/{settings.BUNNY_STREAM_LIBRARY_ID}"

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        return {
            "AccessKey": settings.BUNNY_STREAM_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @classmethod
    def create_video(cls, title: str, collection_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new video entry in Bunny Stream.
        Returns video details including 'guid' (videoId).
        """
        url = f"{cls.get_base_url()}/videos"
        payload = {"title": title}
        if collection_id:
            payload["collectionId"] = collection_id

        response = requests.post(url, json=payload, headers=cls.get_headers(), timeout=15)
        response.raise_for_status()
        return response.json()

    @classmethod
    def upload_video(cls, video_guid: str, video_bytes: bytes) -> Dict[str, Any]:
        """
        Uploads raw binary video content to a created video entry.
        """
        url = f"{cls.get_base_url()}/videos/{video_guid}"
        headers = {
            "AccessKey": settings.BUNNY_STREAM_API_KEY,
            "Content-Type": "application/octet-stream"
        }
        response = requests.put(url, data=video_bytes, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_video(cls, video_guid: str) -> Dict[str, Any]:
        """
        Fetches status, encoding progress, and metadata for a video.
        """
        url = f"{cls.get_base_url()}/videos/{video_guid}"
        response = requests.get(url, headers=cls.get_headers(), timeout=15)
        response.raise_for_status()
        return response.json()

    @classmethod
    def delete_video(cls, video_guid: str) -> bool:
        """
        Deletes a video from Bunny Stream.
        """
        url = f"{cls.get_base_url()}/videos/{video_guid}"
        response = requests.delete(url, headers=cls.get_headers(), timeout=15)
        return response.status_code == 200

    @classmethod
    def get_hls_url(cls, video_guid: str, expires_in_seconds: Optional[int] = None) -> str:
        """
        Returns the HLS Master Playlist URL (.m3u8).
        If token auth key is configured and expires_in_seconds is provided, generates a signed token.
        """
        host = settings.BUNNY_STREAM_CDN_HOSTNAME or f"vz-{settings.BUNNY_STREAM_LIBRARY_ID}.b-cdn.net"
        path = f"/{video_guid}/playlist.m3u8"

        if settings.BUNNY_STREAM_TOKEN_AUTH_KEY and expires_in_seconds:
            expires = int(time.time()) + expires_in_seconds
            hashable = f"{settings.BUNNY_STREAM_TOKEN_AUTH_KEY}{path}{expires}"
            token = hashlib.sha256(hashable.encode("utf-8")).hexdigest()
            return f"https://{host}{path}?token={token}&expires={expires}"

        return f"https://{host}{path}"

    @classmethod
    def get_thumbnail_url(cls, video_guid: str) -> str:
        """
        Returns the primary thumbnail URL for the video.
        """
        host = settings.BUNNY_STREAM_CDN_HOSTNAME or f"vz-{settings.BUNNY_STREAM_LIBRARY_ID}.b-cdn.net"
        return f"https://{host}/{video_guid}/thumbnail.jpg"

    @classmethod
    def get_preview_animation_url(cls, video_guid: str) -> str:
        """
        Returns the animated preview WebP URL.
        """
        host = settings.BUNNY_STREAM_CDN_HOSTNAME or f"vz-{settings.BUNNY_STREAM_LIBRARY_ID}.b-cdn.net"
        return f"https://{host}/{video_guid}/preview.webp"
