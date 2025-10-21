"""Select representative keyframes from scenes."""
import cv2
import os
from project.modules.utils import timeit, setup_logger
from tqdm import tqdm

logger = setup_logger(__name__)


class KeyframeExtractor:
    def __init__(self, outdir: str):
        self.outdir = outdir
        self.storyboard_dir = os.path.join(outdir, "storyboard")
        os.makedirs(self.storyboard_dir, exist_ok=True)

    @timeit
    def extract_keyframes(self, video_path: str, scenes: list):
        """For each scene choose the middle frame as representative keyframe.

        Returns list of dicts: {scene_idx, start, end, frame_path, timestamp}
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        results = []
        for i, (start, end) in enumerate(tqdm(scenes, desc="Extracting keyframes")):
            mid = (start + end) / 2.0
            frame_no = int(mid * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame for scene %d", i)
                continue
            outpath = os.path.join(self.storyboard_dir, f"scene_{i:03d}.jpg")
            cv2.imwrite(outpath, frame)
            results.append({"scene_idx": i, "start": start, "end": end, "frame_path": outpath, "timestamp": mid})
        cap.release()
        return results
