"""Piper TTS — Jarvis-এর মুখ (REAL, offline, $0).

Boss-কে voice-এ উত্তর দেওয়ার কাজ: text -> WAV file -> speaker-এ বাজানো।
Piper = free, পুরো offline, neural voice, CPU-তেই চলে (Raspberry Pi-তেও
চলে)। কোনো API key, account, internet, খরচ — কিছুই লাগে না (voice file
একবার download করার পর)।

Voice id — VERIFIED 2026-11-17, upstream voices.json থেকে
(https://huggingface.co/rhasspy/piper-voices — piper-tts package-এর
নিজের VOICES_JSON URL দিয়ে পড়া, 183 voice-এর catalog):
  - bn: "bn_BD-google-medium" — catalog-এর একমাত্র Bengali voice।
    bn_BD (বাংলা, Bangladesh) + bn_IN, 16 speaker, medium, 22,050 Hz,
    ONNX 76,782,515 bytes। Dataset openSLR 37, licence CC-BY-SA-4.0।
  - en: "en_US-lessac-medium" — 1 speaker, medium, 22,050 Hz।
    Dataset Blizzard 2013 Lessac; licence CSTR Edinburgh-এর page-এ —
    personal use OK, commercial use-এর আগে licence দেখে নিতে হবে।

সৎ সীমা:
  - Bengali voice-এর মান এখনো কোনো native listener শোনেনি — কেমন
    শোনায়, সেটা Boss-ই প্রথম শুনে বলবে।
  - Piper শুধু text -> speech; বুদ্ধি brain-এর (mock/small) — voice
    Jarvis-কে বুদ্ধিমান বানায় না।
  - piper-tts না থাকলে / voice file না থাকলে স্পষ্ট error দেয়,
    চুপচাপ ভান করে না।

Stdlib + piper-tts only (piper import function-এর ভেতরে — না থাকলেও
এই module import হয়)।
"""

import os
import wave
from datetime import datetime, timezone

CEO_CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VOICE_DIR = os.path.join(CEO_CORE_DIR, "voice", "models", "piper")
DEFAULT_OUTPUT_DIR = os.path.join(CEO_CORE_DIR, "voice", "output")

# VERIFIED 2026-11-17 — upstream rhasspy/piper-voices voices.json।
VOICE_IDS = {
    "bn": "bn_BD-google-medium",
    "en": "en_US-lessac-medium",
}

VOICE_LICENSE_NOTES = {
    "bn": "CC-BY-SA-4.0 (openSLR 37) — free, personal use OK।",
    "en": "Lessac — licence CSTR Blizzard 2013 page-এ; personal use OK, "
          "commercial use-এর আগে licence দেখুন।",
}

SAMPLE_RATE = 22050


def _require_piper():
    """piper-tts lazy import — না থাকলে exact install command-সহ error।"""
    try:
        import piper  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "piper-tts ইনস্টল নেই। চালান:\n"
            "  pip install piper-tts\n"
            "তারপর voice download করুন (VOICE-SETUP.md দেখুন)।"
        ) from exc
    return piper


def voice_file(lang, voice_dir=None):
    """এই ভাষার .onnx voice file-এর path। না থাকলে download command-সহ error।"""
    lang = (lang or "bn").lower()
    if lang not in VOICE_IDS:
        raise ValueError(
            f"Unknown language {lang!r}. Known: {sorted(VOICE_IDS)}")
    voice_id = VOICE_IDS[lang]
    vdir = voice_dir or DEFAULT_VOICE_DIR
    path = os.path.join(vdir, f"{voice_id}.onnx")
    if not os.path.exists(path):
        raise RuntimeError(
            f"Piper voice file নেই: {path}\n"
            f"Download করুন:\n"
            f"  python -m piper.download_voices {voice_id} "
            f"--download-dir {vdir}\n"
            f"(একবার download করলেই হবে; তারপর offline।)"
        )
    return path


def speak_to_wav(text, lang="bn", out_path=None, voice_dir=None,
                 speaker_id=0):
    """Text -> WAV file। ফেরত দেয় WAV file-এর path।

    lang: "bn" (default — Boss বাংলায় কথা বলে) বা "en"।
    speaker_id: bn voice-এ 0-15 (16 speaker); en-এ 0।
    """
    if not text or not str(text).strip():
        raise ValueError("speak_to_wav: text খালি — বলার মতো কিছু নেই।")
    text = str(text)
    lang = (lang or "bn").lower()
    piper = _require_piper()
    onnx_path = voice_file(lang, voice_dir)

    out_dir = DEFAULT_OUTPUT_DIR
    if out_path is None:
        os.makedirs(out_dir, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        out_path = os.path.join(out_dir, f"jarvis-{lang}-{stamp}.wav")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(out_path))
                    or ".", exist_ok=True)

    voice = piper.PiperVoice.load(onnx_path)
    try:
        syn_config = piper.SynthesisConfig(speaker_id=int(speaker_id))
    except Exception:  # noqa: BLE001 — পুরনো piper-এ speaker_id নাও থাকতে পারে
        syn_config = None
    chunks = (voice.synthesize(text, syn_config=syn_config)
              if syn_config is not None else voice.synthesize(text))

    with wave.open(out_path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wrote = 0
        for chunk in chunks:
            wav.writeframes(chunk.audio_int16_bytes)
            wrote += len(chunk.audio_int16_bytes)
    if wrote == 0 or os.path.getsize(out_path) == 0:
        raise RuntimeError(
            f"Piper WAV খালি হয়ে গেল: {out_path} — text: {text[:60]!r}")
    return out_path


def _play_wav(wav_path):
    """WAV বাজানো (Windows: winsound; Linux: aplay/ffplay চেষ্টা)।

    কোনো player না পেলে False — তখন caller path-টা print করে, চুপ থাকে না।
    """
    try:
        import winsound  # noqa: PLC0415 — Windows stdlib
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        return True
    except Exception:  # noqa: BLE001 — Windows নয়, বা winsound নেই
        pass
    import shutil
    import subprocess
    for player, args in (("aplay", [wav_path]),
                         ("ffplay", ["-nodisp", "-autoexit", wav_path])):
        exe = shutil.which(player)
        if exe is None:
            continue
        try:
            subprocess.run([exe] + args, check=False,
                           capture_output=True, timeout=300)
            return True
        except Exception:  # noqa: BLE001 — পরের player চেষ্টা করো
            continue
    return False


def speak(text, lang="bn", play=True, out_path=None, voice_dir=None,
          speaker_id=0):
    """Text -> voice। WAV লেখে, সম্ভব হলে বাজায়, WAV path ফেরত দেয়।

    Player না থাকলেও WAV path print করে + ফেরত দেয় — কখনো চুপচাপ নয়।
    """
    wav_path = speak_to_wav(text, lang=lang, out_path=out_path,
                            voice_dir=voice_dir, speaker_id=speaker_id)
    played = False
    if play:
        played = _play_wav(wav_path)
    if played:
        print(f"[Jarvis] বললাম ({lang}): {wav_path}")
    else:
        print(f"[Jarvis] WAV লেখা হয়েছে, player পাইনি — শুনুন: {wav_path}")
    return wav_path


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "bn"
    text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    if text is None:
        text = ("আমি জারভিস, শুনছি।" if lang == "bn"
                else "Hello, I am Jarvis.")
    print(speak(text, lang=lang))
