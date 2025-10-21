"""Speech transcription using Whisper."""
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

                self.model = whisper.load_model(self.model_name)
                logger.info("Loaded Whisper model '%s'", self.model_name)
            except Exception as e:
                logger.warning("Whisper not available: %s", e)

    @timeit
    def transcribe(self, audio_path: str):
        """Simple wrapper to transcribe and return raw text and segments."""
        self._load()
        if not self.model:
            logger.warning("Whisper model not loaded, returning empty transcript")
            return "", []
        res = self.model.transcribe(audio_path)
        text = res.get("text", "")
        segments = res.get("segments", [])
        return text, segments

    # compatibility name used in main
    def transcribe_audio(self, audio_path: str):
        return self.transcribe(audio_path)
