"""Video preprocessing: normalization, audio extraction, scene detection."""
import os
import subprocess
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from project.modules.utils import timeit, setup_logger

logger = setup_logger(__name__)


class VideoPreprocessor:

    def __init__(self, path: str, outdir: str):
        self.path = path
        self.outdir = outdir
        os.makedirs(self.outdir, exist_ok=True)

    @timeit
    def extract_audio(self) -> str:
        """Extracts audio track into a WAV file and returns its path."""
        out = os.path.join(self.outdir, "audio.wav")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            self.path,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            out,
        ]
        logger.info("Extracting audio to %s", out)
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out

    @timeit
    def detect_scenes(self):
        """Detect shot boundaries using ContentDetector.

        Returns a list of (start_time, end_time) in seconds.
        """
        video_manager = VideoManager([self.path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        try:
            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)
            scene_list = scene_manager.get_scene_list()
            scenes = []
            for start, end in scene_list:
                scenes.append((start.get_seconds(), end.get_seconds()))
            logger.info("Detected %d scenes", len(scenes))
            return scenes
        finally:
            video_manager.release()
