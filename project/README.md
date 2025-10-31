# 🎬 AI-Powered Visual Insight System

**Automated Video Summarization and Content Moderation using Deep Learning**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

A comprehensive AI-powered system that automatically analyzes videos to generate intelligent summaries and perform content moderation. Uses state-of-the-art deep learning models for:

- 🎥 **Scene Detection** - Automatically identify scene boundaries
- 🖼️ **Keyframe Extraction** - Select representative frames
- 🔍 **Object Detection** - YOLOv8 for object recognition
- 💬 **Image Captioning** - BLIP for visual understanding  
- 🗣️ **Speech Transcription** - Whisper for audio-to-text
- 📝 **Text Summarization** - Transformer models (BART/Pegasus)
- 🎨 **Visual Ranking** - CLIP embeddings for relevance
- 🛡️ **Content Moderation** - NSFW & violence detection
- 🎬 **Video Summarization** - Automated highlight generation

## ✨ Features

- ✅ **Multi-Modal Analysis**: Video, audio, and text processing
- ✅ **GPU Acceleration**: CUDA support for faster processing  
- ✅ **Modular Architecture**: Easy to extend and customize
- ✅ **CLI & Web UI**: Command-line and Streamlit interfaces
- ✅ **Progress Tracking**: Real-time progress bars and logging
- ✅ **Batch Processing**: Efficient handling of multiple videos
- ✅ **Comprehensive Reports**: JSON & text output formats

## 📋 Requirements

- Python 3.9+
- FFmpeg (for video/audio processing)
- CUDA-capable GPU (optional, for acceleration)
- 8GB+ RAM recommended
- 5GB+ disk space for models

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd project

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (if not already installed)
# Windows: choco install ffmpeg
# Mac: brew install ffmpeg  
# Linux: sudo apt-get install ffmpeg
```

### Basic Usage

```bash
# Process a video (CLI)
python main.py --input sample_video.mp4

# With GPU acceleration
python main.py --input sample_video.mp4 --gpu

# Custom output directory and scene limit
python main.py --input video.mp4 --output results --max-scenes 10

# Launch Web UI
streamlit run app.py
```

## 📁 Project Structure

```
project/
├── main.py                      # Main pipeline orchestrator
├── app.py                       # Streamlit web interface
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── modules/                     # Core processing modules
│   ├── __init__.py
│   ├── video_preprocessor.py    # Scene detection, audio extraction
│   ├── keyframe_extractor.py    # Keyframe selection
│   ├── detection_captioning.py  # YOLO + BLIP + CLIP
│   ├── speech_transcriber.py    # Whisper speech-to-text
│   ├── summarizer.py            # Text summarization (BART)
│   ├── moderator.py             # Content moderation (NudeNet)
│   ├── summarizer_video.py      # Video compilation
│   └── utils.py                 # Helper functions
│
└── outputs/                     # Generated outputs
    └── <session-id>/
        ├── summary.mp4          # Summary video
        ├── summary.txt          # Text summary
        ├── transcript.txt       # Full transcript
        ├── moderation_report.json
        ├── storyboard_metadata.json
        └── storyboard/          # Keyframe images
```

## 🎯 Pipeline Stages

### 1. Video Preprocessing
- Extract audio stream
- Detect scene changes using content analysis
- Normalize video format

### 2. Keyframe Extraction  
- Select representative frame from each scene
- Save high-quality keyframes to disk

### 3. Visual Analysis
- **Object Detection**: YOLOv8 identifies objects
- **Image Captioning**: BLIP generates descriptions
- **CLIP Embeddings**: Semantic understanding

### 4. Audio Processing
- Whisper model transcribes speech
- Segment-level timestamp alignment
- Multi-language support

### 5. Text Summarization
- Combine transcript + image captions
- BART/Pegasus transformer summarization
- Extractive + abstractive approaches

### 6. Content Moderation
- NSFW image detection (NudeNet)
- Violence/weapon detection (YOLO)
- Profanity filtering in transcripts
- Timestamp-accurate flagging

### 7. Video Summary Creation
- Select top N most relevant scenes
- Concatenate clips with transitions
- Generate compact summary video

## 🖥️ Web Interface

Launch the Streamlit UI:

```bash
streamlit run app.py
```

Features:
- 📤 Video upload interface
- 👁️ Real-time processing status
- 🎬 Interactive video player
- 📊 Moderation report visualization
- 💾 Download results

## 🔧 Configuration

### Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  -i, --input PATH          Input video file (required)
  -o, --output PATH         Output directory (default: outputs)
  --max-scenes INT          Max scenes in summary (default: 6)
  --scene-threshold FLOAT   Scene sensitivity (default: 30.0)
  --gpu                     Enable GPU acceleration
  -v, --verbose             Verbose logging
  -h, --help                Show help message
```

### Environment Variables

Create `.env` file:

```bash
# GPU Settings
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Model Cache
TRANSFORMERS_CACHE=./models/cache
TORCH_HOME=./models/torch

# Logging
LOG_LEVEL=INFO
```

## 📊 Output Files

Each processing session creates:

- `summary.mp4` - Short highlight video
- `summary.txt` - Text summary (~200 words)
- `transcript.txt` - Full speech transcript
- `moderation_report.json` - Content flags & timestamps
- `storyboard_metadata.json` - Scene & detection data
- `storyboard/*.jpg` - Extracted keyframes

## 🧪 Example

```bash
python main.py --input sample.mp4 --gpu --max-scenes 8

# Output:
# ================================================================================
# Session ID: abc123
# Input Video: sample.mp4
# Output Directory: outputs/abc123
# GPU Enabled: True
# ================================================================================
# 📹 Stage 1: Video Preprocessing & Scene Detection
# ✓ Detected 15 scenes
# 🖼️  Stage 2: Keyframe Extraction
# ✓ Extracted 15 keyframes
# 🔍 Stage 3: Object Detection & Image Captioning
# ✓ Processed 15 frames with detection & captioning
# 🎤 Stage 4: Speech-to-Text Transcription
# ✓ Transcribed audio (23 segments)
# 📝 Stage 5: Text Summarization
# ✓ Generated text summary (1842 characters)
# 🛡️  Stage 6: Content Moderation
# ✓ Moderation complete (2 flags detected)
# 🎬 Stage 7: Summary Video Creation
# ✓ Created summary video: outputs/abc123/summary.mp4
# ================================================================================
# ✅ Pipeline Complete!
# 📂 All outputs saved to: outputs/abc123
# ================================================================================
```

## 🔬 Model Details

| Component | Model | Purpose |
|-----------|-------|---------|
| Scene Detection | PySceneDetect | Content-based scene segmentation |
| Object Detection | YOLOv8n | Real-time object recognition |
| Image Captioning | BLIP-base | Visual description generation |
| Visual Embeddings | CLIP ViT-B/32 | Semantic image understanding |
| Speech Recognition | Whisper-base | Audio transcription |
| Text Summarization | BART-large-CNN | Abstractive summarization |
| NSFW Detection | NudeNet | Content safety filtering |

## ⚡ Performance

Approximate processing times (GTX 1080 Ti):

- 1 min video: ~30-45 seconds
- 5 min video: ~2-3 minutes  
- 30 min video: ~10-15 minutes

CPU-only mode is 3-5x slower.

## 🐛 Troubleshooting

### FFmpeg Not Found
```bash
# Install FFmpeg
pip install imageio-ffmpeg
# Or system-wide: apt-get install ffmpeg
```

### CUDA Out of Memory
```bash
# Reduce batch size or use CPU mode
python main.py --input video.mp4  # (no --gpu flag)
```

### Model Download Issues
```bash
# Pre-download models
python -c "from transformers import pipeline; pipeline('summarization')"
python -c "import whisper; whisper.load_model('base')"
```

## 📝 Citation

```bibtex
@software{visual_insight_2024,
  title={AI-Powered Visual Insight System},
  author={Visual Insight Team},
  year={2024},
  url={https://github.com/yourusername/visual-insight}
}
```

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ using PyTorch, Transformers, and Streamlit**
