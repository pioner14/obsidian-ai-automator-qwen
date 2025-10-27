"""
Пакет transcription для транскрибации аудио/видео
"""
from .base_transcriber import BaseTranscriber
from .deepgram_transcriber import DeepgramTranscriber
from .openai_transcriber import OpenAITranscriber
from .whisper_transcriber import WhisperTranscriber
from .ollama_transcriber import OllamaTranscriber
from .local_whisper_transcriber import LocalWhisperTranscriber

__all__ = [
    'BaseTranscriber',
    'DeepgramTranscriber',
    'OpenAITranscriber',
    'WhisperTranscriber',
    'OllamaTranscriber',
    'LocalWhisperTranscriber'
]