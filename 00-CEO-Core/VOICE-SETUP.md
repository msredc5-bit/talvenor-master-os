# Jarvis Voice Setup — Windows (Boss's PC)

Jarvis's ears + mouth — **fully offline, $0**. Install + download once;
then it runs without internet.

## What is needed

| Item | Job | Cost |
|---|---|---|
| Python 3.10+ (Windows) | Run the voice code | $0 |
| `piper-tts` | Speaking (TTS) — neural voice, runs on CPU | $0 |
| `vosk` | Listening (STT, English) | $0 |
| `sherpa-onnx` | Listening (STT, Bengali) | $0 |
| `sounddevice` | Capturing the mic (the Windows wheel bundles PortAudio) | $0 |
| Voice/model files (one download) | bn voice 73 MB + en voice ~15 MB + Vosk en 40 MB + sherpa bn 96 MB | $0 |

## Step 1 — Check whether Python is installed

In PowerShell / Command Prompt:

```bat
python --version
```

It must show `Python 3.10` or higher. If not, download it from python.org
(tick **"Add Python to PATH"** during install).

## Step 2 — Install packages

From the repo root (where the `talvenor-master-os` folder is):

```bat
pip install piper-tts vosk sounddevice sherpa-onnx
```

## Step 3 — Download voices + models (once)

```bat
:: Piper voices (Bengali + English) — both in one command
python -m piper.download_voices bn_BD-google-medium en_US-lessac-medium --download-dir 00-CEO-Core\voice\models\piper

:: Vosk English model (40 MB) — download the zip and unzip it
:: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
:: After unzipping, this folder must exist:
::   00-CEO-Core\voice\models\vosk\vosk-model-small-en-us-0.15\am\final.mdl

:: Sherpa Bengali model (~96 MB)
pip install huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download('alphacep/vosk-model-small-streaming-bn', local_dir='00-CEO-Core/voice/models/sherpa-bn')"
```

Voice ids — VERIFIED (from upstream, not a guess):
- **Speaking Bengali:** `bn_BD-google-medium` — the Piper catalog's only
  Bengali voice (bn_BD, 16 speakers, medium, 22,050 Hz, openSLR 37,
  licence CC-BY-SA-4.0).
- **Speaking English:** `en_US-lessac-medium` — 1 speaker, medium.
  Lessac licence on the CSTR Blizzard 2013 page — personal use OK;
  check the licence before commercial use.
- **Hearing English:** `vosk-model-small-en-us-0.15` (on the Vosk official list,
  Apache-2.0).
- **Hearing Bengali:** `vosk-model-small-streaming-bn` (HF repo
  `alphacep/vosk-model-small-streaming-bn`, Apache-2.0, WER self-reported:
  Common Voice 17.9, Fleurs 20.6, Banspeech 32.9).
  The truth: the classic Vosk official list has no Bengali model;
  the one that exists is a Zipformer2 streaming model — so Bengali is heard by
  sherpa-onnx, not Vosk. It does not load with `vosk.Model()`.

## Step 4 — Run the test (no mic/speaker needed)

```bat
python scripts\voice_test.py
```

If all PASS: both voices synthesized, the English WAV was recognised by Vosk,
the Bengali WAV by sherpa. The WAV files live in
`00-CEO-Core\voice\output\voice-test-bn.wav` /
`voice-test-en.wav` — listen for yourself to hear how the Bengali voice sounds.

And check:

```bat
python scripts\check_voice.py
```

## Step 5 — Run the voice loop (the real Jarvis)

```bat
python scripts\jarvis_voice_loop.py
```

- Speak in Bengali (default `bn`) — Jarvis listens and speaks the brain's answer.
- To speak English: `python scripts\jarvis_voice_loop.py --lang en`
- To stop: `Ctrl+C`
- It listens for 8 seconds at a time (to change: `--seconds 12`).

## RAM note (important)

Your PC: 8 GB RAM, only ~1.4 GB free. While running voice, keep **Chrome
closed** — Piper + Vosk/sherpa together take ~1 GB RAM. With Chrome open,
it may freeze.

## If something goes wrong

| Problem | What to do |
|---|---|
| `piper-tts is not installed` | Run step 2 again |
| `Piper voice file missing` | Run the step 3 piper command |
| `Vosk English model missing` | Download + unzip the zip, match the folder path |
| `sherpa Bengali model incomplete` | Run the step 3 snapshot_download |
| `sounddevice / PortAudio not found` | `pip install sounddevice` (the Windows wheel has PortAudio) |
| `Could not open the mic` | Check the mic is plugged in + mic permission in Windows Settings |
| It hears speech but writes it wrong | Normal — a small model (Bengali WER 17-33%). Speak slowly and clearly; reduce background noise |

## Honest limits (know these first)

- **Nobody has heard the Bengali voice's quality** — how it sounds, you will be
  the first to hear and say. If you do not like it, the speaker can be changed
  (the bn voice has 16 speakers; `speak.py` `speaker_id=0..15`).
- **Hearing Bengali will make mistakes** — a small model, WER 17-33%. Speak in
  short, clear sentences.
- **Brain mock** — voice does not make Jarvis intelligent. The answer will be
  a mock draft ("MOCK-PLAN: ..."). For real intelligence, the brain must go `live`
  — that is a separate decision (on Boss's word, after live verification).
- **No gated work by voice** — saying "send" / "post it" only writes PENDING
  to the ApprovalGateway; nothing executes. Nothing moves without Boss's gate
  word (typed).
- **"upload it" / spend / delete cannot be requested by voice** — Boss
  types those.

## Where the files are

```
00-CEO-Core/
├── jarvis_voice.py      # REAL — listen()/speak()/handle_voice_command()
├── VOICE-SETUP.md       # this file
└── voice/
    ├── speak.py         # Piper TTS
    ├── listen.py        # Vosk (en) + sherpa-onnx (bn)
    ├── loop.py          # listen -> brain -> speak + gate
    ├── models/          # voice/model files (not in git — .gitignore)
    │   ├── piper/       # *.onnx voice
    │   ├── vosk/        # vosk-model-small-en-us-0.15/
    │   └── sherpa-bn/   # am-onnx/ + lang/
    └── output/          # generated WAVs (not in git)
scripts/
├── voice_test.py        # headless test (no mic)
├── check_voice.py       # voice check suite
└── jarvis_voice_loop.py # entry point to run on the PC
```
