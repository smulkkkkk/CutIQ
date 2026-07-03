from faster_whisper import WhisperModel
from app.core.config import settings

_client = None


class WhisperClient:
    def __init__(self):
        self._model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type="int8",
        )

    def transcribe(self, audio_path: str) -> dict:
        segments, info = self._model.transcribe(audio_path, beam_size=5)
        segment_list = [
            {"start": s.start, "end": s.end, "text": s.text}
            for s in segments
        ]
        full_text = "".join(s["text"] for s in segment_list)
        return {
            "language": info.language,
            "segments": segment_list,
            "text": full_text,
        }


def get_whisper_client() -> WhisperClient:
    global _client
    if _client is None:
        _client = WhisperClient()
    return _client
