"""Basic content moderation: image-level heuristics and speech profanity checks."""
import re
from project.modules.utils import setup_logger

logger = setup_logger(__name__)

PROFANITY = set(["fuck", "shit", "bitch", "asshole", "nigger"])  # example list - expand in production


class Moderator:
    def __init__(self):
        pass

    def moderate_images_and_text(self, det_results: list, speech_segments: list):
        """Runs simple heuristics to flag unsafe content.

        det_results: output of DetectorCaptioner.process_keyframes
        speech_segments: Whisper segments with 'start','end','text'
        returns: dict report
        """
        image_flags = []
        for r in det_results:
            flags = []
            # check detections for weapons (class label names would require mapping; use confidences)
            for d in r.get("detections", []):
                # placeholder: if any detection has high confidence, flag
                if d.get("conf") and d.get("conf") > 0.8:
                    flags.append({"reason": "high_conf_detection", "detail": d})
            # caption-based heuristics for nudity or violence keywords
            cap = (r.get("caption") or "").lower()
            if any(k in cap for k in ["nude", "naked", "sex", "blood", "knife", "gun"]):
                flags.append({"reason": "caption_keyword", "detail": cap})
            if flags:
                image_flags.append({"scene_idx": r["scene_idx"], "timestamp": r["timestamp"], "flags": flags})

        text_flags = []
        for seg in speech_segments:
            t = (seg.get("text") or "").lower()
            words = re.findall(r"\w+", t)
            found = [w for w in words if w in PROFANITY]
            if found:
                text_flags.append({"start": seg.get("start"), "end": seg.get("end"), "words": found, "text": seg.get("text")})

        report = {"image_flags": image_flags, "text_flags": text_flags}
        return report
