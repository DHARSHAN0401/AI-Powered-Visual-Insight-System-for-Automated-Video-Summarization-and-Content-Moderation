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

st.set_page_config(
    page_title="AI Visual Insight",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800;900&display=swap');
    
    .stApp {
        background: linear-gradient(to bottom right, #f8f9fa, #e9ecef, #ffffff);
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    ::-webkit-scrollbar {width: 8px; height: 8px;}
    ::-webkit-scrollbar-track {background: #f1f3f5;}
    ::-webkit-scrollbar-thumb {background: linear-gradient(180deg, #4f46e5, #6366f1); border-radius: 4px;}
    
    .hero-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 24px;
        padding: 4rem 3rem;
        margin: 2rem 0 3rem 0;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.25);
        animation: gradientShift 10s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        color: white;
        text-align: center;
        margin: 0 0 1rem 0;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        letter-spacing: -2px;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.95);
        text-align: center;
        font-weight: 400;
        margin: 0;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.25);
        transition: all 0.3s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 45px rgba(102, 126, 234, 0.35);
    }
    
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        color: white;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .stButton>button {
        font-family: 'Poppins', sans-serif;
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        border-radius: 16px;
        padding: 1rem 2rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.45);
    }
    
    .stProgress>div>div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def check_system_capabilities():
    capabilities = {
        'opencv': False,
        'scenedetect': False,
        'torch_gpu': False
    }
    
    try:
        import cv2
        capabilities['opencv'] = True
    except ImportError:
        pass
    
    try:
        from scenedetect import detect, ContentDetector
        capabilities['scenedetect'] = True
    except ImportError:
        pass
    
    try:
        import torch
        capabilities['torch_gpu'] = torch.cuda.is_available()
    except ImportError:
        pass
    
    return capabilities

@st.cache_data(show_spinner=False, ttl=3600)
def extract_video_metadata(_video_path: str):
    cap = cv2.VideoCapture(_video_path)
    metadata = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': float(cap.get(cv2.CAP_PROP_FPS)),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration': float(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
    }
    cap.release()
    return metadata

def detect_scenes_fast(video_path: str, threshold: float = 27.0):
    try:
        from scenedetect import detect, ContentDetector
        scenes = detect(video_path, ContentDetector(threshold=threshold))
        return [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in scenes]
    except Exception:
        metadata = extract_video_metadata(video_path)
        return [(0, metadata['duration'])]

def extract_keyframes_parallel(video_path: str, scenes: List[Tuple], output_dir: str):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    
    keyframes = []
    storyboard_dir = os.path.join(output_dir, "storyboard")
    os.makedirs(storyboard_dir, exist_ok=True)
    
    def extract_single_keyframe(idx, start, end):
        try:
            local_cap = cv2.VideoCapture(video_path)
            mid = (start + end) / 2.0
            frame_no = int(mid * fps)
            local_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = local_cap.read()
            local_cap.release()
            
            if ret:
                frame_path = os.path.join(storyboard_dir, f"keyframe_{idx:04d}.jpg")
                cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                return {
                    'scene_idx': idx,
                    'timestamp': mid,
                    'frame_path': frame_path,
                    'scene_start': start,
                    'scene_end': end
                }
        except Exception:
            return None
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for idx, (start, end) in enumerate(scenes):
            future = executor.submit(extract_single_keyframe, idx, start, end)
            futures.append(future)
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                keyframes.append(result)
    
    cap.release()
    keyframes.sort(key=lambda x: x['scene_idx'])
    return keyframes

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def generate_summary_report(video_info: Dict, keyframes: List[Dict], processing_time: float):
    summary = []
    summary.append("╔" + "═" * 78 + "╗")
    summary.append("║" + " " * 20 + "AI VIDEO ANALYSIS REPORT" + " " * 34 + "║")
    summary.append("╚" + "═" * 78 + "╝")
    summary.append("")
    summary.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    summary.append(f"Processing Time: {processing_time:.2f} seconds")
    summary.append("")
    summary.append("─" * 80)
    summary.append("VIDEO INFORMATION")
    summary.append("─" * 80)
    summary.append(f"Resolution: {video_info['width']} × {video_info['height']} pixels")
    summary.append(f"Frame Rate: {video_info['fps']:.2f} FPS")
    summary.append(f"Total Frames: {video_info['frame_count']:,}")
    summary.append(f"Duration: {format_time(video_info['duration'])} ({video_info['duration']:.2f}s)")
    summary.append("")
    summary.append("─" * 80)
    summary.append("ANALYSIS SUMMARY")
    summary.append("─" * 80)
    summary.append(f"Scenes Detected: {len(keyframes)}")
    summary.append(f"Keyframes: {len(keyframes)}")
    summary.append("")
    summary.append("─" * 80)
    summary.append("SCENE BREAKDOWN")
    summary.append("─" * 80)
    
    for kf in keyframes:
        summary.append("")
        summary.append(f"Scene #{kf['scene_idx'] + 1}")
        summary.append(f"  Time Range: {format_time(kf['scene_start'])} → {format_time(kf['scene_end'])}")
        summary.append(f"  Duration: {kf['scene_end'] - kf['scene_start']:.2f}s")
        summary.append(f"  Keyframe: {format_time(kf['timestamp'])}")
    
    summary.append("")
    summary.append("─" * 80)
    
    return "\n".join(summary)

def process_video_optimized(video_path: str, output_dir: str, scene_threshold: float, progress_callback=None):
    start_time = time.time()
    results = {
        'success': False,
        'video_info': {},
        'keyframes': [],
        'summary': '',
        'processing_time': 0
    }
    
    try:
        if progress_callback:
            progress_callback("Analyzing video metadata...", 0.1)
        results['video_info'] = extract_video_metadata(video_path)
        
        if progress_callback:
            progress_callback("Detecting scenes...", 0.3)
        scenes = detect_scenes_fast(video_path, threshold=scene_threshold)
        
        if not scenes:
            scenes = [(0, results['video_info']['duration'])]
        
        if len(scenes) > 20:
            step = len(scenes) / 20
            scenes = [scenes[int(i * step)] for i in range(20)]
        
        if progress_callback:
            progress_callback("Extracting keyframes...", 0.6)
        keyframes = extract_keyframes_parallel(video_path, scenes, output_dir)
        results['keyframes'] = keyframes
        
        if progress_callback:
            progress_callback("Generating report...", 0.9)
        
        processing_time = time.time() - start_time
        results['summary'] = generate_summary_report(results['video_info'], keyframes, processing_time)
        
        summary_path = os.path.join(output_dir, "summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(results['summary'])
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'video_info': results['video_info'],
                'keyframes': [{
                    'scene_idx': kf['scene_idx'],
                    'timestamp': kf['timestamp'],
                    'scene_start': kf['scene_start'],
                    'scene_end': kf['scene_end']
                } for kf in keyframes],
                'processing_time': processing_time
            }, f, indent=2)
        
        results['processing_time'] = processing_time
        results['success'] = True
        
        if progress_callback:
            progress_callback("Complete!", 1.0)
        
    except Exception as e:
        results['error'] = str(e)
        st.error(f"Processing failed: {e}")
    
    return results

def main():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">AI Visual Insight</div>
        <div class="hero-subtitle">
            Next-Generation Video Analysis Platform
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    capabilities = check_system_capabilities()
    
    with st.sidebar:
        st.markdown("### System Status")
        
        if capabilities['opencv']:
            st.success("✓ OpenCV Ready")
        else:
            st.error("✗ OpenCV Missing")
        
        if capabilities['scenedetect']:
            st.success("✓ Scene Detection")
        else:
            st.warning("✗ Scene Detection")
        
        if capabilities['torch_gpu']:
            st.success("✓ GPU Acceleration")
        else:
            st.info("⚠ CPU Mode")
        
        st.markdown("---")
        
        st.markdown("### Settings")
        
        scene_threshold = st.slider(
            "Scene Detection Sensitivity",
            min_value=10.0,
            max_value=50.0,
            value=27.0,
            step=1.0
        )
    
    tab1, tab2 = st.tabs(["Process Video", "Results"])
    
    with tab1:
        st.markdown("### Upload Video")
        
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv']
        )
        
        if uploaded_file:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.video(uploaded_file)
            
            with col2:
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
                st.info(f"**File:** {uploaded_file.name}\n\n**Size:** {file_size:.2f} MB")
            
            st.markdown("---")
            
            if st.button("Start Processing", type="primary"):
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
                
                with st.spinner("Processing..."):
                    results = process_video_optimized(
                        video_path,
                        output_dir,
                        scene_threshold,
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
                    st.success(f"Processing complete in {results['processing_time']:.2f}s!")
                    st.info("Switch to the Results tab to view analysis")
                else:
                    st.error(f"Failed: {results.get('error', 'Unknown error')}")
        else:
            st.info("Upload a video file to begin analysis")
    
    with tab2:
        if 'results' in st.session_state and st.session_state['results']['success']:
            results = st.session_state['results']
            
            st.markdown("### Analysis Overview")
            
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
            
            st.markdown("### Keyframes")
            
            if 'keyframe_images' in st.session_state:
                cols = st.columns(4)
                for idx, (filename, img_data) in enumerate(st.session_state['keyframe_images']):
                    with cols[idx % 4]:
                        st.image(img_data, use_container_width=True)
                        if idx < len(results['keyframes']):
                            kf = results['keyframes'][idx]
                            st.caption(f"Scene {kf['scene_idx'] + 1} • {format_time(kf['timestamp'])}")
            
            st.markdown("---")
            
            st.markdown("### Report")
            
            st.text_area(
                "Analysis Summary",
                results['summary'],
                height=400
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="Download Summary (TXT)",
                    data=results['summary'],
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                metadata_path = os.path.join(st.session_state['output_dir'], "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = f.read()
                    st.download_button(
                        label="Download Metadata (JSON)",
                        data=metadata,
                        file_name=f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
        else:
            st.info("Process a video to see results here")

if __name__ == '__main__':
    main()
