"""Text summarization using transformers pipeline (BART/Pegasus)."""
from transformers import pipeline
from project.modules.utils import setup_logger, timeit

logger = setup_logger(__name__)


class TextSummarizer:
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self.model_name = model_name
        self.summarizer = None

    def _load(self):
        if self.summarizer is None:
            try:
                self.summarizer = pipeline("summarization", model=self.model_name)
                logger.info("Loaded summarization model %s", self.model_name)
            except Exception as e:
                logger.warning("Summarizer not available: %s", e)

    @timeit
    def summarize(self, text: str, max_length: int = 200):
        if not text:
            return ""
        self._load()
        if not self.summarizer:
            return text
        # pipeline will chunk long text; keep simple
        out = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)
        return out[0]["summary_text"]
