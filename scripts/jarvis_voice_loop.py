#!/usr/bin/env python3
"""Jarvis voice loop — Boss-এর PC-তে চালানোর entry (Windows/Linux)।

Repo root থেকে:
  python scripts/jarvis_voice_loop.py [--lang bn|en] [--seconds 8]
  [--turns N] [--business agency]

কী লাগে (VOICE-SETUP.md দেখুন):
  pip install piper-tts vosk sounddevice sherpa-onnx
  + Piper voice (bn_BD-google-medium / en_US-lessac-medium)
  + Vosk en model + sherpa bn model (একবার download)

Gated কাজ (send/publish) voice-এ শুধু ApprovalGateway-এ PENDING হয় —
execute হয় না, Boss-এর gate word ছাড়া এগোয় না।
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

from voice.loop import run_voice_loop  # noqa: E402


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Jarvis voice loop — শোনা -> brain -> বলা (offline, $0)")
    parser.add_argument("--lang", default="bn", choices=["bn", "en"],
                        help="Boss যে ভাষায় কথা বলবে (default: bn)")
    parser.add_argument("--seconds", type=int, default=8,
                        help="প্রতি turn-এ কত সেকেন্ড শুনবে (default: 8)")
    parser.add_argument("--turns", type=int, default=None,
                        help="কয় turn পর থামবে (default: Ctrl+C পর্যন্ত)")
    parser.add_argument("--business", default="agency",
                        help="brain কোন department-এর (default: agency)")
    args = parser.parse_args()
    return run_voice_loop(lang=args.lang, seconds=args.seconds,
                          max_turns=args.turns,
                          brain_department=args.business)


if __name__ == "__main__":
    sys.exit(0 if main() is not None else 0)
