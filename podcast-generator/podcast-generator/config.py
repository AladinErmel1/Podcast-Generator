"""Configuration defaults for the podcast generator."""

from __future__ import annotations

# Podcast duration controls.
VALID_DURATIONS_MINUTES = (5, 10, 15, 20)
DEFAULT_DURATION_MINUTES = 15
MAX_DURATION_MINUTES = 20
WORDS_PER_MINUTE = 150
SCRIPT_WORD_TOLERANCE = 0.10

# Model defaults.
SCRIPT_MODEL = "gpt-5.5"
TTS_MODEL = "gpt-4o-mini-tts"

# OpenAI speech endpoint input limit is 4096 characters. Keep a margin for safety.
TTS_MAX_INPUT_CHARS = 3800

# Document extraction and source-note limits.
MAX_SOURCE_CHARS_FOR_NOTES = 60000
SOURCE_CHUNK_CHARS = 9000

# Speaker configuration.
SPEAKER_NAMES = {
    "woman": "SARAH",
    "man": "MIKE",
}

SPEAKER_PROFILES = {
    "woman": "an experienced audit professional and risk management expert",
    "man": "a governance specialist and researcher",
}

SPEAKER_VOICES = {
    "woman": "marin",
    "man": "cedar",
}

SPEAKER_TTS_INSTRUCTIONS = {
    "woman": (
        "Speak as Sarah: warm, thoughtful, clear, and engaged. "
        "Use a professional podcast-host tone."
    ),
    "man": (
        "Speak as Mike: calm, precise, curious, and conversational. "
        "Use a professional researcher tone."
    ),
}

# Audio settings.
SPEECH_SPEED = 1.0
PAUSE_BETWEEN_SPEAKERS_MS = 300

# Output settings.
DEFAULT_OUTPUT_DIR = "output"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Script structure as fractions of the requested duration.
SCRIPT_SECTIONS = (
    ("opening", "Warm opening and why this document matters", 0.08),
    (
        "understanding",
        "Explain the document's main topic, methods or argument, evidence, findings, and conclusions",
        0.42,
    ),
    (
        "analysis",
        "Explore future risks, risk management, roles, assurance, governance, and practical implications",
        0.40,
    ),
    ("closing", "Key takeaways and a concise closing reflection", 0.10),
)

