#!/usr/bin/env python3
"""Example usage for the podcast generator."""

from __future__ import annotations

from podcast_generator import PodcastGenerator


DOCUMENT_PATH = "your_document.pdf"
PAPER_TITLE = "Optional Episode Title"
OUTPUT_DIR = "output"
DURATION_MINUTES = 15
GENERATE_AUDIO = True


def main() -> None:
    generator = PodcastGenerator()
    script_path, audio_path = generator.create_podcast(
        document_path=DOCUMENT_PATH,
        output_dir=OUTPUT_DIR,
        paper_title=PAPER_TITLE,
        duration_minutes=DURATION_MINUTES,
        generate_audio=GENERATE_AUDIO,
    )

    print(f"Script saved to: {script_path}")
    if audio_path:
        print(f"Audio saved to: {audio_path}")


if __name__ == "__main__":
    main()

