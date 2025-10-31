"""
AI-Powered Visual Insight System - Streamlit Cloud Deployment
Web interface for video summarization and content analysis
"""

import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="AI Video Summarization",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def check_dependencies():
    """Check which dependencies are installed"""
    deps = {}
    required = {
        'cv2': 'OpenCV',
        'scenedetect': 'PySceneDetect',
        'PIL': 'Pillow',
        'numpy': 'NumPy',
    }
    
    for module, name in required.items():
        try:
            __import__(module)
            deps[name] = True
        except ImportError:
            deps[name] = False
    
    return deps

def process_video_basic(video_path, output_dir, max_scenes=8, threshold=30.0):
    """Process video with scene detection and summarization"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        import cv2
        from scenedetect import detect, ContentDetector
        import numpy as np
        from PIL import Image
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        storyboard_dir = os.path.join(output_dir, "storyboard")
        os.makedirs(storyboard_dir, exist_ok=True)
        
        # Step 1: Get video info
        status_text.text("📹 Opening video file...")
        progress_bar.progress(10)
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        video_info = {
            'fps': fps,
            'frame_count': frame_count,
            'duration': duration,
            'width': width,
            'height': height
        }
        
        # Step 2: Detect scenes
        status_text.text("🔍 Detecting scenes in video...")
        progress_bar.progress(20)
        
        scenes = detect(video_path, ContentDetector(threshold=threshold))
        
        if not scenes:
            status_text.text("⚠️ No scenes detected, using full video")
            scenes = [(0, frame_count)]
        
        # Limit scenes
        if len(scenes) > max_scenes:
            # Select evenly distributed scenes
            step = len(scenes) / max_scenes
            selected_indices = [int(i * step) for i in range(max_scenes)]
            scenes = [scenes[i] for i in selected_indices]
        
        status_text.text(f"✅ Detected {len(scenes)} scenes")
        progress_bar.progress(40)
        
        # Step 3: Extract keyframes
        status_text.text("🖼️ Extracting keyframes...")
        progress_bar.progress(50)
        
        cap = cv2.VideoCapture(video_path)
        keyframes = []
        
        for idx, scene in enumerate(scenes):
            # Get middle frame of scene
            start_frame = int(scene[0].get_frames()) if hasattr(scene[0], 'get_frames') else scene[0]
            end_frame = int(scene[1].get_frames()) if hasattr(scene[1], 'get_frames') else scene[1]
            middle_frame = (start_frame + end_frame) // 2
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            ret, frame = cap.read()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Save keyframe
                keyframe_path = os.path.join(storyboard_dir, f"keyframe_{idx:03d}.jpg")
                Image.fromarray(frame_rgb).save(keyframe_path, quality=85)
                
                start_time = start_frame / fps if fps > 0 else 0
                end_time = end_frame / fps if fps > 0 else 0
                
                keyframes.append({
                    'index': idx,
                    'path': keyframe_path,
                    'timestamp': middle_frame / fps if fps > 0 else 0,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time
                })
            
            progress_bar.progress(50 + int((idx + 1) / len(scenes) * 30))
        
        cap.release()
        status_text.text(f"✅ Extracted {len(keyframes)} keyframes")
        progress_bar.progress(80)
        
        # Step 4: Generate summary
        status_text.text("📝 Generating summary...")
        progress_bar.progress(85)
        
        summary_text = f"""AI Video Analysis Summary
{'=' * 50}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

VIDEO INFORMATION:
- Resolution: {width}x{height}
- Frame Rate: {fps:.2f} fps
- Total Frames: {frame_count}
- Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)

ANALYSIS RESULTS:
- Total Scenes Detected: {len(scenes)}
- Keyframes Extracted: {len(keyframes)}
- Processing Mode: Basic Scene Detection

SCENE BREAKDOWN:
{'=' * 50}
"""
        
        for kf in keyframes:
            summary_text += f"""
Scene {kf['index'] + 1}:
  Time Range: {kf['start_time']:.2f}s - {kf['end_time']:.2f}s
  Duration: {kf['duration']:.2f}s
  Keyframe: {kf['timestamp']:.2f}s
  Status: Processed ✓
"""
        
        summary_text += f"""
{'=' * 50}

NEXT STEPS:
To enable advanced AI features (object detection, image captioning, 
speech transcription), install additional models:
- YOLOv8 for object detection
- BLIP for image captioning  
- Whisper for speech-to-text
- BART for text summarization

{'=' * 50}
End of Report
"""
        
        # Save summary
        summary_path = os.path.join(output_dir, "summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        
        # Save metadata
        metadata = {
            'video_info': video_info,
            'scenes_detected': len(scenes),
            'keyframes_extracted': len(keyframes),
            'keyframes': keyframes,
            'timestamp': datetime.now().isoformat(),
            'processing_mode': 'basic'
        }
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        status_text.text("✅ Processing complete!")
        progress_bar.progress(100)
        
        return {
            'success': True,
            'video_info': video_info,
            'scenes': len(scenes),
            'keyframes': keyframes,
            'summary': summary_text,
            'metadata': metadata
        }
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        status_text.text(f"❌ Error: {str(e)}")
        return {'success': False, 'error': error_msg}

def main():
    # Header
    st.markdown('<h1 class="main-header">🎬 AI-Powered Visual Insight System</h1>', unsafe_allow_html=True)
    st.markdown("### Automated Video Summarization and Content Analysis")
    
    # Check dependencies
    deps = check_dependencies()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - 🎥 Scene Detection
        - 🖼️ Keyframe Extraction
        - 📝 Summary Generation
        - 📊 Metadata Export
        
        **Advanced Features** (coming soon):
        - 🔍 Object Detection
        - 💬 Image Captioning
        - 🎤 Speech Transcription
        - 🛡️ Content Moderation
        """)
        
        st.markdown("---")
        st.markdown("### 📦 System Status")
        
        all_installed = all(deps.values())
        
        for name, installed in deps.items():
            status = "✅" if installed else "❌"
            st.markdown(f"{status} {name}")
        
        if all_installed:
            st.success("✅ All dependencies ready!")
        else:
            st.warning("⚠️ Some dependencies missing")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📊 Results", "ℹ️ About"])
    
    with tab1:
        st.markdown("## Upload Video")
        
        # Check if dependencies are available
        if not deps.get('OpenCV', False):
            st.error("❌ OpenCV is not installed. Cannot process videos.")
            st.info("This app requires opencv-python-headless to function.")
            st.stop()
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Upload a video file to analyze"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.video(uploaded_file)
                st.success(f"✅ Video uploaded: {uploaded_file.name}")
                st.info(f"📦 Size: {uploaded_file.size / 1024 / 1024:.1f} MB")
            
            with col2:
                st.markdown("### ⚙️ Settings")
                
                max_scenes = st.slider("Max scenes", 3, 15, 8, 
                    help="Maximum number of scenes to extract")
                scene_threshold = st.slider("Scene sensitivity", 10.0, 50.0, 30.0,
                    help="Lower = more sensitive to scene changes")
            
            st.markdown("---")
            
            # Process button
            if st.button("🚀 Process Video", type="primary", use_container_width=True):
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Save uploaded file
                    video_path = os.path.join(tmpdir, uploaded_file.name)
                    with open(video_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Create output directory
                    output_dir = os.path.join(tmpdir, "outputs")
                    
                    # Process video
                    with st.spinner("Processing video..."):
                        result = process_video_basic(video_path, output_dir, max_scenes, scene_threshold)
                    
                    if result['success']:
                        st.session_state['result'] = result
                        st.session_state['output_dir'] = output_dir
                        
                        # Copy files to persistent location (in-memory for cloud)
                        storyboard_files = []
                        storyboard_dir = os.path.join(output_dir, "storyboard")
                        if os.path.exists(storyboard_dir):
                            for fname in os.listdir(storyboard_dir):
                                fpath = os.path.join(storyboard_dir, fname)
                                with open(fpath, 'rb') as f:
                                    storyboard_files.append((fname, f.read()))
                        
                        st.session_state['storyboard_files'] = storyboard_files
                        
                        st.balloons()
                        st.success("🎉 Video processing complete! Check the Results tab.")
                        st.rerun()
                    else:
                        st.error(f"❌ Processing failed!")
                        with st.expander("Error Details"):
                            st.code(result.get('error', 'Unknown error'))
        else:
            st.info("👆 Please upload a video file to begin")
    
    with tab2:
        st.markdown("## 📊 Analysis Results")
        
        if 'result' in st.session_state and st.session_state['result']['success']:
            result = st.session_state['result']
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📹 Total Scenes", result['scenes'])
            
            with col2:
                st.metric("🖼️ Keyframes", len(result['keyframes']))
            
            with col3:
                duration = result['video_info']['duration']
                st.metric("⏱️ Duration", f"{duration:.1f}s")
            
            with col4:
                fps = result['video_info']['fps']
                st.metric("🎞️ Frame Rate", f"{fps:.1f} fps")
            
            st.markdown("---")
            
            # Video info
            with st.expander("📹 Video Information", expanded=False):
                info = result['video_info']
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Resolution:** {info['width']}x{info['height']}")
                    st.write(f"**Frame Rate:** {info['fps']:.2f} fps")
                with col2:
                    st.write(f"**Total Frames:** {info['frame_count']:,}")
                    st.write(f"**Duration:** {info['duration']/60:.1f} minutes")
            
            # Keyframe storyboard
            st.markdown("### 🖼️ Keyframe Storyboard")
            
            if 'storyboard_files' in st.session_state:
                cols = st.columns(4)
                for idx, (fname, data) in enumerate(st.session_state['storyboard_files']):
                    with cols[idx % 4]:
                        st.image(data, caption=f"Scene {idx + 1}")
            else:
                st.info("No storyboard images available")
            
            st.markdown("---")
            
            # Text summary
            st.markdown("### 📝 Summary Report")
            st.text_area("Generated Summary", result['summary'], height=400)
            
            # Download buttons
            st.markdown("### 💾 Download Results")
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📄 Download Summary (TXT)",
                    result['summary'],
                    file_name=f"video_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                metadata_json = json.dumps(result['metadata'], indent=2)
                st.download_button(
                    "📊 Download Metadata (JSON)",
                    metadata_json,
                    file_name=f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.info("👈 Process a video first to see results here")
    
    with tab3:
        st.markdown("## About This Project")
        
        st.markdown("""
        ### 🎬 AI-Powered Visual Insight System
        
        An intelligent video analysis platform that automatically processes videos to extract 
        meaningful insights, detect scenes, and generate comprehensive summaries.
        
        #### 🔧 Current Features:
        - ✅ **Automatic Scene Detection**: Identifies scene boundaries using content analysis
        - ✅ **Keyframe Extraction**: Captures representative frames from each scene
        - ✅ **Summary Generation**: Creates detailed text reports
        - ✅ **Metadata Export**: Exports structured data in JSON format
        - ✅ **Visual Storyboard**: Displays keyframe gallery
        
        #### 🚀 Advanced Features (Coming Soon):
        - 🔍 **Object Detection**: YOLOv8-powered object recognition
        - 💬 **Image Captioning**: BLIP model for frame descriptions
        - 🎤 **Speech Transcription**: Whisper for audio-to-text
        - 📝 **Text Summarization**: BART for concise summaries
        - 🛡️ **Content Moderation**: NSFW detection and filtering
        
        #### 📦 Technology Stack:
        - **Frontend**: Streamlit
        - **Video Processing**: OpenCV, PySceneDetect
        - **Deep Learning**: PyTorch, Transformers (optional)
        - **Image Processing**: Pillow, NumPy
        
        #### 🎯 Use Cases:
        - 📺 Content creators analyzing footage
        - 🎓 Educators reviewing lecture videos
        - 🏢 Businesses processing training materials
        - 🔬 Researchers analyzing video data
        
        #### 📖 How It Works:
        1. **Upload**: Select your video file
        2. **Configure**: Adjust scene detection settings
        3. **Process**: AI analyzes the video
        4. **Review**: Examine keyframes and summary
        5. **Export**: Download results
        
        ---
        
        **Repository**: [GitHub](https://github.com/DHARSHAN0401/AI-Powered-Visual-Insight-System-for-Automated-Video-Summarization-and-Content-Moderation)
        
        **Made with ❤️ using Streamlit, OpenCV, and Python**
        """)

if __name__ == '__main__':
    main()
