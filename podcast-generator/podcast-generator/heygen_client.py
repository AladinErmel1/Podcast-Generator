"""Small HeyGen API client for private voice listing and speech synthesis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


HEYGEN_API_BASE_URL = "https://api.heygen.com"


@dataclass(frozen=True)
class HeyGenVoice:
    voice_id: str
    name: str
    language: str | None = None
    gender: str | None = None

    @property
    def label(self) -> str:
        details = ", ".join(part for part in (self.language, self.gender) if part)
        return f"{self.name} ({details})" if details else self.name


def parse_heygen_voices(payload: dict[str, Any]) -> list[HeyGenVoice]:
    """Parse HeyGen voice-list responses across common response shapes."""
    raw_voices = payload.get("voices")
    if raw_voices is None:
        raw_voices = payload.get("data", {}).get("voices")
    if raw_voices is None and isinstance(payload.get("data"), list):
        raw_voices = payload["data"]
    raw_voices = raw_voices or []

    voices: list[HeyGenVoice] = []
    for item in raw_voices:
        voice_id = item.get("voice_id") or item.get("voiceId") or item.get("id")
        name = item.get("name") or item.get("voice_name") or item.get("display_name")
        if not voice_id or not name:
            continue
        voices.append(
            HeyGenVoice(
                voice_id=str(voice_id),
                name=str(name),
                language=item.get("language") or item.get("locale"),
                gender=item.get("gender"),
            )
        )
    return voices


def parse_heygen_speech_url(payload: dict[str, Any]) -> str:
    """Parse HeyGen speech-create responses and return the generated audio URL."""
    candidates = [
        payload.get("url"),
        payload.get("audio_url"),
        payload.get("audioUrl"),
        payload.get("data", {}).get("url") if isinstance(payload.get("data"), dict) else None,
        payload.get("data", {}).get("audio_url") if isinstance(payload.get("data"), dict) else None,
        payload.get("data", {}).get("audioUrl") if isinstance(payload.get("data"), dict) else None,
    ]
    for value in candidates:
        if value:
            return str(value)
    raise ValueError("HeyGen speech response did not include an audio URL.")


class HeyGenClient:
    def __init__(self, api_key: str, base_url: str = HEYGEN_API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    @property
    def headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def list_private_voices(self) -> list[HeyGenVoice]:
        response = requests.get(
            f"{self.base_url}/v3/voices",
            headers=self.headers,
            params={"type": "private", "engine": "starfish", "limit": 100},
            timeout=30,
        )
        response.raise_for_status()
        return parse_heygen_voices(response.json())

    def create_speech_url(
        self,
        voice_id: str,
        text: str,
        speed: float = 1.0,
        locale: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "voiceId": voice_id,
            "text": text,
            "inputType": "text",
            "speed": speed,
        }
        if locale:
            payload["locale"] = locale
        response = requests.post(
            f"{self.base_url}/v3/voices/speech",
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return parse_heygen_speech_url(response.json())


def download_audio(url: str) -> bytes:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.content

