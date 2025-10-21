"""Simple speech transcriber placeholder.

This implementation attempts to import Whisper if available. If not,
it returns an empty transcript and no segments. This keeps the pipeline
lightweight for demonstration.
"""
from project.modules.utils import setup_logger, timeit

logger = setup_logger(__name__)


class SpeechTranscriber:
    def __init__(self, model_name: str = "small"):
        self.model_name = model_name
        self.model = None

    def _load(self):
        if self.model is None:
            try:
                import whisper
                # use getattr to avoid static analysis error if attribute isn't present
                load_fn = getattr(whisper, "load_model", None)
                if callable(load_fn):
                    self.model = load_fn(self.model_name)
                    logger.info("Loaded Whisper model '%s'", self.model_name)
                else:
                    self.model = None
            except Exception:
                # silence the exception; we fall back to placeholder
                self.model = None

    @timeit
    def transcribe(self, audio_path: str):
        self._load()
        if not self.model:
            logger.info("Whisper not available, returning placeholder transcript")
            # placeholder: return empty text and no segments
            return "", []
        transcribe_fn = getattr(self.model, "transcribe", None)
        if not callable(transcribe_fn):
            return "", []
        res = transcribe_fn(audio_path)
        if isinstance(res, dict):
            text = res.get("text", "")
            segments = res.get("segments", [])
        else:
            # best-effort extraction
            try:
                text = getattr(res, "text", "") or ""
            except Exception:
                text = ""
            try:
                segments = getattr(res, "segments", []) or []
            except Exception:
                segments = []
        return text, segments

    def transcribe_audio(self, audio_path: str):
        return self.transcribe(audio_path)
