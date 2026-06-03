# Overview

This project generates source-grounded podcasts from documents.

Pipeline:

1. Extract text from PDF, TXT, or DOCX.
2. Chunk the source text.
3. Summarize source-grounded notes.
4. Generate a Mike/Sarah script section by section.
5. Validate word count for the selected duration.
6. Repair the script if it is too short or too long.
7. Optionally render audio with chunked text-to-speech.
8. Combine MP3 segments into one output file.

Duration presets are 5, 10, 15, and 20 minutes. The word target is `duration * 150`, with a plus or minus 10 percent tolerance before audio generation.

Primary entry points:

- Web app: `streamlit run app.py`
- CLI: `python run_podcast_generation.py --input <file> --duration 15`
- Library: `PodcastGenerator.create_podcast(...)`

