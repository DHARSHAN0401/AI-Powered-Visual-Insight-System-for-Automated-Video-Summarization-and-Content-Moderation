AI-Powered Visual Insight System for Automated Video Summarization and Content Moderation

Overview
--------
This project demonstrates a modular Python pipeline that:

- detects scene changes, extracts representative keyframes
- runs object detection and image captioning
- transcribes audio using Whisper
- summarizes transcript text using transformers (BART)
- ranks frames with CLIP embeddings and selects relevant clips
- performs basic content moderation (image + speech heuristics)
- creates a short summarized video and outputs reports

Files
-----
- `main.py` - CLI entry point to run the full pipeline
- `app.py` - Streamlit dashboard to upload and inspect results
- `modules/` - Contains modular pipeline components

Quick start
-----------
1. Create a virtualenv and install requirements:

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r "D:/maj pro/project/requirements.txt"
```

2. Run the pipeline on a video:

```pwsh
python "D:/maj pro/project/main.py" --input "path\to\video.mp4"
```

3. Launch the Streamlit UI:

```pwsh
streamlit run "D:/maj pro/project/app.py"
```

Notes
-----
- The modules lazily load heavy models (YOLOv8, Whisper, CLIP, BLIP) and will download weights on first run. Ensure you have network access and enough disk space.
- ffmpeg is required on PATH for some operations (moviepy/ffmpeg backend).
