"""Jarvis — voice interface (REAL, Phase voice — 2026-11-17).

Jarvis = the Main CEO Bot's nickname / voice face. Boss will talk to Jarvis,
and Jarvis passes it on to the Main CEO Bot (brain).

Previously a STUB (Phase 0) — now REAL:
  - Speaking (TTS): Piper — offline, neural, $0, runs on CPU.
    Voice: bn = bn_BD-google-medium (the catalog's only Bengali voice,
    VERIFIED from upstream voices.json), en = en_US-lessac-medium.
  - Listening (STT): English = Vosk (vosk-model-small-en-us-0.15, on the official
    list); Bengali = sherpa-onnx (vosk-model-small-streaming-bn,
    Zipformer2 — the classic Vosk official list has no Bengali model,
    so sherpa-onnx is the way to hear Bengali).
  - Loop: listen -> brain (mock default) -> speak; gated work
    (send/publish) only becomes PENDING in the ApprovalGateway by voice.

Important: Jarvis and the Main CEO Bot are not one thing — separate modules.
Jarvis only listens/speaks (voice engine); the brain is the Main CEO Bot.

Honest limits:
  - No native listener has heard the quality of the Bengali Piper voice yet;
    Boss himself will verify Vosk/sherpa Bengali accuracy by speaking to it.
  - Brain mock (default) — voice does not make Jarvis intelligent.
  - Without a mic/speaker there is no live test on this VM — the first real mic test
    is on Boss's PC (see VOICE-SETUP.md).

Public functions (the Phase 0 names are unchanged):
  listen() / speak(text) / handle_voice_command(audio_input)
"""

import os
import sys

CEO_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
if CEO_CORE_DIR not in sys.path:
    sys.path.insert(0, CEO_CORE_DIR)

from voice.listen import listen as _listen  # noqa: E402
from voice.loop import handle_voice_text, run_voice_loop  # noqa: E402
from voice.speak import speak as _speak  # noqa: E402

DEFAULT_LANG = "bn"


def listen(seconds=8, lang=DEFAULT_LANG):
    """Listen from the mic — Vosk (en) / sherpa-onnx (bn). Returns text."""
    return _listen(seconds=seconds, lang=lang)


def speak(text, lang=DEFAULT_LANG):
    """Answer Boss by voice — Piper. Returns the WAV path."""
    return _speak(text, lang=lang)


def handle_voice_command(audio_input, lang=DEFAULT_LANG):
    """Voice command -> sent to the Main CEO Bot.

    If audio_input is a str, it is taken as the heard sentence and one turn
    runs; if None, it listens once on the mic and then runs. Returns: the
    handle_voice_text dict.
    """
    if audio_input is None:
        heard = _listen(seconds=8, lang=lang)
    elif isinstance(audio_input, str):
        heard = audio_input
    else:
        raise TypeError(
            "handle_voice_command: audio_input must be a str (the heard sentence) "
            f"or None (listen on the mic). Got: {type(audio_input).__name__}")
    return handle_voice_text(heard, lang=lang)


if __name__ == "__main__":
    print("Jarvis voice — REAL (Piper TTS + Vosk/sherpa-onnx STT, offline, $0)")
    print("Usage: python scripts/jarvis_voice_loop.py [--lang bn|en]")
    print("One-turn test (with text, no mic):")
    print(handle_voice_command("What is my work today?", lang="en"))
