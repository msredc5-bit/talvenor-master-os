#!/usr/bin/env python3
"""Voice headless self-test — Jarvis voice loop (no mic/speaker needed).

Verifies (Piper TTS + Vosk/sherpa-onnx STT, offline, $0):
  1. piper-tts imports
  2. upstream voices.json has bn_BD-google-medium + en_US-lessac-medium
     (read via piper-tts package's own VOICES_JSON URL)
  3. Both voices download (if missing; with md5 verification)
  4. English synth: "Hello, I am Jarvis." -> WAV (valid header, non-empty)
  5. Bengali synth: "আমি জারভিস, শুনছি।" -> WAV (valid header, non-empty)
  6. English WAV -> Vosk transcribe: "jarvis" (and at least one of hello/i/am
     must be present)
  7. Bengali WAV -> sherpa-onnx transcribe: Bengali characters must be present
     (WER 17-33%, so exact-word match is not claimed — what is verified is whether
     the pipeline works)

No mic/speaker needed — runs on this VM too. Model download needs network
(once only; offline after that).

Usage: python3 scripts/voice_test.py [--models-dir ...] [--skip-bn-stt]
Exit 0 = all PASS; 1 = some FAIL (the reason is printed, no pretence).
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

from voice.listen import MODEL_IDS, transcribe_file  # noqa: E402
from voice.speak import VOICE_IDS, speak_to_wav  # noqa: E402

EN_TEXT = "Hello, I am Jarvis."
BN_TEXT = "আমি জারভিস, শুনছি।"
BN_RE = re.compile(r"[\u0980-\u09ff]")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))


def wav_is_valid(path):
    """WAV exists + non-empty + valid header + mono 16-bit + frames > 0."""
    try:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return False, "file missing or empty"
        with wave.open(path, "rb") as wav:
            if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
                return False, (f"channels={wav.getnchannels()}, "
                               f"sampwidth={wav.getsampwidth()}")
            if wav.getnframes() == 0:
                return False, "0 frames"
            return True, (f"{os.path.getsize(path)} B, "
                          f"{wav.getframerate()} Hz, "
                          f"{wav.getnframes()} frames")
    except Exception as e:  # noqa: BLE001 — FAIL with detail
        return False, f"{type(e).__name__}: {e}"


def ensure_piper_voices(model_dir):
    """Piper voice download (with piper-tts's own downloader)."""
    import piper.download_voices as dv  # noqa: PLC0415
    piper_dir = os.path.join(model_dir, "piper")
    os.makedirs(piper_dir, exist_ok=True)
    for voice_id in (VOICE_IDS["bn"], VOICE_IDS["en"]):
        onnx = os.path.join(piper_dir, f"{voice_id}.onnx")
        if os.path.exists(onnx) and os.path.getsize(onnx) > 0:
            print(f"  voice exists: {voice_id}")
            continue
        print(f"  downloading voice: {voice_id} ...")
        dv.download_voice(voice_id, piper_dir)


def ensure_vosk_model(model_dir):
    """Vosk en model zip download + unzip (if missing)."""
    import zipfile  # noqa: PLC0415
    vosk_dir = os.path.join(model_dir, "vosk")
    model_dir_path = os.path.join(vosk_dir, MODEL_IDS["en"]["model"])
    if os.path.exists(os.path.join(model_dir_path, "am", "final.mdl")):
        print(f"  vosk model exists: {MODEL_IDS['en']['model']}")
        return
    os.makedirs(vosk_dir, exist_ok=True)
    zippath = os.path.join(vosk_dir, "vosk-model-small-en-us-0.15.zip")
    if not os.path.exists(zippath):
        print("  downloading vosk en model zip (40 MB) ...")
        req = urllib.request.Request(
            MODEL_IDS["en"]["download_url"],
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=300) as r, \
                open(zippath, "wb") as f:
            f.write(r.read())
    print("  unzipping vosk en model ...")
    with zipfile.ZipFile(zippath) as z:
        z.extractall(vosk_dir)


def ensure_sherpa_model(model_dir):
    """Sherpa bn model download (huggingface_hub snapshot_download)."""
    from huggingface_hub import snapshot_download  # noqa: PLC0415
    sherpa_dir = os.path.join(model_dir, "sherpa-bn")
    need = ["am-onnx/encoder.onnx", "am-onnx/decoder.onnx",
            "am-onnx/joiner.onnx", "lang/tokens.txt",
            "lang/unigram_500.vocab"]
    if all(os.path.exists(os.path.join(sherpa_dir, p)) for p in need):
        print(f"  sherpa model exists: {MODEL_IDS['bn']['model']}")
        return
    print("  downloading sherpa bn model (~96 MB) ...")
    snapshot_download(MODEL_IDS["bn"]["repo"], local_dir=sherpa_dir)


def main():
    parser = argparse.ArgumentParser(description="Jarvis voice headless test")
    parser.add_argument("--models-dir", default=os.path.join(
        CEO_CORE_DIR, "voice", "models"))
    parser.add_argument("--skip-bn-stt", action="store_true",
                        help="skip the Bengali STT check (if the model is missing)")
    args = parser.parse_args()
    model_dir = args.models_dir
    out_dir = os.path.join(CEO_CORE_DIR, "voice", "output")
    os.makedirs(out_dir, exist_ok=True)

    # 1. piper import
    try:
        import piper  # noqa: PLC0415
        check("piper-tts import", True,
              getattr(piper, "__version__", "version n/a"))
    except ImportError as e:
        check("piper-tts import", False,
              "run pip install piper-tts — " + str(e))
        return _finish()

    # 2. upstream voices.json has both voices
    try:
        import piper.download_voices as dv  # noqa: PLC0415
        with urllib.request.urlopen(dv.VOICES_JSON, timeout=60) as r:
            voices = json.load(r)
        bn_ok = VOICE_IDS["bn"] in voices
        en_ok = VOICE_IDS["en"] in voices
        check("upstream voices.json has bn + en voices", bn_ok and en_ok,
              f"bn={VOICE_IDS['bn']}: {bn_ok}, "
              f"en={VOICE_IDS['en']}: {en_ok}, total {len(voices)} voices")
    except Exception as e:  # noqa: BLE001
        check("upstream voices.json has bn + en voices", False,
              f"{type(e).__name__}: {e}")
        return _finish()

    # 3. voice download
    try:
        ensure_piper_voices(model_dir)
        check("Piper voice files (bn + en) exist", all(
            os.path.exists(os.path.join(
                model_dir, "piper", f"{v}.onnx")) for v in VOICE_IDS.values()))
    except Exception as e:  # noqa: BLE001
        check("Piper voice files (bn + en) exist", False,
              f"{type(e).__name__}: {e}")
        return _finish()

    # 4+5. synth en + bn
    wav_paths = {}
    for lang, text in (("en", EN_TEXT), ("bn", BN_TEXT)):
        try:
            path = speak_to_wav(
                text, lang=lang,
                out_path=os.path.join(out_dir, f"voice-test-{lang}.wav"),
                voice_dir=os.path.join(model_dir, "piper"))
            wav_paths[lang] = path
            ok, detail = wav_is_valid(path)
            check(f"Piper synth ({lang}): {text!r}", ok, detail)
        except Exception as e:  # noqa: BLE001
            check(f"Piper synth ({lang}): {text!r}", False,
                  f"{type(e).__name__}: {e}")

    # 6. en WAV -> Vosk
    if "en" in wav_paths:
        try:
            ensure_vosk_model(model_dir)
            text = transcribe_file(wav_paths["en"], lang="en",
                                   model_dir=model_dir)
            words = set(text.lower().split())
            hit = words & {"hello", "i", "am", "jarvis"}
            check("Vosk transcribe (en WAV)", "jarvis" in words and len(hit) >= 2,
                  f"transcript: {text!r} (matches: {sorted(hit)})")
        except Exception as e:  # noqa: BLE001
            check("Vosk transcribe (en WAV)", False,
                  f"{type(e).__name__}: {e}")
    else:
        check("Vosk transcribe (en WAV)", False, "en WAV could not be made")

    # 7. bn WAV -> sherpa-onnx
    if args.skip_bn_stt:
        check("sherpa transcribe (bn WAV)", False, "SKIPPED --skip-bn-stt")
    elif "bn" in wav_paths:
        try:
            ensure_sherpa_model(model_dir)
            text = transcribe_file(wav_paths["bn"], lang="bn",
                                   model_dir=model_dir)
            has_bn = bool(BN_RE.search(text))
            check("sherpa transcribe (bn WAV)", has_bn,
                  f"transcript: {text!r}")
        except Exception as e:  # noqa: BLE001
            check("sherpa transcribe (bn WAV)", False,
                  f"{type(e).__name__}: {e}")
    else:
        check("sherpa transcribe (bn WAV)", False, "bn WAV could not be made")

    return _finish()


def _finish():
    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} voice checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Voice headless test: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
