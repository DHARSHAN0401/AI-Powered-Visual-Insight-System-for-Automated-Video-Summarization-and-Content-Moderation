#!/usr/bin/env python3
"""
AI-Powered Visual Insight System - Main Pipeline
Orchestrates video summarization and content moderation workflow
"""

import argparse
import time
import logging
import os
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.utils import ensure_dirs, setup_logger, generate_id, timeit
from modules.video_preprocessor import VideoPreprocessor
from modules.keyframe_extractor import KeyframeExtractor
from modules.detection_captioning import DetectorCaptioner
from modules.speech_transcriber import SpeechTranscriber
from modules.summarizer import TextSummarizer
from modules.moderator import Moderator
from modules.summarizer_video import VideoSummarizer

# Setup logger
logger = setup_logger(name=__name__, level=logging.INFO)


def build_arg_parser():
    """Build command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="AI-Powered Visual Insight System - Video Summarization & Content Moderation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--input", "-i", required=True, 
                        help="Input video file path (mp4, mov, avi, etc.)")
    parser.add_argument("--output", "-o", default="outputs",
                        help="Output directory for results")
    parser.add_argument("--max-scenes", type=int, default=6,
                        help="Maximum scenes to include in summary video")
    parser.add_argument("--scene-threshold", type=float, default=30.0,
                        help="Scene detection sensitivity (lower = more scenes)")
    parser.add_argument("--gpu", action="store_true",
                        help="Use GPU acceleration if available")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")
    return parser


@timeit
def run_pipeline(video_path: str, output_dir: str, max_scenes: int = 6, 
                 scene_threshold: float = 30.0, use_gpu: bool = False):
    """
    Execute the complete video processing pipeline
    
    Args:
        video_path: Path to input video file
        output_dir: Directory for output files
        max_scenes: Maximum number of scenes in summary
        scene_threshold: Scene detection sensitivity
        use_gpu: Whether to use GPU acceleration
        
    Returns:
        dict: Processing results and output paths
    """
    # Generate unique session ID
    session_id = generate_id()
    session_dir = os.path.join(output_dir, session_id)
    storyboard_dir = os.path.join(session_dir, "storyboard")
    ensure_dirs([session_dir, storyboard_dir])
    
    logger.info(f"=" * 80)
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Input Video: {video_path}")
    logger.info(f"Output Directory: {session_dir}")
    logger.info(f"GPU Enabled: {use_gpu}")
    logger.info(f"=" * 80)
    
    results = {"session_id": session_id, "video_path": video_path, "outputs": {}}
    
    # Stage 1: Video Preprocessing & Scene Detection
    logger.info("📹 Stage 1: Video Preprocessing & Scene Detection")
    preprocessor = VideoPreprocessor(video_path, session_dir)
    audio_path = preprocessor.extract_audio()
    scenes = preprocessor.detect_scenes(threshold=scene_threshold)
    logger.info(f"✓ Detected {len(scenes)} scenes")
    results["scene_count"] = len(scenes)
    
    # Stage 2: Keyframe Extraction
    logger.info("🖼️  Stage 2: Keyframe Extraction")
    keyframe_extractor = KeyframeExtractor(storyboard_dir)
    keyframes = keyframe_extractor.extract_keyframes(video_path, scenes)
    logger.info(f"✓ Extracted {len(keyframes)} keyframes")
    results["keyframe_count"] = len(keyframes)
    
    # Stage 3: Object Detection & Image Captioning
    logger.info("🔍 Stage 3: Object Detection & Image Captioning")
    detector = DetectorCaptioner(use_gpu=use_gpu)
    detection_results = detector.process_keyframes(keyframes)
    logger.info(f"✓ Processed {len(detection_results)} frames with detection & captioning")
    
    # Stage 4: Speech-to-Text Transcription
    logger.info("🎤 Stage 4: Speech-to-Text Transcription")
    transcriber = SpeechTranscriber(use_gpu=use_gpu)
    transcript, speech_segments = transcriber.transcribe_audio(audio_path)
    transcript_path = os.path.join(session_dir, "transcript.txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    logger.info(f"✓ Transcribed audio ({len(speech_segments)} segments)")
    results["outputs"]["transcript"] = transcript_path
    
    # Stage 5: Text Summarization
    logger.info("📝 Stage 5: Text Summarization")
    summarizer = TextSummarizer(use_gpu=use_gpu)
    # Combine captions and transcript for comprehensive summary
    combined_text = transcript + "\n\n" + "\n".join([
        f"Frame {i}: {res['caption']}" 
        for i, res in enumerate(detection_results) if res.get('caption')
    ])
    summary_text = summarizer.summarize(combined_text)
    summary_path = os.path.join(session_dir, "summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    logger.info(f"✓ Generated text summary ({len(summary_text)} characters)")
    results["outputs"]["summary"] = summary_path
    
    # Stage 6: Content Moderation
    logger.info("🛡️  Stage 6: Content Moderation")
    moderator = Moderator(use_gpu=use_gpu)
    moderation_report = moderator.moderate(
        detection_results, speech_segments
    )
    moderation_path = os.path.join(session_dir, "moderation_report.json")
    with open(moderation_path, "w", encoding="utf-8") as f:
        json.dump(moderation_report, f, indent=2, ensure_ascii=False)
    flag_count = moderation_report.get("summary", {}).get("image_flags_count", 0) + \
                 moderation_report.get("summary", {}).get("text_flags_count", 0)
    logger.info(f"✓ Moderation complete ({flag_count} flags detected)")
    results["outputs"]["moderation"] = moderation_path
    results["moderation_flags"] = flag_count
    
    # Stage 7: Summary Video Creation
    logger.info("🎬 Stage 7: Summary Video Creation")
    video_summarizer = VideoSummarizer(session_dir)
    summary_video_path = video_summarizer.create_summary_video(
        video_path, scenes, detection_results, max_scenes=max_scenes
    )
    logger.info(f"✓ Created summary video: {summary_video_path}")
    results["outputs"]["summary_video"] = summary_video_path
    
    # Save storyboard metadata
    storyboard_metadata = {
        "session_id": session_id,
        "scenes": scenes,
        "keyframes": keyframes,
        "detections": detection_results
    }
    storyboard_path = os.path.join(session_dir, "storyboard_metadata.json")
    with open(storyboard_path, "w", encoding="utf-8") as f:
        json.dump(storyboard_metadata, f, indent=2)
    results["outputs"]["storyboard"] = storyboard_path
    
    logger.info(f"=" * 80)
    logger.info(f"✅ Pipeline Complete!")
    logger.info(f"📂 All outputs saved to: {session_dir}")
    logger.info(f"=" * 80)
    
    return results


def main():
    """Main entry point"""
    parser = build_arg_parser()
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.input):
        logger.error(f"❌ Input video not found: {args.input}")
        return 1
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run pipeline
    try:
        results = run_pipeline(
            video_path=args.input,
            output_dir=args.output,
            max_scenes=args.max_scenes,
            scene_threshold=args.scene_threshold,
            use_gpu=args.gpu
        )
        return 0
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
