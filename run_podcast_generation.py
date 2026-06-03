#!/usr/bin/env python3
"""Command-line entry point for the podcast generator."""

from __future__ import annotations

import argparse
import os
import sys

PROJECT_DIR = os.path.join(os.path.dirname(__file__), "podcast-generator", "podcast-generator")
sys.path.insert(0, PROJECT_DIR)

import config
from podcast_generator import PodcastGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Mike/Sarah podcast from a PDF, TXT, or DOCX document."
    )
    parser.add_argument("--input", required=True, help="Path to a PDF, TXT, or DOCX document.")
    parser.add_argument("--output-dir", default=config.DEFAULT_OUTPUT_DIR, help="Output directory.")
    parser.add_argument("--title", default=None, help="Optional document or episode title.")
    parser.add_argument(
        "--duration",
        type=int,
        default=config.DEFAULT_DURATION_MINUTES,
        choices=config.VALID_DURATIONS_MINUTES,
        help="Podcast duration preset in minutes.",
    )
    parser.add_argument("--script-only", action="store_true", help="Generate script without audio.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generator = PodcastGenerator()
    try:
        script_path, audio_path = generator.create_podcast(
            document_path=args.input,
            output_dir=args.output_dir,
            paper_title=args.title,
            duration_minutes=args.duration,
            generate_audio=not args.script_only,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Script: {script_path}")
    if audio_path:
        print(f"Audio: {audio_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

