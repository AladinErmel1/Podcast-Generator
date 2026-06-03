#!/usr/bin/env python3
"""Batch podcast generation for PDF, TXT, and DOCX documents."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import config
from podcast_generator import PodcastGenerator


SUPPORTED_SUFFIXES = {".pdf", ".txt", ".docx"}


class BatchPodcastGenerator:
    """Generate podcasts for all supported documents in a folder."""

    def __init__(
        self,
        input_folder: str,
        output_folder: str = config.DEFAULT_OUTPUT_DIR,
        duration_minutes: int = config.DEFAULT_DURATION_MINUTES,
        generate_audio: bool = True,
    ):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.duration_minutes = PodcastGenerator.validate_duration(duration_minutes)
        self.generate_audio = generate_audio
        self.generator = PodcastGenerator()
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.results = {
            "successful": [],
            "failed": [],
            "total": 0,
            "start_time": datetime.now().isoformat(),
        }

    def process_all_documents(self, titles: dict[str, str] | None = None) -> dict:
        titles = titles or {}
        files = [
            path
            for path in self.input_folder.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        ]
        self.results["total"] = len(files)

        if not files:
            print(f"No supported documents found in {self.input_folder}")
            return self.results

        for index, document in enumerate(files, start=1):
            print(f"Processing {index}/{len(files)}: {document.name}")
            try:
                title = titles.get(document.name, document.stem)
                script_path, audio_path = self.generator.create_podcast(
                    document_path=document,
                    output_dir=self.output_folder,
                    paper_title=title,
                    duration_minutes=self.duration_minutes,
                    generate_audio=self.generate_audio,
                )
                self.results["successful"].append(
                    {
                        "document": document.name,
                        "title": title,
                        "script": script_path,
                        "audio": audio_path,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as exc:
                self.results["failed"].append(
                    {
                        "document": document.name,
                        "error": str(exc),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                print(f"Failed: {document.name}: {exc}")

        self._save_results()
        self._print_summary()
        return self.results

    def _save_results(self) -> None:
        results_file = self.output_folder / f"batch_results_{datetime.now().strftime(config.TIMESTAMP_FORMAT)}.json"
        results_file.write_text(json.dumps(self.results, indent=2), encoding="utf-8")
        print(f"Results saved to: {results_file}")

    def _print_summary(self) -> None:
        successful = len(self.results["successful"])
        failed = len(self.results["failed"])
        total = self.results["total"]
        print(f"Batch complete: {successful}/{total} successful, {failed}/{total} failed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch generate podcasts from local documents.")
    parser.add_argument("input_folder", help="Folder containing PDF, TXT, or DOCX documents.")
    parser.add_argument("output_folder", nargs="?", default=config.DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--duration",
        type=int,
        default=config.DEFAULT_DURATION_MINUTES,
        choices=config.VALID_DURATIONS_MINUTES,
    )
    parser.add_argument("--script-only", action="store_true")
    args = parser.parse_args()

    batch = BatchPodcastGenerator(
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        duration_minutes=args.duration,
        generate_audio=not args.script_only,
    )
    batch.process_all_documents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

