"""Jarvis — voice interface (REAL, Phase voice — 2026-11-17).

Jarvis = Main CEO Bot-এর ডাকনাম / voice মুখ। Boss কথা বলবেন Jarvis-কে,
Jarvis সেটা Main CEO Bot (brain)-এর কাছে পাঠাবে।

আগে ছিল STUB (Phase 0) — এখন REAL:
  - বলা (TTS): Piper — offline, neural, $0, CPU-তে চলে।
    Voice: bn = bn_BD-google-medium (catalog-এর একমাত্র Bengali voice,
    VERIFIED upstream voices.json), en = en_US-lessac-medium।
  - শোনা (STT): English = Vosk (vosk-model-small-en-us-0.15, official
    list-এ আছে); Bengali = sherpa-onnx (vosk-model-small-streaming-bn,
    Zipformer2 — classic Vosk-এর official list-এ Bengali model নেই,
    তাই sherpa-onnx-ই Bengali শোনার পথ)।
  - Loop: listen -> brain (mock default) -> speak; gated কাজ
    (send/publish) voice-এ শুধু ApprovalGateway-এ PENDING হয়।

গুরুত্বপূর্ণ: Jarvis আর Main CEO Bot এক জিনিস নয় — আলাদা module।
Jarvis শুধু কথা শোনে/বলে (voice engine), brain Main CEO Bot।

সৎ সীমা:
  - Bengali Piper voice-এর মান এখনো কোনো native listener শোনেনি;
    Vosk/sherpa Bengali নির্ভুলতা Boss নিজে কথা বলে যাচাই করবে।
  - Brain mock (default) — voice Jarvis-কে বুদ্ধিমান বানায় না।
  - Mic/speaker ছাড়া এই VM-এ live test হয় না — প্রথম আসল mic test
    Boss-এর PC-তে (VOICE-SETUP.md দেখুন)।

Public functions (Phase 0-র নামই আছে — বদলায়নি):
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
    """Mic থেকে শোনা — Vosk (en) / sherpa-onnx (bn)। Text ফেরত দেয়।"""
    return _listen(seconds=seconds, lang=lang)


def speak(text, lang=DEFAULT_LANG):
    """Boss-কে voice-এ উত্তর দেওয়া — Piper। WAV path ফেরত দেয়।"""
    return _speak(text, lang=lang)


def handle_voice_command(audio_input, lang=DEFAULT_LANG):
    """Voice command -> Main CEO Bot-এর কাছে পাঠানো।

    audio_input str হলে সেটাই শোনা বাক্য ধরে এক turn চালায়; None হলে
    একবার mic-এ শুনে তারপর চালায়। ফেরত: handle_voice_text-এর dict।
    """
    if audio_input is None:
        heard = _listen(seconds=8, lang=lang)
    elif isinstance(audio_input, str):
        heard = audio_input
    else:
        raise TypeError(
            "handle_voice_command: audio_input হতে হবে str (শোনা বাক্য) "
            f"বা None (mic-এ শোনো)। পেলাম: {type(audio_input).__name__}")
    return handle_voice_text(heard, lang=lang)


if __name__ == "__main__":
    print("Jarvis voice — REAL (Piper TTS + Vosk/sherpa-onnx STT, offline, $0)")
    print("ব্যবহার: python scripts/jarvis_voice_loop.py [--lang bn|en]")
    print("এক turn test (text দিয়ে, mic ছাড়া):")
    print(handle_voice_command("আমার আজকের কাজ কী?", lang="bn"))
