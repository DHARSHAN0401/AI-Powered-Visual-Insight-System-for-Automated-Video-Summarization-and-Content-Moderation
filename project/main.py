
import argparse
import time
import logging
from project.modules.utils import ensure_dirs, setup_logger, generate_id

logger = setup_logger(name=__name__)


def build_arg_parser():
    p = argparse.ArgumentParser(description="Video summarization pipeline")
    p.add_argument("--input", required=True, help="Input video file path")
    p.add_argument("--outdir", default="D:/maj pro/project/outputs", help="Output folder")
    p.add_argument("--max_summary_scenes", type=int, default=6, help="Max scenes to include in summary")
    return p


def main():
    args = build_arg_parser().parse_args()
    start = time.time()
    ensure_dirs([args.outdir])
    session_id = generate_id()
    logger.info(f"Starting pipeline session {session_id} for {args.input}")

    from project.modules.video_preprocessor import VideoPreprocessor
    from project.modules.keyframe_extractor import KeyframeExtractor
    from project.modules.detection_captioning import DetectorCaptioner
    from project.modules.speech_transcriber import SpeechTranscriber
    from project.modules.summarizer import TextSummarizer
    from project.modules.moderator import Moderator
    from project.modules.summarizer_video import VideoSummarizer

    vp = VideoPreprocessor(args.input, args.outdir)
    scenes = vp.detect_scenes()

    kfe = KeyframeExtractor(args.outdir)
    keyframes = kfe.extract_keyframes(args.input, scenes)

    detcap = DetectorCaptioner()
    det_results = detcap.process_keyframes(keyframes)

    st = SpeechTranscriber()
    transcript, segments = st.transcribe_audio(vp.extract_audio())

    summarizer = TextSummarizer()
    summary_text = summarizer.summarize(transcript)
    summary_txt_path = f"{args.outdir}/summary.txt"
    with open(summary_txt_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    moderator = Moderator()
    report = moderator.moderate_images_and_text(det_results, segments)
    import json
    with open(f"{args.outdir}/moderation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    vs = VideoSummarizer(args.outdir)
    summary_video = vs.create_summary_video(args.input, scenes, det_results, max_scenes=args.max_summary_scenes)

    logger.info(f"Outputs written to {args.outdir}")
    elapsed = time.time() - start
    logger.info(f"Pipeline completed in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
