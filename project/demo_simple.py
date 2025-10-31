"""
Simple demo script to test the project without heavy dependencies
"""
import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    parser = argparse.ArgumentParser(description='AI Video Summarization - Simple Demo')
    parser.add_argument('--input', '-i', required=False, help='Input video file')
    parser.add_argument('--output', '-o', default='outputs', help='Output directory')
    parser.add_argument('--check', action='store_true', help='Just check system status')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🎬 AI-Powered Visual Insight System - Demo Mode")
    print("=" * 80)
    
    if args.input:
        print(f"Input Video: {args.input}")
        print(f"Output Directory: {args.output}")
        print()
        
        # Check if input file exists
        if not os.path.exists(args.input):
            print(f"❌ Error: Input file '{args.input}' not found!")
            print()
        else:
            print("✅ Input file found")
            print()
    else:
        print("Mode: System Status Check")
        print()
    
    print("📦 Checking installed packages...")
    
    # Check what's available
    packages_status = {}
    required_packages = [
        ('torch', 'PyTorch (Deep Learning)'),
        ('transformers', 'Transformers (NLP Models)'),
        ('cv2', 'OpenCV (Video Processing)'),
        ('scenedetect', 'PySceneDetect (Scene Detection)'),
        ('whisper', 'Whisper (Speech Recognition)'),
        ('ultralytics', 'YOLOv8 (Object Detection)'),
        ('streamlit', 'Streamlit (Web UI)'),
    ]
    
    for package_name, description in required_packages:
        try:
            __import__(package_name)
            status = "✅ Installed"
            packages_status[package_name] = True
        except ImportError:
            status = "❌ Missing"
            packages_status[package_name] = False
        
        print(f"  {status}: {description}")
    
    print()
    
    # Count installed packages
    installed_count = sum(packages_status.values())
    total_count = len(packages_status)
    
    print(f"📊 Status: {installed_count}/{total_count} packages installed")
    print()
    
    if installed_count < total_count:
        print("⚠️  Some packages are missing. To install all dependencies, run:")
        print("   pip install -r requirements.txt")
        print()
        print("💡 Note: Due to disk space limitations, you may need to:")
        print("   1. Free up disk space")
        print("   2. Install packages one by one")
        print("   3. Use a different drive for package cache")
        print()
    
    if packages_status.get('cv2', False) and args.input and os.path.exists(args.input):
        print("🎥 Running video analysis...")
        print("   (This would process the video with full pipeline)")
    elif not packages_status.get('cv2', False):
        print("ℹ️  OpenCV not installed - cannot process video")
        print("   Install with: pip install opencv-python")
    elif args.input:
        print("ℹ️  Ready to process video once all packages are installed")
    
    print()
    print("=" * 80)
    print("✅ Status Check Complete!")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
