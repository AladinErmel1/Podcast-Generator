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
3. Add an environment variable named `OPENAI_API_KEY`.
4. Optional: add `APP_PASSWORD` to limit access, or `MAX_UPLOAD_MB` to change the upload limit.
5. Deploy.

Railway uses the included `Procfile`, `railway.json`, and `nixpacks.toml`.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Create a `.env` file first:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```
