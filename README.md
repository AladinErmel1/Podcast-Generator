# AI Podcast Generator

Turn a PDF, TXT, or DOCX document into a two-speaker podcast with Sarah and Mike.

## Features

- Upload a document in the browser.
- Choose 5, 10, 15, or 20 minutes.
- Generate a source-grounded script.
- Create downloadable MP3 audio.
- Let each user enter their own OpenAI API key.

## Deploy On Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create a new app from this repo.
3. Set the app entry point to `app.py`.
4. Deploy.

The app uses:

- `requirements.txt` for Python dependencies.
- `packages.txt` for `ffmpeg`, which is needed for MP3 assembly.

By default, users enter their own OpenAI API key in the app. If you prefer one shared key, add `OPENAI_API_KEY` in Streamlit secrets. You can also add `APP_PASSWORD` to limit access or `MAX_UPLOAD_MB` to change the upload limit.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The `.env` file is optional. If you skip it, the app asks for an API key in the browser.

