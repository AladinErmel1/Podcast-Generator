# AI Podcast Generator

Turn a PDF, TXT, or DOCX document into a two-speaker podcast with Sarah and Mike.

## Features

- Upload a document in the browser.
- Choose 5, 10, 15, or 20 minutes.
- Generate a source-grounded script.
- Create downloadable MP3 audio.

## Deploy On Railway

1. Push this repo to GitHub.
2. Create a new Railway project from the GitHub repo.
3. Deploy.

By default, each user enters their own OpenAI API key in the app.

Optional environment variables:

- `OPENAI_API_KEY`: use one shared server key instead of asking each user.
- `APP_PASSWORD`: limit access to the app.
- `MAX_UPLOAD_MB`: change the upload limit.

Railway uses the included `Procfile`, `railway.json`, and `nixpacks.toml`.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The `.env` file is optional. If you skip it, the app asks for an API key in the browser.

```bash
OPENAI_API_KEY=your_openai_api_key_here
```
