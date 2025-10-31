import streamlit as st
import cv2
import os
import sys
import json
import time
import tempfile
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import hashlib

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from project.modules.video_preprocessor import VideoPreprocessor
from project.modules.keyframe_extractor import KeyframeExtractor
from project.modules.detection_captioning import DetectorCaptioner
from project.modules.speech_transcriber import SpeechTranscriber
from project.modules.summarizer import TextSummarizer
from project.modules.moderator import Moderator
from project.modules.summarizer_video import VideoSummarizer

st.set_page_config(
    page_title="AI Visual Insight Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800;900&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    ::-webkit-scrollbar {width: 10px; height: 10px;}
    ::-webkit-scrollbar-track {background: rgba(255,255,255,0.1);}
    ::-webkit-scrollbar-thumb {background: linear-gradient(180deg, #4f46e5, #6366f1); border-radius: 5px;}
    
    .hero-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 24px;
        padding: 4rem 3rem;
        margin: 2rem 0 3rem 0;
        box-shadow: 0 30px 80px rgba(102, 126, 234, 0.4);
        animation: gradientShift 8s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 4px 12px rgba(0,0,0,0.3);
        letter-spacing: -2px;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 500;
        color: rgba(255,255,255,0.95);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }
    
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        font-family: 'Poppins', sans-serif;
    }
    
    .metric-label {
        font-size: 1rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem;
        box-shadow: 0 5px 15px rgba(245, 87, 108, 0.3);
    }
    
    .detection-box {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        border-radius: 16px;
        padding: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
    }
    
    .stButton>button {
        width: 100%;
        height: 60px;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
    }
</style>
""", unsafe_allow_html=True)

def format_duration(seconds: float) -> str:
    td = timedelta(seconds=int(seconds))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def check_system_capabilities():
    import torch
    has_gpu = torch.cuda.is_available()
    return {
        'gpu_available': has_gpu,
        'gpu_name': torch.cuda.get_device_name(0) if has_gpu else None,
        'cpu_count': os.cpu_count()
    }

def extract_video_metadata(video_path: str) -> Dict:
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    cap.release()
    return {
        'fps': fps,
        'frame_count': frame_count,
        'width': width,
        'height': height,
        'duration': duration,
        'resolution': f"{width}x{height}"
    }

def process_video_advanced(
    video_path: str,
    output_dir: str,
    scene_threshold: float = 27.0,
    use_gpu: bool = False,
    enable_detection: bool = True,
    enable_transcription: bool = True,
    enable_summarization: bool = True,
    enable_moderation: bool = True,
    progress_callback=None
):
    start_time = time.time()
    results = {
        'success': False,
        'video_info': {},
        'scenes': [],
        'keyframes': [],
        'detections': [],
        'captions': [],
        'transcript': '',
        'summary': '',
        'moderation': {},
        'processing_time': 0
    }
    
    try:
        if progress_callback:
            progress_callback("Extracting video metadata...", 0.05)
        
        video_info = extract_video_metadata(video_path)
        results['video_info'] = video_info
        
        if progress_callback:
            progress_callback("Detecting scenes...", 0.15)
        
        preprocessor = VideoPreprocessor(output_dir)
        scenes = preprocessor.detect_scenes(video_path, threshold=scene_threshold)
        results['scenes'] = scenes
        
        if progress_callback:
            progress_callback("Extracting keyframes...", 0.30)
        
        extractor = KeyframeExtractor(output_dir)
        keyframes = extractor.extract_keyframes(video_path, scenes)
        results['keyframes'] = keyframes
        
        if enable_detection and keyframes:
            if progress_callback:
                progress_callback("Running AI detection & captioning...", 0.45)
            
            detector = DetectorCaptioner(use_gpu=use_gpu)
            det_results = detector.process_keyframes(keyframes)
            results['detections'] = det_results
            
            results['captions'] = [
                {'scene_idx': r['scene_idx'], 'caption': r['caption']}
                for r in det_results
            ]
        
        if enable_transcription:
            if progress_callback:
                progress_callback("Transcribing audio...", 0.60)
            
            audio_path = preprocessor.extract_audio(video_path)
            if audio_path and os.path.exists(audio_path):
                transcriber = SpeechTranscriber(use_gpu=use_gpu)
                transcript, segments = transcriber.transcribe(audio_path)
                results['transcript'] = transcript
                results['transcript_segments'] = segments
        
        if enable_summarization and results['transcript']:
            if progress_callback:
                progress_callback("Generating summary...", 0.75)
            
            summarizer = TextSummarizer(use_gpu=use_gpu)
            summary = summarizer.summarize(results['transcript'])
            results['summary'] = summary
        
        if enable_moderation:
            if progress_callback:
                progress_callback("Running content moderation...", 0.85)
            
            moderator = Moderator(use_gpu=use_gpu)
            mod_results = moderator.moderate(
                results.get('detections', []),
                results.get('transcript_segments', [])
            )
            results['moderation'] = mod_results
        
        if progress_callback:
            progress_callback("Finalizing results...", 0.95)
        
        metadata_path = os.path.join(output_dir, "analysis.json")
        with open(metadata_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        results['success'] = True
        results['processing_time'] = time.time() - start_time
        
        if progress_callback:
            progress_callback("Complete!", 1.0)
        
    except Exception as e:
        results['error'] = str(e)
        st.error(f"Processing error: {e}")
    
    return results

def main():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🚀 AI Visual Insight Pro</div>
        <div class="hero-subtitle">Advanced Video Analysis with Deep Learning</div>
        <div style="text-align: center;">
            <span class="ai-badge">🎯 Object Detection</span>
            <span class="ai-badge">🎤 Speech Recognition</span>
            <span class="ai-badge">📝 Auto Summarization</span>
            <span class="ai-badge">🛡️ Content Moderation</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        sys_info = check_system_capabilities()
        
        if sys_info['gpu_available']:
            st.success(f"🚀 GPU: {sys_info['gpu_name']}")
            use_gpu = st.checkbox("Enable GPU Acceleration", value=True)
        else:
            st.warning("💻 CPU Mode")
            use_gpu = False
        
        st.markdown("---")
        st.markdown("### 🎬 Scene Detection")
        scene_threshold = st.slider("Sensitivity", 10.0, 50.0, 27.0, 1.0)
        
        st.markdown("---")
        st.markdown("### 🤖 AI Features")
        enable_detection = st.checkbox("Object Detection & Captioning", value=True)
        enable_transcription = st.checkbox("Speech Transcription", value=True)
        enable_summarization = st.checkbox("Text Summarization", value=True)
        enable_moderation = st.checkbox("Content Moderation", value=True)
        
        st.markdown("---")
        st.markdown("### 📊 System")
        st.info(f"CPU Cores: {sys_info['cpu_count']}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📊 Results", "🤖 AI Analysis", "🛡️ Moderation"])
    
    with tab1:
        st.markdown("### Upload Video")
        
        uploaded_file = st.file_uploader(
            "Drop your video file here",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Supported: MP4, AVI, MOV, MKV"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.video(uploaded_file)
            
            with col2:
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
                st.info(f"**File:** {uploaded_file.name}\n\n**Size:** {file_size:.2f} MB")
            
            st.markdown("---")
            
            if st.button("🚀 Start Advanced Processing", type="primary"):
                if 'temp_dir' not in st.session_state:
                    st.session_state['temp_dir'] = tempfile.mkdtemp()
                
                temp_dir = st.session_state['temp_dir']
                video_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(video_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                output_dir = os.path.join(temp_dir, "outputs")
                os.makedirs(output_dir, exist_ok=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(msg, pct):
                    status_text.markdown(f"**{msg}**")
                    progress_bar.progress(pct)
                
                with st.spinner("Processing with AI..."):
                    results = process_video_advanced(
                        video_path,
                        output_dir,
                        scene_threshold,
                        use_gpu,
                        enable_detection,
                        enable_transcription,
                        enable_summarization,
                        enable_moderation,
                        progress_callback=update_progress
                    )
                
                if results['success']:
                    st.session_state['results'] = results
                    st.session_state['output_dir'] = output_dir
                    
                    keyframe_images = []
                    storyboard_dir = os.path.join(output_dir, "storyboard")
                    if os.path.exists(storyboard_dir):
                        for filename in sorted(os.listdir(storyboard_dir)):
                            if filename.endswith('.jpg'):
                                filepath = os.path.join(storyboard_dir, filename)
                                with open(filepath, 'rb') as f:
                                    keyframe_images.append((filename, f.read()))
                    st.session_state['keyframe_images'] = keyframe_images
                    
                    st.balloons()
                    st.success(f"✅ Processing complete in {results['processing_time']:.2f}s!")
                    st.info("🎯 Check Results & AI Analysis tabs")
                else:
                    st.error(f"❌ Failed: {results.get('error', 'Unknown error')}")
        else:
            st.info("📁 Upload a video file to begin")
    
    with tab2:
        if 'results' in st.session_state and st.session_state['results']['success']:
            results = st.session_state['results']
            
            st.markdown("### 📊 Analysis Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{len(results['keyframes'])}</div>
                    <div class="metric-label">Scenes</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{format_duration(results['video_info']['duration'])}</div>
                    <div class="metric-label">Duration</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{results['video_info']['fps']:.0f}</div>
                    <div class="metric-label">FPS</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{results['processing_time']:.1f}s</div>
                    <div class="metric-label">Process Time</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🎬 Keyframes")
            
            if 'keyframe_images' in st.session_state:
                cols = st.columns(4)
                for idx, (filename, img_data) in enumerate(st.session_state['keyframe_images']):
                    with cols[idx % 4]:
                        img = Image.open(io.BytesIO(img_data))
                        st.image(img, caption=f"Scene {idx}", use_container_width=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📥 Download Analysis JSON",
                    data=json.dumps(results, indent=2, default=str),
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                if 'output_dir' in st.session_state:
                    st.info(f"📁 Output: {st.session_state['output_dir']}")
        else:
            st.info("⚠️ No results yet. Process a video first.")
    
    with tab3:
        if 'results' in st.session_state and st.session_state['results']['success']:
            results = st.session_state['results']
            
            st.markdown("### 🤖 AI-Powered Analysis")
            
            if results.get('detections'):
                st.markdown("#### 🎯 Object Detection & Captions")
                for det in results['detections'][:10]:
                    with st.expander(f"Scene {det['scene_idx']} @ {det['timestamp']:.1f}s"):
                        st.markdown(f"**Caption:** {det.get('caption', 'N/A')}")
                        
                        if det.get('detections'):
                            st.markdown("**Detected Objects:**")
                            for obj in det['detections'][:5]:
                                st.markdown(f"""
                                <div class="detection-box">
                                    <strong>{obj['class_name']}</strong> - Confidence: {obj['conf']:.2%}
                                </div>
                                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            if results.get('transcript'):
                st.markdown("#### 🎤 Speech Transcript")
                st.text_area("Full Transcript", results['transcript'], height=200)
            
            st.markdown("---")
            
            if results.get('summary'):
                st.markdown("#### 📝 Auto-Generated Summary")
                st.success(results['summary'])
        else:
            st.info("⚠️ No AI analysis yet. Enable AI features and process a video.")
    
    with tab4:
        if 'results' in st.session_state and st.session_state['results'].get('moderation'):
            mod = st.session_state['results']['moderation']
            
            st.markdown("### 🛡️ Content Moderation Report")
            
            summary = mod.get('summary', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nsfw_status = "⚠️ Flagged" if summary.get('has_nsfw_content') else "✅ Clean"
                st.metric("NSFW Content", nsfw_status)
            
            with col2:
                violence_status = "⚠️ Detected" if summary.get('has_violence_content') else "✅ None"
                st.metric("Violence", violence_status)
            
            with col3:
                profanity_status = "⚠️ Found" if summary.get('has_profanity') else "✅ Clean"
                st.metric("Profanity", profanity_status)
            
            st.markdown("---")
            
            if mod.get('image_flags'):
                st.markdown("#### 🚨 Image Flags")
                for flag in mod['image_flags'][:5]:
                    st.warning(f"Scene {flag['scene_idx']} @ {flag['timestamp']:.1f}s - {flag['reason']}")
            
            if mod.get('text_flags'):
                st.markdown("#### 🚨 Text Flags")
                for flag in mod['text_flags'][:5]:
                    st.warning(f"{flag['start']:.1f}s - {flag['end']:.1f}s: {flag.get('words', [])}")
        else:
            st.info("⚠️ No moderation data. Enable moderation and process a video.")

if __name__ == "__main__":
    import io
    main()
