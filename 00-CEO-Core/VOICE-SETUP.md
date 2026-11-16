# Jarvis Voice Setup — Windows (Boss-এর PC)

Jarvis-এর কান + মুখ — **পুরো offline, $0**। একবার install + download
করলেই হবে; তারপর internet ছাড়াই চলবে।

## কী কী লাগবে

| জিনিস | কাজ | খরচ |
|---|---|---|
| Python 3.10+ (Windows) | voice code চালানো | $0 |
| `piper-tts` | বলা (TTS) — neural voice, CPU-তে চলে | $0 |
| `vosk` | শোনা (STT, English) | $0 |
| `sherpa-onnx` | শোনা (STT, Bengali) | $0 |
| `sounddevice` | mic ধরা (Windows wheel-এ PortAudio বান্ডেল থাকে) | $0 |
| Voice/model file (একবার download) | bn voice 73 MB + en voice ~15 MB + Vosk en 40 MB + sherpa bn 96 MB | $0 |

## ধাপ ১ — Python আছে কিনা দেখুন

PowerShell / Command Prompt-এ:

```bat
python --version
```

`Python 3.10` বা তার বেশি দেখাতে হবে। না থাকলে python.org থেকে
ডাউনলোড করুন (install-এর সময় **"Add Python to PATH"** টিক দিন)।

## ধাপ ২ — Package install

Repo-র root থেকে (যেখানে `talvenor-master-os` folder):

```bat
pip install piper-tts vosk sounddevice sherpa-onnx
```

## ধাপ ৩ — Voice + model download (একবারই)

```bat
:: Piper voice (Bengali + English) — এক command-এ দুইটা
python -m piper.download_voices bn_BD-google-medium en_US-lessac-medium --download-dir 00-CEO-Core\voice\models\piper

:: Vosk English model (40 MB) — zip download করে unzip করুন
:: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
:: unzip-এর পর এই folder-টা থাকতে হবে:
::   00-CEO-Core\voice\models\vosk\vosk-model-small-en-us-0.15\am\final.mdl

:: Sherpa Bengali model (~96 MB)
pip install huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download('alphacep/vosk-model-small-streaming-bn', local_dir='00-CEO-Core/voice/models/sherpa-bn')"
```

Voice id — VERIFIED (upstream থেকে, অনুমান নয়):
- **Bengali বলা:** `bn_BD-google-medium` — Piper catalog-এর একমাত্র
  Bengali voice (bn_BD, 16 speaker, medium, 22,050 Hz, openSLR 37,
  licence CC-BY-SA-4.0)।
- **English বলা:** `en_US-lessac-medium` — 1 speaker, medium।
  Lessac licence CSTR Blizzard 2013 page-এ — personal use OK,
  commercial use-এর আগে licence দেখুন।
- **English শোনা:** `vosk-model-small-en-us-0.15` (Vosk official list-এ
  আছে, Apache-2.0)।
- **Bengali শোনা:** `vosk-model-small-streaming-bn` (HF repo
  `alphacep/vosk-model-small-streaming-bn`, Apache-2.0, WER self-reported:
  Common Voice 17.9, Fleurs 20.6, Banspeech 32.9)।
  সত্য কথা: classic Vosk-এর official list-এ কোনো Bengali model নেই;
  যেটা আছে সেটা Zipformer2 streaming model — তাই Bengali শোনে
  sherpa-onnx, Vosk নয়। `vosk.Model()` দিয়ে এটা লোড হয় না।

## ধাপ ৪ — Test চালান (mic/speaker ছাড়াই)

```bat
python scripts\voice_test.py
```

সব PASS হলে: দুই voice-এ synth হয়েছে, English WAV Vosk চিনেছে,
Bengali WAV sherpa চিনেছে। WAV file থাকে
`00-CEO-Core\voice\output\voice-test-bn.wav` /
`voice-test-en.wav`-এ — নিজে শুনে দেখুন Bengali voice কেমন শোনায়।

আর check:

```bat
python scripts\check_voice.py
```

## ধাপ ৫ — Voice loop চালান (আসল Jarvis)

```bat
python scripts\jarvis_voice_loop.py
```

- বাংলায় বলুন (default `bn`) — Jarvis শুনে brain-এর উত্তর বলবে।
- English-এ বলতে চাইলে: `python scripts\jarvis_voice_loop.py --lang en`
- থামাতে: `Ctrl+C`
- একবারে ৮ সেকেন্ড শোনে (বদলাতে: `--seconds 12`)।

## RAM নোট (জরুরি)

আপনার PC: 8 GB RAM, খালি মাত্র ~1.4 GB। Voice চালানোর সময় **Chrome
বন্ধ রাখুন** — Piper + Vosk/sherpa একসাথে ~1 GB RAM নেয়। Chrome খোলা
থাকলে আটকে যেতে পারে।

## সমস্যা হলে

| সমস্যা | করণীয় |
|---|---|
| `piper-tts ইনস্টল নেই` | ধাপ ২ আবার চালান |
| `Piper voice file নেই` | ধাপ ৩-এর piper command চালান |
| `Vosk English model নেই` | zip download + unzip, folder path মেলান |
| `sherpa Bengali model অসম্পূর্ণ` | ধাপ ৩-এর snapshot_download চালান |
| `sounddevice / PortAudio পাওয়া যায়নি` | `pip install sounddevice` (Windows wheel-এ PortAudio থাকে) |
| `Mic খুলতে পারলাম না` | Mic লাগানো + Windows Settings-এ mic অনুমতি আছে কিনা দেখুন |
| কথা শুনে ভুল লেখে | স্বাভাবিক — ছোট model (Bengali WER 17-33%)। ধীরে, পরিষ্কার করে বলুন; শোরগোল কমান |

## সৎ সীমা (আগে জানুন)

- **Bengali voice-এর মান কেউ শোনেনি** — কেমন শোনায়, আপনিই প্রথম
  শুনে বলবেন। ভালো না লাগলে speaker বদলানো যায় (bn voice-এ 16 speaker;
  `speak.py`-তে `speaker_id=0..15`)।
- **Bengali শোনায় ভুল হবে** — ছোট model, WER 17-33%। ছোট, পরিষ্কার
  বাক্য বলুন।
- **Brain mock** — voice Jarvis-কে বুদ্ধিমান বানায় না। উত্তর হবে
  mock draft ("MOCK-PLAN: ...")। আসল বুদ্ধির জন্য brain `live` করতে
  হয় — সেটা আলাদা সিদ্ধান্ত (Boss-এর কথায়, live verification-এর পর)।
- **Voice-এ gated কাজ হয় না** — "send" / "post it" বললে শুধু
  ApprovalGateway-এ PENDING লেখা হয়; execute হয় না। Boss-এর gate
  word (টাইপ করা) ছাড়া কিছুই এগোয় না।
- **"upload it" / খরচ / delete voice-এ request করা যায় না** — ওগুলো
  Boss টাইপ করে দেবে।

## File কোথায়

```
00-CEO-Core/
├── jarvis_voice.py      # REAL — listen()/speak()/handle_voice_command()
├── VOICE-SETUP.md       # এই file
└── voice/
    ├── speak.py         # Piper TTS
    ├── listen.py        # Vosk (en) + sherpa-onnx (bn)
    ├── loop.py          # শোনা -> brain -> বলা + gate
    ├── models/          # voice/model file (git-এ যায় না — .gitignore)
    │   ├── piper/       # *.onnx voice
    │   ├── vosk/        # vosk-model-small-en-us-0.15/
    │   └── sherpa-bn/   # am-onnx/ + lang/
    └── output/          # বানানো WAV (git-এ যায় না)
scripts/
├── voice_test.py        # headless test (mic ছাড়া)
├── check_voice.py       # voice check suite
└── jarvis_voice_loop.py # PC-তে চালানোর entry
```
