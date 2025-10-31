import torch
from project.modules.utils import setup_logger, timeit

logger = setup_logger(__name__)

class SpeechTranscriber:
    def __init__(self, model_name: str = "base", use_gpu: bool = False):
        self.model_name = model_name
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing SpeechTranscriber on device: {self.device}")
        self.model = None

    def _load(self):
        if self.model is None:
            try:
                import whisper
                logger.info(f"Loading Whisper model '{self.model_name}'...")
                self.model = whisper.load_model(self.model_name, device=self.device)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                self.model = None

    @timeit
    def transcribe(self, audio_path: str):
        self._load()
        if not self.model:
            logger.warning("Whisper not available, returning placeholder transcript.")
            return "", []
        try:
            res = self.model.transcribe(audio_path, fp16=self.device=="cuda")
            text = res.get("text", "")
            segments = res.get("segments", [])
            return text, segments
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return "", []

    def transcribe_audio(self, audio_path: str):
        return self.transcribe(audio_path)
