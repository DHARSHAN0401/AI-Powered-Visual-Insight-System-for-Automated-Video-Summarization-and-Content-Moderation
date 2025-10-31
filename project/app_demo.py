"""
AI-Powered Visual Insight System - Web Interface
Interactive Streamlit dashboard for video summarization and content moderation
"""

import streamlit as st
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import tempfile

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
    .stAlert {
        border-radius: 10px;
    }
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def check_dependencies():
    """Check which dependencies are installed"""
    deps = {}
    required = {
        'cv2': 'OpenCV',
        'scenedetect': 'PySceneDetect',
        'torch': 'PyTorch',
        'transformers': 'Transformers',
        'whisper': 'Whisper',
        'ultralytics': 'YOLOv8',
    }
    
    for module, name in required.items():
        try:
            __import__(module)
            deps[name] = True
        except ImportError:
            deps[name] = False
    
    return deps

def process_video_basic(video_path, output_dir):
    """Process video with basic scene detection and summarization"""
    try:
        import cv2
        from scenedetect import detect, ContentDetector
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Detect scenes
        st.info("📹 Detecting scenes in video...")
        scenes = detect(video_path, ContentDetector(threshold=30.0))
        
        st.success(f"✅ Detected {len(scenes)} scenes")
        
        # Step 2: Extract keyframes
        st.info("🖼️ Extracting keyframes...")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        keyframes = []
        storyboard_dir = os.path.join(output_dir, "storyboard")
        os.makedirs(storyboard_dir, exist_ok=True)
        
        for idx, scene in enumerate(scenes[:8]):  # Limit to 8 scenes
            # Get middle frame of scene
            start_frame = int(scene[0].get_frames())
            end_frame = int(scene[1].get_frames())
            middle_frame = (start_frame + end_frame) // 2
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            ret, frame = cap.read()
            
            if ret:
                keyframe_path = os.path.join(storyboard_dir, f"keyframe_{idx:03d}.jpg")
                cv2.imwrite(keyframe_path, frame)
                keyframes.append({
                    'index': idx,
                    'path': keyframe_path,
                    'timestamp': middle_frame / fps,
                    'scene': [start_frame / fps, end_frame / fps]
                })
        
        cap.release()
        st.success(f"✅ Extracted {len(keyframes)} keyframes")
        
        # Step 3: Generate basic summary
        st.info("📝 Generating summary...")
        
        summary_text = f"""Video Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Video Analysis:
- Total Scenes Detected: {len(scenes)}
- Keyframes Extracted: {len(keyframes)}
- Video Duration: {keyframes[-1]['scene'][1]:.2f} seconds

Scene Breakdown:
"""
        
        for kf in keyframes:
            summary_text += f"\nScene {kf['index'] + 1}:"
            summary_text += f"\n  Time: {kf['scene'][0]:.2f}s - {kf['scene'][1]:.2f}s"
            summary_text += f"\n  Duration: {kf['scene'][1] - kf['scene'][0]:.2f}s"
        
        # Save summary
        summary_path = os.path.join(output_dir, "summary.txt")
        with open(summary_path, 'w') as f:
            f.write(summary_text)
        
        # Save metadata
        metadata = {
            'scenes': len(scenes),
            'keyframes': keyframes,
            'timestamp': datetime.now().isoformat(),
            'processing_mode': 'basic'
        }
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        st.success("✅ Processing complete!")
        
        return {
            'success': True,
            'scenes': len(scenes),
            'keyframes': keyframes,
            'summary': summary_text,
            'metadata': metadata
        }
        
    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    # Header
    st.markdown('<h1 class="main-header">🎬 AI-Powered Visual Insight System</h1>', unsafe_allow_html=True)
    st.markdown("### Automated Video Summarization and Content Moderation")
    
    # Sidebar
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/_static/logo.svg", width=200)
        st.markdown("---")
        
        st.markdown("### 🎯 Features")
        st.markdown("""
        - 🎥 Scene Detection
        - 🖼️ Keyframe Extraction
        - 🔍 Object Detection (with AI models)
        - 💬 Image Captioning
        - 🎤 Speech Transcription
        - 📝 Text Summarization
        - 🛡️ Content Moderation
        """)
        
        st.markdown("---")
        st.markdown("### 📦 System Status")
        
        deps = check_dependencies()
        for name, installed in deps.items():
            status = "✅" if installed else "❌"
            st.markdown(f"{status} {name}")
        
        installed_count = sum(deps.values())
        total_count = len(deps)
        
        if installed_count == total_count:
            st.success(f"All packages installed! ({installed_count}/{total_count})")
        else:
            st.warning(f"Some packages missing ({installed_count}/{total_count})")
            st.info("💡 Running in basic mode")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "📊 Results", "ℹ️ About"])
    
    with tab1:
        st.markdown("## Upload Video")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Upload a video file to analyze (max 200MB)"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if uploaded_file is not None:
                st.video(uploaded_file)
                
                # Save uploaded file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    video_path = tmp_file.name
                
                st.session_state['video_path'] = video_path
                st.success(f"✅ Video uploaded: {uploaded_file.name}")
        
        with col2:
            st.markdown("### ⚙️ Settings")
            
            max_scenes = st.slider("Max scenes to extract", 3, 15, 8)
            scene_threshold = st.slider("Scene detection sensitivity", 10.0, 50.0, 30.0)
            
            st.session_state['max_scenes'] = max_scenes
            st.session_state['scene_threshold'] = scene_threshold
        
        st.markdown("---")
        
        # Process button
        if uploaded_file is not None:
            if st.button("🚀 Process Video", type="primary", use_container_width=True):
                with st.spinner("Processing video... This may take a few minutes."):
                    # Create output directory
                    output_dir = os.path.join("outputs", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    
                    # Process video
                    result = process_video_basic(video_path, output_dir)
                    
                    if result['success']:
                        st.session_state['result'] = result
                        st.session_state['output_dir'] = output_dir
                        st.balloons()
                        st.success("🎉 Video processing complete! Check the Results tab.")
                    else:
                        st.error(f"Processing failed: {result.get('error', 'Unknown error')}")
        else:
            st.info("👆 Please upload a video file to begin")
    
    with tab2:
        st.markdown("## 📊 Analysis Results")
        
        if 'result' in st.session_state and st.session_state['result']['success']:
            result = st.session_state['result']
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Scenes", result['scenes'])
            
            with col2:
                st.metric("Keyframes Extracted", len(result['keyframes']))
            
            with col3:
                duration = result['keyframes'][-1]['scene'][1] if result['keyframes'] else 0
                st.metric("Duration", f"{duration:.1f}s")
            
            st.markdown("---")
            
            # Keyframe storyboard
            st.markdown("### 🖼️ Keyframe Storyboard")
            
            cols = st.columns(4)
            for idx, kf in enumerate(result['keyframes']):
                with cols[idx % 4]:
                    if os.path.exists(kf['path']):
                        st.image(kf['path'], caption=f"Scene {kf['index'] + 1}\n{kf['timestamp']:.1f}s")
            
            st.markdown("---")
            
            # Text summary
            st.markdown("### 📝 Summary")
            st.text_area("Generated Summary", result['summary'], height=300)
            
            # Download buttons
            st.markdown("### 💾 Download Results")
            col1, col2 = st.columns(2)
            
            with col1:
                summary_file = os.path.join(st.session_state['output_dir'], 'summary.txt')
                if os.path.exists(summary_file):
                    with open(summary_file, 'r') as f:
                        st.download_button(
                            "📄 Download Summary",
                            f.read(),
                            file_name="video_summary.txt",
                            mime="text/plain"
                        )
            
            with col2:
                metadata_file = os.path.join(st.session_state['output_dir'], 'metadata.json')
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        st.download_button(
                            "📊 Download Metadata",
                            f.read(),
                            file_name="metadata.json",
                            mime="application/json"
                        )
        else:
            st.info("👈 Process a video first to see results here")
    
    with tab3:
        st.markdown("## About This Project")
        
        st.markdown("""
        ### 🎬 AI-Powered Visual Insight System
        
        This application uses state-of-the-art AI models to automatically analyze videos:
        
        #### 🔧 Current Features (Basic Mode):
        - ✅ **Scene Detection**: Automatically identifies scene boundaries
        - ✅ **Keyframe Extraction**: Selects representative frames from each scene
        - ✅ **Summary Generation**: Creates text summaries of video content
        
        #### 🚀 Advanced Features (with full AI models):
        - 🔍 **Object Detection**: YOLOv8 identifies objects in frames
        - 💬 **Image Captioning**: BLIP generates descriptions
        - 🎤 **Speech Transcription**: Whisper converts speech to text
        - 📝 **Text Summarization**: BART creates concise summaries
        - 🛡️ **Content Moderation**: NSFW detection and filtering
        
        #### 📦 Tech Stack:
        - **OpenCV** - Video processing
        - **PySceneDetect** - Scene detection
        - **PyTorch** - Deep learning framework
        - **Transformers** - NLP models
        - **Streamlit** - Web interface
        
        #### 📝 How to Use:
        1. Upload a video file (MP4, AVI, MOV, etc.)
        2. Adjust processing settings if needed
        3. Click "Process Video"
        4. View results in the Results tab
        5. Download summary and metadata
        
        ---
        
        **Note**: This demo runs in basic mode. Install additional AI models for advanced features:
        ```bash
        pip install openai-whisper ultralytics transformers[torch]
        ```
        """)

if __name__ == '__main__':
    main()
