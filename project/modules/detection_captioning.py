"""Lightweight detection and captioning placeholder.

This simplified implementation avoids heavy ML dependencies. It returns an
empty list for detections and uses the filename as a caption. This keeps the
pipeline fast and easy to run for testing and demonstration.
"""
import os
from typing import List
from project.modules.utils import setup_logger, timeit

logger = setup_logger(__name__)


class DetectorCaptioner:
    def __init__(self):
        pass

    @timeit
    def process_keyframes(self, keyframes: List[dict]) -> List[dict]:
        results = []
        for kf in keyframes:
            frame = kf.get("frame_path")
            # ensure frame is a string to avoid type warnings
            caption = os.path.basename(str(frame))
            item = dict(kf)
            item["detections"] = []
            item["caption"] = caption
            results.append(item)
        return results
