"""Creates a short summarized video by selecting top scenes and concatenating them."""
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from project.modules.utils import setup_logger, timeit
from tqdm import tqdm

logger = setup_logger(__name__)


class VideoSummarizer:
    def __init__(self, outdir: str):
        self.outdir = outdir

    @timeit
    def create_summary_video(self, video_path: str, scenes: list, det_results: list, max_scenes: int = 6):
        """Selects top scenes (by presence of detections or simply first N) and concatenates them.

        Returns path to summary video.
        """
        scored = []
        det_map = {r["scene_idx"]: r for r in det_results}
        for i, s in enumerate(scenes):
            score = 0
            r = det_map.get(i)
            if r and r.get("detections"):
                score += len(r.get("detections"))
            scored.append((score, i, s))
        scored.sort(reverse=True)
        chosen = [s for _, _, s in scored[:max_scenes]]

        clips = []
        for start, end in tqdm(chosen, desc="Building summary clips"):
            try:
                clip = VideoFileClip(video_path).subclip(start, end)
                clips.append(clip)
            except Exception as e:
                logger.warning("Failed to create clip %s-%s: %s", start, end, e)

        if not clips:
            logger.warning("No clips selected; creating a short sample from the start")
            clips = [VideoFileClip(video_path).subclip(0, min(5, 5))]

        final = concatenate_videoclips(clips)
        out_path = os.path.join(self.outdir, "summary.mp4")
        final.write_videofile(out_path, codec="libx264", audio_codec="aac")
        for c in clips:
            c.close()
        final.close()
        return out_path
