"""Piper TTS — Jarvis's mouth (REAL, offline, $0).

The job of answering Boss by voice: text -> WAV file -> played on the speaker.
Piper = free, fully offline, neural voice, runs on CPU (even on a Raspberry Pi).
No API key, account, internet, or cost — nothing is needed (after the voice file
is downloaded once).

Voice id — VERIFIED 2026-11-17, from upstream voices.json
(https://huggingface.co/rhasspy/piper-voices — read via the piper-tts package's
own VOICES_JSON URL, a catalog of 183 voices):
  - bn: "bn_BD-google-medium" — the catalog's only Bengali voice.
    bn_BD (Bengali, Bangladesh) + bn_IN, 16 speaker, medium, 22,050 Hz,
    ONNX 76,782,515 bytes. Dataset openSLR 37, licence CC-BY-SA-4.0.
  - en: "en_US-lessac-medium" — 1 speaker, medium, 22,050 Hz.
    Dataset Blizzard 2013 Lessac; licence on CSTR Edinburgh's page —
    personal use OK; check the licence before commercial use.

Honest limits:
  - No native listener has heard the quality of the Bengali voice yet — how it
    sounds, Boss himself will be the first to hear and say.
  - Piper is only text -> speech; the intelligence is the brain's (mock/small) — voice
    does not make Jarvis intelligent.
  - Without piper-tts / without the voice file, it gives a clear error;
    it never silently pretends.

Stdlib + piper-tts only (the piper import is inside the functions — the module
imports even without it).
"""

import os
import wave
from datetime import datetime, timezone

CEO_CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VOICE_DIR = os.path.join(CEO_CORE_DIR, "voice", "models", "piper")
DEFAULT_OUTPUT_DIR = os.path.join(CEO_CORE_DIR, "voice", "output")

# VERIFIED 2026-11-17 — upstream rhasspy/piper-voices voices.json.
VOICE_IDS = {
    "bn": "bn_BD-google-medium",
    "en": "en_US-lessac-medium",
}

VOICE_LICENSE_NOTES = {
    "bn": "CC-BY-SA-4.0 (openSLR 37) — free, personal use OK.",
    "en": "Lessac — licence on the CSTR Blizzard 2013 page; personal use OK, "
          "check the licence before commercial use.",
}

SAMPLE_RATE = 22050


def _require_piper():
    """piper-tts lazy import — with an exact install command in the error if missing."""
    try:
        import piper  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "piper-tts is not installed. Run:\n"
            "  pip install piper-tts\n"
            "Then download the voice (see VOICE-SETUP.md)."
        ) from exc
    return piper


def voice_file(lang, voice_dir=None):
    """The path of this language's .onnx voice file. With a download command in the error if missing."""
    lang = (lang or "bn").lower()
    if lang not in VOICE_IDS:
        raise ValueError(
            f"Unknown language {lang!r}. Known: {sorted(VOICE_IDS)}")
    voice_id = VOICE_IDS[lang]
    vdir = voice_dir or DEFAULT_VOICE_DIR
    path = os.path.join(vdir, f"{voice_id}.onnx")
    if not os.path.exists(path):
        raise RuntimeError(
            f"Piper voice file missing: {path}\n"
            f"Download:\n"
            f"  python -m piper.download_voices {voice_id} "
            f"--download-dir {vdir}\n"
            f"(Downloading once is enough; then offline.)"
        )
    return path


def speak_to_wav(text, lang="bn", out_path=None, voice_dir=None,
                 speaker_id=0):
    """Text -> WAV file. Returns the WAV file's path.

    lang: "bn" (default — Boss speaks Bengali) or "en".
    speaker_id: 0-15 for the bn voice (16 speakers); 0 for en.
    """
    if not text or not str(text).strip():
        raise ValueError("speak_to_wav: text is empty — nothing to say.")
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
    except Exception:  # noqa: BLE001 — an old piper may not have speaker_id
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
            f"Piper WAV came out empty: {out_path} — text: {text[:60]!r}")
    return out_path


def _play_wav(wav_path):
    """Play a WAV (Windows: winsound; Linux: try aplay/ffplay).

    False if no player is found — then the caller prints the path; it never stays silent.
    """
    try:
        import winsound  # noqa: PLC0415 — Windows stdlib
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        return True
    except Exception:  # noqa: BLE001 — not Windows, or no winsound
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
        except Exception:  # noqa: BLE001 — try the next player
            continue
    return False


def speak(text, lang="bn", play=True, out_path=None, voice_dir=None,
          speaker_id=0):
    """Text -> voice. Writes the WAV, plays it if possible, returns the WAV path.

    Even without a player, it prints the WAV path + returns it — never silent.
    """
    wav_path = speak_to_wav(text, lang=lang, out_path=out_path,
                            voice_dir=voice_dir, speaker_id=speaker_id)
    played = False
    if play:
        played = _play_wav(wav_path)
    if played:
        print(f"[Jarvis] said it ({lang}): {wav_path}")
    else:
        print(f"[Jarvis] WAV written, no player found — listen here: {wav_path}")
    return wav_path


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "bn"
    text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    if text is None:
        text = ("I am Jarvis, listening." if lang == "bn"
                else "Hello, I am Jarvis.")
    print(speak(text, lang=lang))
