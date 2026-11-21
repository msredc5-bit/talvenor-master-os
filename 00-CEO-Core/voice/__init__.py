"""Jarvis voice loop — Piper TTS + Vosk/sherpa-onnx STT (REAL, offline, $0).

Ears (listening) + mouth (speaking) — both on this PC, no internet, $0 cost.

  - Speaking (TTS): Piper — voice id VERIFIED from upstream voices.json.
  - Listening (STT): English = Vosk (classic Kaldi model, on the official list);
    Bengali = sherpa-onnx (Zipformer2 streaming model — because the classic
    Vosk official list has no Bengali model; the one that exists is a
    sherpa-onnx/icefall model and does not load with vosk.Model()).

Importing this package does not require piper/vosk/sherpa — those are
lazily imported inside the functions. If one is missing, a clear error
comes with the exact install/download command; nothing silently pretends.
"""

from .speak import VOICE_IDS, speak, speak_to_wav
from .listen import MODEL_IDS, listen, transcribe_file
from .loop import GATE_PHRASES, handle_voice_text, run_voice_loop

__all__ = [
    "VOICE_IDS",
    "MODEL_IDS",
    "speak",
    "speak_to_wav",
    "listen",
    "transcribe_file",
    "GATE_PHRASES",
    "handle_voice_text",
    "run_voice_loop",
]
