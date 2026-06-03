# AI Podcast Generator

Turn a PDF, TXT, or DOCX document into a two-speaker podcast.

There are two ways to use this project.

## Option 1: Use The Streamlit App

Use this option if you only want to generate a podcast.

1. Open the app:

```text
https://podcast-generatorgit-3lfrcezzxvhrwt2nfpkup3.streamlit.app/
```

2. Enter your OpenAI API key.
3. Upload a PDF, TXT, or DOCX document.
4. Choose a podcast length: 5, 10, 15, or 20 minutes.
5. Optional: change the two host names and voices.
6. Optional: preview the voices.
7. Click **Generate**.
8. Download the script or MP3.

Your API key is used only for the current app session and is not saved by the app.

## Option 2: Use The GitHub Project

Use this option if you want to run or modify the app yourself.

1. Open this repository on GitHub.
2. Download or clone the repository.
3. Open a terminal and run:

```bash
git clone https://github.com/AladinErmel1/Podcast-Generator.git
cd Podcast-Generator
python -m pip install -r requirements.txt
streamlit run app.py
```

4. Open the local Streamlit URL shown in your terminal.
5. Follow the same app steps from Option 1.

The GitHub project contains the source code, app configuration, and generator logic.

## What It Creates

- A source-grounded podcast script.
- A natural conversation between two hosts.
- Optional MP3 audio.
