"""Streamlit web app for the podcast generator."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(__file__).parent / "podcast-generator" / "podcast-generator"
sys.path.insert(0, str(PROJECT_DIR))

import config
from podcast_generator import PodcastGenerator

load_dotenv()

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))


def collect_progress(message: str) -> None:
    if message.startswith(("Document:", "Script:", "Audio:", "=")):
        return
    st.session_state.setdefault("progress_messages", []).append(message)


def configured_api_key() -> str | None:
    if os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_API_KEY")
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = None
    if api_key:
        return str(api_key)
    return None


def get_api_key() -> str:
    api_key = configured_api_key()
    if api_key:
        st.caption("Using the configured server API key.")
        return api_key

    api_key = st.text_input(
        "OpenAI API key",
        type="password",
        placeholder="sk-...",
        help="Your key is used only for this session and is not saved by the app.",
    ).strip()
    if not api_key:
        st.info("Enter your OpenAI API key to generate a podcast.")
        st.stop()
    return api_key


def require_app_password() -> None:
    password = os.getenv("APP_PASSWORD")
    if not password:
        return

    entered = st.text_input("Password", type="password")
    if entered != password:
        st.stop()


def default_voice_label(voice_id: str) -> str:
    for label, value in config.VOICE_OPTIONS.items():
        if value == voice_id:
            return label
    return next(iter(config.VOICE_OPTIONS))


def generate_voice_preview(
    api_key: str,
    voice: str,
    speaker_name: str,
    speaker_role: str,
) -> bytes:
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model=config.TTS_MODEL,
        voice=voice,
        input=(
            f"Hi, I am {speaker_name}. This is a short preview of how I will sound "
            "in your podcast conversation."
        ),
        instructions=(
            f"Speak as {speaker_name}, {speaker_role}. "
            "Sound natural, clear, and conversational."
        ),
        response_format="mp3",
    )
    return response.content


def main() -> None:
    st.set_page_config(page_title="Podcast Generator", layout="centered")
    st.title("Podcast Generator")

    st.session_state.setdefault("progress_messages", [])
    st.session_state.setdefault("script_path", None)
    st.session_state.setdefault("audio_path", None)
    st.session_state.setdefault("voice_previews", {})

    require_app_password()
    api_key = get_api_key()

    uploaded_file = st.file_uploader(
        "Document",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=False,
    )
    if uploaded_file and uploaded_file.size > MAX_UPLOAD_MB * 1024 * 1024:
        st.error(f"File is too large. Maximum upload size is {MAX_UPLOAD_MB} MB.")
        st.stop()
    title = st.text_input("Title", placeholder="Optional; uses the filename if empty")
    duration = st.radio(
        "Duration",
        options=list(config.VALID_DURATIONS_MINUTES),
        index=list(config.VALID_DURATIONS_MINUTES).index(config.DEFAULT_DURATION_MINUTES),
        format_func=lambda value: f"{value} min",
        horizontal=True,
    )
    generate_audio = st.toggle("Create MP3 audio", value=True)

    with st.expander("Podcast hosts", expanded=False):
        speaker_col_1, speaker_col_2 = st.columns(2)
        voice_labels = list(config.VOICE_OPTIONS.keys())

        with speaker_col_1:
            woman_name = st.text_input("First host name", value="Sarah")
            woman_voice_label = st.selectbox(
                "First host voice",
                options=voice_labels,
                index=voice_labels.index(default_voice_label(config.SPEAKER_VOICES["woman"])),
            )
            woman_voice = config.VOICE_OPTIONS[woman_voice_label]
            if st.button("Preview first host", use_container_width=True):
                try:
                    st.session_state["voice_previews"]["woman"] = generate_voice_preview(
                        api_key,
                        woman_voice,
                        woman_name.strip() or "Sarah",
                        "an audit and risk management expert",
                    )
                except Exception as exc:
                    st.error(f"Preview failed: {exc}")
            if st.session_state["voice_previews"].get("woman"):
                st.audio(st.session_state["voice_previews"]["woman"], format="audio/mp3")

        with speaker_col_2:
            man_name = st.text_input("Second host name", value="Mike")
            man_voice_label = st.selectbox(
                "Second host voice",
                options=voice_labels,
                index=voice_labels.index(default_voice_label(config.SPEAKER_VOICES["man"])),
            )
            man_voice = config.VOICE_OPTIONS[man_voice_label]
            if st.button("Preview second host", use_container_width=True):
                try:
                    st.session_state["voice_previews"]["man"] = generate_voice_preview(
                        api_key,
                        man_voice,
                        man_name.strip() or "Mike",
                        "a governance specialist and researcher",
                    )
                except Exception as exc:
                    st.error(f"Preview failed: {exc}")
            if st.session_state["voice_previews"].get("man"):
                st.audio(st.session_state["voice_previews"]["man"], format="audio/mp3")

    generate_clicked = st.button(
        "Generate",
        type="primary",
        disabled=uploaded_file is None,
        use_container_width=True,
    )

    status_box = st.empty()
    progress_box = st.container()

    if generate_clicked and uploaded_file:
        st.session_state["progress_messages"] = []
        st.session_state["script_path"] = None
        st.session_state["audio_path"] = None

        suffix = Path(uploaded_file.name).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_path = Path(temp_file.name)

        try:
            with st.spinner("Generating podcast..."):
                generator = PodcastGenerator(
                    openai_api_key=api_key,
                    speaker_names={
                        "woman": woman_name.strip() or "Sarah",
                        "man": man_name.strip() or "Mike",
                    },
                    speaker_voices={
                        "woman": woman_voice,
                        "man": man_voice,
                    },
                    progress_callback=collect_progress,
                )
                output_dir = tempfile.mkdtemp(prefix="podcast_output_")
                script_path, audio_path = generator.create_podcast(
                    document_path=temp_path,
                    output_dir=output_dir,
                    paper_title=title.strip() or Path(uploaded_file.name).stem,
                    duration_minutes=duration,
                    generate_audio=generate_audio,
                )
                st.session_state["script_path"] = script_path
                st.session_state["audio_path"] = audio_path
            status_box.success("Done.")
        except Exception as exc:
            status_box.error(f"Generation failed: {exc}")
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    with progress_box:
        if st.session_state.get("progress_messages"):
            st.subheader("Progress")
            for message in st.session_state["progress_messages"][-12:]:
                st.write(message)

    script_path = st.session_state.get("script_path")
    audio_path = st.session_state.get("audio_path")

    if script_path:
        script_file = Path(script_path)
        script_text = script_file.read_text(encoding="utf-8")
        st.subheader("Script")
        st.text_area("Generated script", value=script_text, height=420)
        st.download_button(
            "Download script",
            data=script_text,
            file_name=script_file.name,
            mime="text/plain",
        )

    if audio_path:
        audio_file = Path(audio_path)
        audio_bytes = audio_file.read_bytes()
        st.subheader("Audio")
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button(
            "Download MP3",
            data=audio_bytes,
            file_name=audio_file.name,
            mime="audio/mpeg",
        )


if __name__ == "__main__":
    main()
