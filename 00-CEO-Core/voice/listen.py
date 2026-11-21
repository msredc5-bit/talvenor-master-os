"""Vosk (en) + sherpa-onnx (bn) — Jarvis's ears (REAL, offline, $0).

Mic -> text (listen) and WAV file -> text (transcribe_file).

Engine choice — VERIFIED 2026-11-17 (not a guess):
  - English ("en"): Vosk, model "vosk-model-small-en-us-0.15" (40 MB,
    Apache-2.0) — official list https://alphacephei.com/vosk/models.html
    (WER 9.85 librispeech test-clean). Download:
    https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
  - Bengali ("bn"): sherpa-onnx, model "vosk-model-small-streaming-bn"
    (HF repo alphacep/vosk-model-small-streaming-bn, ~96 MB, Apache-2.0,
    WER self-reported: Common Voice 17.9, Fleurs 20.6, Banspeech 32.9).
    Why not Vosk: the classic Vosk official models.html list has no
    Bengali model; the one that exists is a Zipformer2 streaming model
    (am-onnx/encoder.onnx + decoder.onnx + joiner.onnx, lang/tokens.txt)
    — vosk.Model() cannot load it (no am/final.mdl + graph/).
    sherpa-onnx is the real way to hear Bengali.

Honest limits:
  - Boss himself will verify Bengali accuracy by speaking to it (WER 17-33% means
    there will be mistakes — a small model, that is the truth).
  - This VM has no PortAudio (no apt candidate) — sounddevice does not
    import, so there is no live mic test here; the WAV test runs via
    transcribe_file. On Windows, the sounddevice wheel bundles PortAudio,
    so the mic works there.
  - Piper's WAV is 22,050 Hz; Vosk/sherpa want 16,000 Hz — resampling happens
    here (stdlib linear interpolation, no extra dependency).

Stdlib + vosk/sherpa_onnx/sounddevice only (those are lazily imported inside
the functions — the module imports even without them).
"""

import json
import os
import queue
import struct
import wave

CEO_CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_DIR = os.path.join(CEO_CORE_DIR, "voice", "models")

SAMPLE_RATE = 16000

# VERIFIED 2026-11-17 — see the sources in the docstring above.
MODEL_IDS = {
    "en": {
        "engine": "vosk",
        "model": "vosk-model-small-en-us-0.15",
        "download_url": "https://alphacephei.com/vosk/models/"
                        "vosk-model-small-en-us-0.15.zip",
        "size_mb": 40,
        "license": "Apache-2.0",
        "source": "https://alphacephei.com/vosk/models.html (official list)",
    },
    "bn": {
        "engine": "sherpa-onnx",
        "model": "vosk-model-small-streaming-bn",
        "repo": "alphacep/vosk-model-small-streaming-bn",
        "size_mb": 96,
        "license": "Apache-2.0",
        "source": "https://huggingface.co/alphacep/"
                  "vosk-model-small-streaming-bn — not on the official Vosk "
                  "models.html list; Zipformer2 streaming model, "
                  "sherpa-onnx only",
        "wer_self_reported": {"Common Voice": 17.9, "Fleurs": 20.6,
                              "Banspeech": 32.9},
    },
}


def _require_vosk():
    try:
        import vosk  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "vosk is not installed. Run:\n  pip install vosk"
        ) from exc
    return vosk


def _require_sherpa():
    try:
        import sherpa_onnx  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "sherpa-onnx is not installed. Run:\n  pip install sherpa-onnx"
        ) from exc
    return sherpa_onnx


def _require_sounddevice():
    try:
        import sounddevice  # noqa: PLC0415
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "sounddevice / PortAudio not found — the mic cannot be heard.\n"
            "On Windows, run:  pip install sounddevice\n"
            "(The Windows wheel bundles PortAudio. This VM has no PortAudio,\n"
            "so there is no mic test here — a WAV transcribe test runs instead.)"
        ) from exc
    return sounddevice


def _vosk_model_path(model_dir=None):
    """English Vosk model dir — with an exact download command in the error if missing."""
    base = model_dir or DEFAULT_MODEL_DIR
    path = os.path.join(base, "vosk", MODEL_IDS["en"]["model"])
    if not os.path.exists(os.path.join(path, "am", "final.mdl")):
        raise RuntimeError(
            f"Vosk English model missing: {path}\n"
            f"Download + unzip:\n"
            f"  {MODEL_IDS['en']['download_url']}\n"
            f"  -> unzip into the {os.path.join(base, 'vosk')} folder."
        )
    return path


def _sherpa_model_files(model_dir=None):
    """The Bengali sherpa model files — with an exact download in the error if missing."""
    base = model_dir or DEFAULT_MODEL_DIR
    mdir = os.path.join(base, "sherpa-bn")
    files = {
        "encoder": os.path.join(mdir, "am-onnx", "encoder.onnx"),
        "decoder": os.path.join(mdir, "am-onnx", "decoder.onnx"),
        "joiner": os.path.join(mdir, "am-onnx", "joiner.onnx"),
        "tokens": os.path.join(mdir, "lang", "tokens.txt"),
        "bpe_vocab": os.path.join(mdir, "lang", "unigram_500.vocab"),
    }
    missing = [k for k, p in files.items() if not os.path.exists(p)]
    if missing:
        raise RuntimeError(
            f"sherpa Bengali model incomplete: missing {missing} "
            f"({mdir})\n"
            f"Download:\n"
            f"  pip install huggingface_hub\n"
            f"  python -c \"from huggingface_hub import snapshot_download; "
            f"snapshot_download('{MODEL_IDS['bn']['repo']}', "
            f"local_dir='{mdir}')\"\n"
            f"(~96 MB, once; then offline.)"
        )
    return files


def _read_wav_mono16(wav_path):
    """Read a WAV (mono, 16-bit) -> (16000, pcm_bytes).

    If Piper's 22,050 Hz, resample to 16,000 Hz (stdlib linear
    interpolation) — both Vosk/sherpa want 16 kHz.
    """
    with wave.open(wav_path, "rb") as wav:
        nchannels = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
    if nchannels != 1 or sampwidth != 2:
        raise ValueError(
            f"WAV must be mono 16-bit PCM: {wav_path} "
            f"(channels={nchannels}, sampwidth={sampwidth})")
    if rate == SAMPLE_RATE:
        return SAMPLE_RATE, frames
    return SAMPLE_RATE, _resample_pcm16(frames, rate, SAMPLE_RATE)


def _resample_pcm16(pcm_bytes, src_rate, dst_rate):
    """Linear-interpolation resample (16-bit PCM) — stdlib only."""
    n_in = len(pcm_bytes) // 2
    samples = struct.unpack(f"<{n_in}h", pcm_bytes)
    n_out = max(1, int(n_in * dst_rate / src_rate))
    out = bytearray()
    for i in range(n_out):
        pos = i * (n_in - 1) / max(1, n_out - 1)
        j = int(pos)
        frac = pos - j
        s0 = samples[j]
        s1 = samples[min(j + 1, n_in - 1)]
        out += struct.pack("<h", int(s0 + (s1 - s0) * frac))
    return bytes(out)


def _transcribe_vosk_file(wav_path, model_dir=None):
    vosk = _require_vosk()
    _rate, pcm = _read_wav_mono16(wav_path)
    model = vosk.Model(_vosk_model_path(model_dir))
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    text_parts = []
    chunk = 4000
    for i in range(0, len(pcm), chunk):
        if rec.AcceptWaveform(pcm[i:i + chunk]):
            text_parts.append(json.loads(rec.Result()).get("text", ""))
    text_parts.append(json.loads(rec.FinalResult()).get("text", ""))
    return " ".join(p for p in text_parts if p).strip()


def _transcribe_sherpa_file(wav_path, model_dir=None):
    sherpa_onnx = _require_sherpa()
    import numpy as np  # noqa: PLC0415 — a sherpa-onnx dependency
    _rate, pcm = _read_wav_mono16(wav_path)
    files = _sherpa_model_files(model_dir)
    # Zipformer2 streaming model — it does not load with OfflineRecognizer
    # (a C++ abort on the encoder input int32/int64 check, sherpa-onnx 2.0.1).
    # So OnlineRecognizer, like the model's own decode.py.
    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=files["tokens"], encoder=files["encoder"],
        decoder=files["decoder"], joiner=files["joiner"],
        num_threads=2, sample_rate=SAMPLE_RATE, dither=3e-5,
        decoding_method="modified_beam_search", max_active_paths=10,
        model_type="zipformer2", provider="cpu")
    samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    stream = recognizer.create_stream()
    stream.accept_waveform(SAMPLE_RATE, samples)
    tail = np.zeros(int(SAMPLE_RATE * 1.0), dtype=np.float32)
    stream.accept_waveform(SAMPLE_RATE, tail)
    stream.input_finished()
    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)
    return recognizer.get_result(stream).strip()


def transcribe_file(wav_path, lang="bn", model_dir=None):
    """WAV file -> text. No mic needed — the headless test path."""
    lang = (lang or "bn").lower()
    if lang not in MODEL_IDS:
        raise ValueError(
            f"Unknown language {lang!r}. Known: {sorted(MODEL_IDS)}")
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV file missing: {wav_path}")
    if lang == "en":
        return _transcribe_vosk_file(wav_path, model_dir)
    return _transcribe_sherpa_file(wav_path, model_dir)


def listen(seconds=8, lang="bn", model_dir=None, device=None):
    """Listen from the mic — record `seconds` seconds and return text.

    lang "bn" (default) or "en". Without a mic/sounddevice, a clear
    RuntimeError — never a silent empty string.
    """
    lang = (lang or "bn").lower()
    if lang not in MODEL_IDS:
        raise ValueError(
            f"Unknown language {lang!r}. Known: {sorted(MODEL_IDS)}")
    sd = _require_sounddevice()
    import numpy as np  # noqa: PLC0415 — sounddevice/sherpa companion

    chunks = []
    q = queue.Queue()

    def _callback(indata, _frames, _time, status):
        if status:
            print(f"[listen] mic status: {status}")
        q.put(bytes(indata))

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                            dtype="int16", device=device,
                            callback=_callback):
            import time
            end = time.time() + max(1, int(seconds))
            while time.time() < end:
                try:
                    chunks.append(q.get(timeout=1))
                except queue.Empty:
                    continue
    except Exception as exc:
        raise RuntimeError(
            f"Could not open the mic ({type(exc).__name__}: {exc}). "
            "Check whether the mic is plugged in / permitted."
        ) from exc
    if not chunks:
        return ""

    if lang == "en":
        vosk = _require_vosk()
        model = vosk.Model(_vosk_model_path(model_dir))
        rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
        text_parts = []
        for data in chunks:
            if rec.AcceptWaveform(data):
                text_parts.append(json.loads(rec.Result()).get("text", ""))
        text_parts.append(json.loads(rec.FinalResult()).get("text", ""))
        return " ".join(p for p in text_parts if p).strip()

    sherpa_onnx = _require_sherpa()
    files = _sherpa_model_files(model_dir)
    # The model's own decode.py config (Zipformer2) — without modeling_unit /
    # bpe_vocab, exactly as decode.py does it.
    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=files["tokens"], encoder=files["encoder"],
        decoder=files["decoder"], joiner=files["joiner"],
        num_threads=2, sample_rate=SAMPLE_RATE, dither=3e-5,
        decoding_method="modified_beam_search", max_active_paths=10,
        model_type="zipformer2", provider="cpu")
    stream = recognizer.create_stream()
    for data in chunks:
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        samples /= 32768.0
        stream.accept_waveform(SAMPLE_RATE, samples)
    stream.input_finished()
    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)
    return recognizer.get_result(stream).strip()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Listen from the mic (Vosk en / sherpa-onnx bn) — offline, $0")
    parser.add_argument("--lang", default="bn", choices=["bn", "en"])
    parser.add_argument("--seconds", type=int, default=8)
    args = parser.parse_args()
    print(listen(seconds=args.seconds, lang=args.lang))
