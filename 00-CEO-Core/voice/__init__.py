"""Jarvis voice loop — Piper TTS + Vosk/sherpa-onnx STT (REAL, offline, $0).

কান (শোনা) + মুখ (বলা) — দুইটাই এই PC-তে, internet ছাড়া, খরচ $0।

  - বলা (TTS): Piper — voice id VERIFIED upstream voices.json থেকে।
  - শোনা (STT): English = Vosk (classic Kaldi model, official list-এ
    আছে); Bengali = sherpa-onnx (Zipformer2 streaming model — কারণ
    classic Vosk-এর official list-এ কোনো Bengali model নেই; যেটা আছে
    সেটা sherpa-onnx/icefall-এর model, vosk.Model() দিয়ে লোড হয় না)।

এই package import করলেই piper/vosk/sherpa লাগে না — ওগুলো function-এর
ভেতরে lazy import হয়। না থাকলে exact install/download command-সহ
স্পষ্ট error আসে, চুপচাপ ভান হয় না।
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
