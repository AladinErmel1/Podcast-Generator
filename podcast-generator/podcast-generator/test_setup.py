#!/usr/bin/env python3
"""Environment check for the podcast generator."""

from __future__ import annotations

import os
import shutil
import sys

from dotenv import load_dotenv

import config

load_dotenv()


def test_python_version() -> bool:
    version = sys.version_info
    ok = version.major == 3 and version.minor >= 10
    print(f"Python {version.major}.{version.minor}.{version.micro}: {'OK' if ok else 'Need 3.10+'}")
    return ok


def test_imports() -> bool:
    packages = {
        "openai": "OpenAI SDK",
        "PyPDF2": "PyPDF2",
        "pdfplumber": "pdfplumber",
        "pydub": "pydub",
        "docx": "python-docx",
        "streamlit": "Streamlit",
    }
    ok = True
    for package, label in packages.items():
        try:
            __import__(package)
            print(f"{label}: OK")
        except ImportError:
            print(f"{label}: missing")
            ok = False
    return ok


def test_api_key() -> bool:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY: missing")
        return False
    print(f"OPENAI_API_KEY: present ({api_key[:7]}...)")
    return True


def test_framework() -> bool:
    try:
        from podcast_generator import PodcastGenerator

        generator = PodcastGenerator()
        PodcastGenerator.validate_duration(config.DEFAULT_DURATION_MINUTES)
        print(f"Framework: OK (script model {generator.script_model}, TTS model {generator.tts_model})")
        return True
    except Exception as exc:
        print(f"Framework: failed ({exc})")
        return False


def test_ffmpeg() -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        print(f"FFmpeg: OK ({ffmpeg})")
        return True
    print("FFmpeg: missing. Install it if MP3 combining fails.")
    return False


def main() -> int:
    results = {
        "python": test_python_version(),
        "imports": test_imports(),
        "api_key": test_api_key(),
        "framework": test_framework(),
        "ffmpeg": test_ffmpeg(),
    }
    required = ["python", "imports", "api_key", "framework"]
    required_ok = all(results[name] for name in required)
    print(f"Required checks: {sum(results[name] for name in required)}/{len(required)}")
    return 0 if required_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

