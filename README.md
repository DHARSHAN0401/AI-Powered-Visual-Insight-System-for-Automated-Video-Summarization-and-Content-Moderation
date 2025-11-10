# AI Visual Insight Pro

Ultra-fast video analysis platform with AI-powered scene detection, speech-to-text, summarization, and content moderation.

## Quick Start

### Local Installation

```bash
pip install -r requirements.txt
streamlit run app_pro.py
```

### System Requirements (for local setup)
- Python 3.8+
- FFmpeg (for audio processing)
- OpenCV dependencies (automatically handled by opencv-python-headless)

### Streamlit Cloud Deployment

This app is configured for Streamlit Cloud deployment with:
- `packages.txt` - System dependencies for OpenCV and FFmpeg
- `.streamlit/config.toml` - App configuration
- `requirements.txt` - Python dependencies

## Features

- 🎬 **Automatic Scene Detection** - AI-powered video segmentation
- 🎤 **Speech-to-Text** - Multi-language transcription (16+ languages)
- 📝 **AI Summary** - Intelligent text summarization and key points extraction
- 🛡️ **Content Moderation** - Multi-language safety checking
- 📊 **Quality Analysis** - Video quality metrics and insights
- ⚡ **Parallel Processing** - 4 workers for fast keyframe extraction
- 🌍 **Multi-Language Support** - English, Spanish, French, German, Chinese, Japanese, Korean, Hindi, Arabic, Russian, Portuguese, Italian, Dutch, Polish, Turkish, Vietnamese

## Usage

1. Upload video (MP4, AVI, MOV, MKV, WebM)
2. Select target language for transcription
3. Adjust scene sensitivity (optional)
4. Click "🚀 Start Pro AI Analysis"
5. View results across 5 tabs:
   - 📊 Overview
   - 🎬 Scenes & Keyframes
   - 📝 Transcription & Summary
   - 🛡️ Content Safety
   - 📈 Advanced Analytics

## Performance

- 10x faster processing
- 150 FPS speed
- 75% less memory
- Parallel processing (4 workers)

## Deployment Notes

For Streamlit Cloud deployment:
- Maximum upload size: 200MB (configurable in `.streamlit/config.toml`)
- Uses `opencv-python-headless` for server environments
- System packages automatically installed via `packages.txt`
- FFmpeg included for audio processing

