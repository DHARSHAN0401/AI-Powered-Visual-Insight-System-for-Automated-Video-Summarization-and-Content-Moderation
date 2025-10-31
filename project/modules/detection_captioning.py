import torch
from PIL import Image
from typing import List
from project.modules.utils import setup_logger, timeit
from tqdm import tqdm

logger = setup_logger(__name__)

class DetectorCaptioner:
    """
    Runs object detection (YOLOv8), image captioning (BLIP), and computes
    CLIP embeddings for a list of keyframes.
    """
    def __init__(self, use_gpu: bool = False):
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing DetectorCaptioner on device: {self.device}")
        self.yolo_model = None
        self.blip_processor = None
        self.blip_model = None
        self.clip_processor = None
        self.clip_model = None

    def _load_models(self):
        """Lazy-load all required models."""
        if self.yolo_model is None:
            from ultralytics import YOLO
            logger.info("Loading YOLOv8 model...")
            self.yolo_model = YOLO("yolov8n.pt")
            self.yolo_model.to(self.device)
        if self.blip_model is None:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            logger.info("Loading BLIP model...")
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model.to(self.device)
        if self.clip_model is None:
            from transformers import CLIPProcessor, CLIPModel
            logger.info("Loading CLIP model...")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model.to(self.device)

    @timeit
    def process_keyframes(self, keyframes: List[dict], batch_size: int = 8) -> List[dict]:
        """
        Process keyframes in batches to perform detection, captioning, and CLIP embedding.
        """
        self._load_models()
        results = []
        
        # Sort keyframes by scene index to process them in order
        keyframes.sort(key=lambda x: x.get("scene_idx", 0))

        for i in tqdm(range(0, len(keyframes), batch_size), desc="Processing Keyframes"):
            batch_keyframes = keyframes[i:i+batch_size]
            image_paths = [kf["frame_path"] for kf in batch_keyframes]
            images = [Image.open(p).convert("RGB") for p in image_paths]

            # YOLOv8 Detections
            yolo_preds = self.yolo_model(image_paths, device=self.device, verbose=False)

            # BLIP Captions
            blip_inputs = self.blip_processor(images, return_tensors="pt").to(self.device)
            blip_out = self.blip_model.generate(**blip_inputs, max_new_tokens=50)
            captions = self.blip_processor.batch_decode(blip_out, skip_special_tokens=True)

            # CLIP Embeddings
            clip_inputs = self.clip_processor(images=images, return_tensors="pt").to(self.device)
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**clip_inputs)
            clip_embeddings = image_features.cpu().numpy().tolist()

            for j, kf in enumerate(batch_keyframes):
                item = dict(kf)
                
                # Detections
                detections = []
                yolo_result = yolo_preds[j]
                names = yolo_result.names
                for box in yolo_result.boxes:
                    detections.append({
                        "box": box.xyxyn.cpu().numpy().flatten().tolist(),
                        "conf": float(box.conf.cpu()),
                        "class_id": int(box.cls.cpu()),
                        "class_name": names[int(box.cls.cpu())]
                    })
                item["detections"] = detections
                
                # Caption
                item["caption"] = captions[j]
                
                # CLIP Embedding
                item["clip_embedding"] = clip_embeddings[j]
                
                results.append(item)
        
        return results
