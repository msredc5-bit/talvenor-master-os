#!/usr/bin/env python3
"""Jarvis voice loop — entry to run on Boss's PC (Windows/Linux).

From the repo root:
  python scripts/jarvis_voice_loop.py [--lang bn|en] [--seconds 8]
  [--turns N] [--business agency]

What you need (see VOICE-SETUP.md):
  pip install piper-tts vosk sounddevice sherpa-onnx
  + Piper voice (bn_BD-google-medium / en_US-lessac-medium)
  + Vosk en model + sherpa bn model (download once)

Gated work (send/publish) by voice only becomes PENDING in the ApprovalGateway —
never executes, does not move forward without Boss's gate word.
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
        description="Jarvis voice loop — listen -> brain -> speak (offline, $0)")
    parser.add_argument("--lang", default="bn", choices=["bn", "en"],
                        help="the language Boss will speak (default: bn)")
    parser.add_argument("--seconds", type=int, default=8,
                        help="how many seconds to listen per turn (default: 8)")
    parser.add_argument("--turns", type=int, default=None,
                        help="after how many turns to stop (default: until Ctrl+C)")
    parser.add_argument("--business", default="agency",
                        help="which department the brain is for (default: agency)")
    args = parser.parse_args()
    return run_voice_loop(lang=args.lang, seconds=args.seconds,
                          max_turns=args.turns,
                          brain_department=args.business)


if __name__ == "__main__":
    sys.exit(0 if main() is not None else 0)
