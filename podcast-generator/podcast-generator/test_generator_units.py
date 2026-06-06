#!/usr/bin/env python3
"""Unit-style tests for podcast generator helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from docx import Document

from heygen_client import HeyGenClient, parse_heygen_speech_url, parse_heygen_voices
from podcast_generator import DialogueSegment, PodcastGenerator


class PodcastGeneratorHelperTests(unittest.TestCase):
    def test_duration_validation_accepts_only_presets(self) -> None:
        self.assertEqual(PodcastGenerator.validate_duration(15), 15)
        with self.assertRaises(ValueError):
            PodcastGenerator.validate_duration(25)
        with self.assertRaises(ValueError):
            PodcastGenerator.validate_duration("abc")

    def test_parser_keeps_mike_and_sarah_turns(self) -> None:
        generator = PodcastGenerator(openai_api_key="sk-test")
        dialogue = generator._parse_script(
            """
            TITLE
            SARAH: Welcome to the episode.
            MIKE: Thanks, Sarah.
            ALEX: This should be ignored.
            SARAH: Let us continue.
            """
        )
        self.assertEqual(
            dialogue,
            [
                DialogueSegment("woman", "Welcome to the episode."),
                DialogueSegment("man", "Thanks, Sarah."),
                DialogueSegment("woman", "Let us continue."),
            ],
        )

    def test_parser_supports_custom_speaker_names(self) -> None:
        generator = PodcastGenerator(
            openai_api_key="sk-test",
            speaker_names={"woman": "Anna", "man": "Ben"},
        )
        dialogue = generator._parse_script(
            """
            ANNA: Let us introduce the document.
            BEN: I want to unpack the main risk.
            """
        )
        self.assertEqual(
            dialogue,
            [
                DialogueSegment("woman", "Let us introduce the document."),
                DialogueSegment("man", "I want to unpack the main risk."),
            ],
        )

    def test_tts_chunker_respects_character_limit(self) -> None:
        text = " ".join(["This is a sentence."] * 600)
        chunks = PodcastGenerator.split_tts_input(text, max_chars=500)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 500 for chunk in chunks))

    def test_word_count_bounds_detect_short_script(self) -> None:
        generator = PodcastGenerator(openai_api_key="sk-test")
        minimum, maximum = generator.word_count_bounds(15)
        self.assertLess(1000, minimum)
        self.assertGreater(maximum, minimum)

    def test_word_count_bounds_for_all_duration_presets(self) -> None:
        generator = PodcastGenerator(openai_api_key="sk-test")
        expected = {
            5: (675, 825),
            10: (1350, 1650),
            15: (2025, 2475),
            20: (2700, 3300),
        }
        for duration, bounds in expected.items():
            self.assertEqual(generator.word_count_bounds(duration), bounds)

    def test_trim_dialogue_to_word_limit(self) -> None:
        generator = PodcastGenerator(openai_api_key="sk-test")
        dialogue = [
            DialogueSegment("woman", " ".join(["one"] * 120)),
            DialogueSegment("man", " ".join(["two"] * 80)),
        ]
        trimmed = generator._trim_dialogue_to_word_limit(dialogue, max_words=150)
        self.assertLessEqual(generator._dialogue_word_count(trimmed), 150)

    def test_expand_dialogue_to_word_minimum(self) -> None:
        generator = PodcastGenerator(openai_api_key="sk-test")
        dialogue = [
            DialogueSegment("woman", "This is short."),
            DialogueSegment("man", "Very short."),
        ]
        expanded = generator._expand_dialogue_to_word_minimum(
            dialogue,
            min_words=80,
            max_words=140,
        )
        words = generator._dialogue_word_count(expanded)
        self.assertGreaterEqual(words, 80)
        self.assertLessEqual(words, 140)

    def test_txt_and_docx_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            txt_path = temp_root / "sample.txt"
            txt_path.write_text("A useful source document.", encoding="utf-8")

            docx_path = temp_root / "sample.docx"
            document = Document()
            document.add_paragraph("A DOCX source document.")
            document.save(docx_path)

            generator = PodcastGenerator(openai_api_key="sk-test")
            self.assertIn("useful source", generator.extract_text(txt_path))
            self.assertIn("DOCX source", generator.extract_text(docx_path))

    def test_invalid_file_type_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.csv"
            path.write_text("not supported", encoding="utf-8")
            generator = PodcastGenerator(openai_api_key="sk-test")
            with self.assertRaises(ValueError):
                generator.extract_text(path)

    def test_voice_provider_validation(self) -> None:
        generator = PodcastGenerator(
            openai_api_key="sk-test",
            speaker_voice_providers={"woman": "openai", "man": "heygen"},
        )
        self.assertEqual(generator.voice_providers["woman"], "openai")
        self.assertEqual(generator.voice_providers["man"], "heygen")
        with self.assertRaises(ValueError):
            PodcastGenerator(
                openai_api_key="sk-test",
                speaker_voice_providers={"woman": "invalid"},
            )

    def test_parse_heygen_private_voices(self) -> None:
        voices = parse_heygen_voices(
            {
                "data": {
                    "voices": [
                        {
                            "voice_id": "voice-1",
                            "name": "Aladin Ermel",
                            "language": "Mehrsprachig",
                            "gender": "Male",
                        },
                        {
                            "voiceId": "voice-2",
                            "voice_name": "Aladin Avatar",
                        },
                    ]
                }
            }
        )
        self.assertEqual(len(voices), 2)
        self.assertEqual(voices[0].voice_id, "voice-1")
        self.assertIn("Aladin Ermel", voices[0].label)

    def test_parse_heygen_official_data_list_response(self) -> None:
        voices = parse_heygen_voices(
            {
                "data": [
                    {
                        "voice_id": "voice-1",
                        "name": "Aladin Ermel",
                        "language": "Multilingual",
                        "gender": "Male",
                        "preview_audio_url": "https://example.com/preview.mp3",
                    }
                ],
                "has_more": False,
            }
        )
        self.assertEqual(len(voices), 1)
        self.assertEqual(voices[0].voice_id, "voice-1")
        self.assertEqual(voices[0].preview_audio_url, "https://example.com/preview.mp3")

    def test_parse_heygen_speech_url(self) -> None:
        self.assertEqual(
            parse_heygen_speech_url({"data": {"audio_url": "https://example.com/audio.mp3"}}),
            "https://example.com/audio.mp3",
        )
        with self.assertRaises(ValueError):
            parse_heygen_speech_url({"data": {}})

    def test_heygen_speech_uses_documented_request_fields(self) -> None:
        response = Mock()
        response.json.return_value = {"data": {"audio_url": "https://example.com/audio.mp3"}}
        response.raise_for_status.return_value = None

        with patch("heygen_client.requests.post", return_value=response) as post:
            audio_url = HeyGenClient("heygen-test").create_speech_url(
                voice_id="voice-1",
                text="Hello.",
            )

        self.assertEqual(audio_url, "https://example.com/audio.mp3")
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["voice_id"], "voice-1")
        self.assertEqual(payload["input_type"], "text")
        self.assertNotIn("voiceId", payload)
        self.assertNotIn("inputType", payload)

    def test_mixed_provider_tts_routing(self) -> None:
        class FakeSpeech:
            def create(self, **kwargs):
                class Response:
                    content = b"openai-audio"

                return Response()

        class FakeAudio:
            speech = FakeSpeech()

        class FakeClient:
            audio = FakeAudio()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            generator = PodcastGenerator(
                openai_api_key="sk-test",
                heygen_api_key="heygen-test",
                speaker_voice_providers={"woman": "openai", "man": "heygen"},
                speaker_voices={"woman": "marin", "man": "heygen-voice"},
            )
            generator.client = FakeClient()
            calls = []

            def fake_heygen(speaker, text, output_path):
                calls.append((speaker, text))
                output_path.write_bytes(b"heygen-audio")

            generator._write_heygen_tts_segment = fake_heygen
            openai_path = temp_root / "openai.mp3"
            heygen_path = temp_root / "heygen.mp3"
            generator._write_tts_segment("woman", "OpenAI line.", openai_path)
            generator._write_tts_segment("man", "HeyGen line.", heygen_path)

            self.assertEqual(openai_path.read_bytes(), b"openai-audio")
            self.assertEqual(heygen_path.read_bytes(), b"heygen-audio")
            self.assertEqual(calls, [("man", "HeyGen line.")])


if __name__ == "__main__":
    unittest.main()
