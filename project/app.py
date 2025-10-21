import streamlit as st
import os
import tempfile
import time
from typing import Callable, Optional

from project.modules.utils import setup_logger, ensure_dirs
logger = setup_logger('app')


def run_pipeline(inpath: str, outdir: str, max_scenes: int = 4, progress: Optional[Callable[[str, Optional[float]], None]] = None):
    """Run the pipeline in-process. progress is an optional callable(progress_msg, progress_float).
    Returns the outdir on success.
    """
    def _p(msg: str, pct: Optional[float] = None):
        if callable(progress):
            try:
                progress(msg, pct)
            except Exception:
                pass

    ensure_dirs([outdir])
    _p('Starting pipeline')
    start = time.time()

    from project.modules.video_preprocessor import VideoPreprocessor
    from project.modules.keyframe_extractor import KeyframeExtractor
    from project.modules.detection_captioning import DetectorCaptioner
    from project.modules.speech_transcriber import SpeechTranscriber
    from project.modules.summarizer import TextSummarizer
    from project.modules.moderator import Moderator
    from project.modules.summarizer_video import VideoSummarizer

    vp = VideoPreprocessor(inpath, outdir)
    _p('Detecting scenes', 0.05)
    scenes = vp.detect_scenes()

    _p('Extracting keyframes', 0.2)
    kfe = KeyframeExtractor(outdir)
    keyframes = kfe.extract_keyframes(inpath, scenes)

    _p('Running detections & captions', 0.4)
    detcap = DetectorCaptioner()
    det_results = detcap.process_keyframes(keyframes)

    _p('Extracting audio', 0.6)
    audio_path = vp.extract_audio()

    _p('Transcribing audio', 0.65)
    st_model = SpeechTranscriber()
    transcript, segments = st_model.transcribe_audio(audio_path)

    _p('Summarizing text', 0.8)
    summarizer = TextSummarizer()
    summary_text = summarizer.summarize(transcript)
    with open(os.path.join(outdir, 'summary.txt'), 'w', encoding='utf-8') as f:
        f.write(summary_text)

    _p('Moderating content', 0.85)
    moderator = Moderator()
    report = moderator.moderate_images_and_text(det_results, segments)
    import json
    with open(os.path.join(outdir, 'moderation_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    _p('Building summary video', 0.9)
    vs = VideoSummarizer(outdir)
    summary_video = vs.create_summary_video(inpath, scenes, det_results, max_scenes=max_scenes)

    elapsed = time.time() - start
    _p(f'Completed in {elapsed:.1f}s', 1.0)
    return outdir


st.set_page_config(page_title='Video Summarizer & Moderator', layout='wide')

st.title('AI-Powered Visual Insight — Demo (Lightweight)')

st.markdown('Upload a video and click Run to execute the pipeline. This demo uses lightweight fallbacks for models.')

uploaded = st.file_uploader('Upload video', type=['mp4', 'mov', 'mkv'])
max_scenes = st.slider('Max summary scenes', 1, 10, 4)
run_btn = st.button('Run pipeline')

if 'last_run' not in st.session_state:
    st.session_state['last_run'] = None

if run_btn and uploaded:
    tmpdir = tempfile.mkdtemp(prefix='vis_demo_')
    inpath = os.path.join(tmpdir, uploaded.name)
    with open(inpath, 'wb') as f:
        f.write(uploaded.getbuffer())
    outdir = os.path.join(tmpdir, 'outputs')
    pbar = st.progress(0.0)
    log = st.empty()

    def _progress(msg, pct=None):
        if pct is not None:
            try:
                pbar.progress(min(max(int(pct*100), 0), 100))
            except Exception:
                pass
        log.text(msg)

    try:
        st.info('Running pipeline — this may take a few seconds')
        od = run_pipeline(inpath, outdir, max_scenes=max_scenes, progress=_progress)
        st.success('Pipeline finished')
        st.session_state['last_run'] = od
    except Exception as e:
        st.error(f'Pipeline failed: {e}')

if st.session_state['last_run']:
    outdir = st.session_state['last_run']
    st.header('Outputs')
    cols = st.columns([1,2])
    with cols[0]:
        st.subheader('Storyboard')
        sb = os.path.join(outdir, 'storyboard')
        if os.path.exists(sb):
            imgs = sorted([os.path.join(sb, f) for f in os.listdir(sb) if f.lower().endswith('.jpg')])
            for im in imgs:
                st.image(im, use_column_width=True)
        else:
            st.write('No storyboard')

    with cols[1]:
        st.subheader('Summary')
        sum_path = os.path.join(outdir, 'summary.txt')
        if os.path.exists(sum_path):
            with open(sum_path, 'r', encoding='utf-8') as f:
                st.text(f.read())
        else:
            st.write('No summary')

    st.subheader('Moderation report')
    rep = os.path.join(outdir, 'moderation_report.json')
    if os.path.exists(rep):
        st.json(__import__('json').load(open(rep, 'r', encoding='utf-8')))
    else:
        st.write('No report')

    st.subheader('Summary video')
    sv = os.path.join(outdir, 'summary.mp4')
    if os.path.exists(sv):
        st.video(sv)
    else:
        st.write('No summary video')
