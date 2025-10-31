import re
import torch
from project.modules.utils import setup_logger, timeit
from tqdm import tqdm

logger = setup_logger(__name__)

# A more comprehensive, but still basic, profanity list
PROFANITY = {
    "fuck", "shit", "bitch", "asshole", "cunt", "dick", "pussy", 
    "nigger", "faggot", "slut", "whore"
}

class Moderator:
    def __init__(self, use_gpu: bool = False):
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing Moderator on device: {self.device}")
        self.nudenet = None

    def _load_model(self):
        """Lazy-load the NudeNet model."""
        if self.nudenet is None:
            try:
                from nudenet import NudeDetector
                logger.info("Loading NudeNet model...")
                self.nudenet = NudeDetector()
            except ImportError:
                logger.warning("NudeNet is not installed. Skipping NSFW detection.")
                self.nudenet = "unavailable"
            except Exception as e:
                logger.error(f"Failed to load NudeNet model: {e}")
                self.nudenet = "unavailable"

    @timeit
    def moderate(self, det_results: list, speech_segments: list):
        """
        Runs moderation checks for NSFW content, violence, and profanity.
        """
        self._load_model()
        
        image_flags = self._moderate_images(det_results)
        text_flags = self._moderate_text(speech_segments)

        report = {
            "image_flags": image_flags, 
            "text_flags": text_flags,
            "summary": {
                "image_flags_count": len(image_flags),
                "text_flags_count": len(text_flags),
                "has_nsfw_content": any(f['reason'] == 'nsfw' for f in image_flags),
                "has_violence_content": any(f['reason'] == 'violence_keyword' for f in image_flags),
                "has_profanity": len(text_flags) > 0
            }
        }
        return report

    def _moderate_images(self, det_results: list):
        """Moderate images for NSFW content and violence keywords."""
        image_flags = []
        
        # NSFW detection with NudeNet
        if self.nudenet and self.nudenet != "unavailable":
            image_paths = [r["frame_path"] for r in det_results]
            try:
                nude_results = self.nudenet.detect(image_paths)
                for i, res in enumerate(nude_results):
                    nsfw_detections = [d for d in res['preds'] if d['class'] in ['EXPOSED_ANUS', 'EXPOSED_BREAST_F', 'EXPOSED_GENITALIA_F', 'EXPOSED_GENITALIA_M']]
                    if nsfw_detections:
                        image_flags.append({
                            "scene_idx": det_results[i]["scene_idx"],
                            "timestamp": det_results[i]["timestamp"],
                            "reason": "nsfw",
                            "details": nsfw_detections
                        })
            except Exception as e:
                logger.error(f"NudeNet detection failed: {e}")

        # Violence/weapon detection using YOLO results
        weapon_labels = {'knife', 'gun', 'pistol', 'revolver', 'rifle'} # Example labels
        for r in det_results:
            for d in r.get("detections", []):
                if d.get("class_name") in weapon_labels and d.get("conf", 0) > 0.4:
                    image_flags.append({
                        "scene_idx": r["scene_idx"],
                        "timestamp": r["timestamp"],
                        "reason": "violence_keyword",
                        "details": d
                    })
        return image_flags

    def _moderate_text(self, speech_segments: list):
        """Check speech segments for profanity."""
        text_flags = []
        for seg in speech_segments:
            text_lower = (seg.get("text") or "").lower()
            # Use word boundaries to avoid matching substrings
            found_words = {word for word in PROFANITY if re.search(r'\b' + re.escape(word) + r'\b', text_lower)}
            
            if found_words:
                text_flags.append({
                    "start": seg.get("start"), 
                    "end": seg.get("end"), 
                    "words": list(found_words), 
                    "text": seg.get("text")
                })
        return text_flags
    
    def moderate_images_and_text(self, det_results: list, speech_segments: list):
        return self.moderate(det_results, speech_segments)
