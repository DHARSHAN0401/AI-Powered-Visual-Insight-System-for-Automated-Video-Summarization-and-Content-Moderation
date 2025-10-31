import torch
from project.modules.utils import setup_logger, timeit
from transformers import pipeline

logger = setup_logger(__name__)


class TextSummarizer:
    def __init__(self, use_gpu: bool = False):
        self.device = 0 if use_gpu and torch.cuda.is_available() else -1
        logger.info(f"Initializing TextSummarizer on device: {'GPU' if self.device == 0 else 'CPU'}")
        self.summarizer = None

    def _load_model(self):
        if self.summarizer is None:
            logger.info("Loading summarization model (BART)...")
            self.summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn", 
                device=self.device
            )

    @timeit
    def summarize(self, text: str, min_length: int = 50, max_length: int = 250):
        self._load_model()
        if not text or not self.summarizer:
            return ""
        
        try:
            # Handle potential token limits by chunking, though for many cases this is sufficient
            summary = self.summarizer(
                text, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )
            return summary[0]['summary_text']
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            # Fallback to simple truncation if model fails
            return " ".join(text.split()[:max_length])
