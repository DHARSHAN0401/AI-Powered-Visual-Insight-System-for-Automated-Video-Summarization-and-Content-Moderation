"""Lightweight heuristic summarizer.

This simple summarizer returns the first few sentences (or first N words)
and is intentionally small and dependency-free so the project remains easy
to run. Replace with a transformer-based summarizer for higher quality.
"""
import re
from project.modules.utils import setup_logger, timeit

logger = setup_logger(__name__)


class TextSummarizer:
    def __init__(self, max_sentences: int = 3):
        self.max_sentences = max_sentences

    @timeit
    def summarize(self, text: str, max_length: int = 200):
        if not text:
            return ""
        # split into sentences naively
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        if len(sentences) <= self.max_sentences:
            return text.strip()
        return " ".join(sentences[: self.max_sentences])
