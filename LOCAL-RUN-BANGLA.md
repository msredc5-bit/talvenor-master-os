# Talvenor Master OS — PC-তে Locally চালানো (বাংলা গাইড)

## যা লাগবে (একবার)

1. **Python 3.10+** — [python.org](https://www.python.org/downloads/) থেকে install। Install-এর সময় **"Add Python to PATH" টিক দিতেই হবে**।
2. **Repo-টা** — Git থাকলে: `git clone https://github.com/msredc5-bit/talvenor-master-os.git`। Git না থাকলে GitHub page থেকে **Code → Download ZIP** → unzip।
3. **ইন্টারনেট** — প্রথমবার clone + 3D লাইব্রেরি (Three.js CDN) লোডের জন্য। অফিসের কাজ (run_office.py, voice) ইন্টারনেট ছাড়াই চলে।

## ৩ ধাপে চালানো

### ধাপ ১ — Dashboard খোলা (3D)

Repo ফোল্ডারে গিয়ে **`run_local.bat` ডাবল-ক্লিক** করুন। এটা নিজে নিজে করবে:

1. `python scripts\sync_status.py` — আসল ফাইল থেকে সংখ্যা তাজা করে (`dashboards\status.json`)
2. Local server চালু করে — `http://localhost:8765`
3. ব্রাউজারে **3D Dashboard** খোলে

বন্ধ করতে: bat-এর window-এ **Ctrl+C**।

### ধাপ ২ — Jarvis-এর সাথে কথা বলা (voice)

```bat
python scripts\jarvis_voice_loop.py
```

- বাংলায় বলুন, বাংলায় উত্তর দেবে। English-ও চলে (`--lang en`)।
- প্রথমবার ~৩৬১ MB মডেল ডাউনলোড হবে (Piper + Vosk/sherpa) — একবারই।
- **সত্য কথা:** voice আসল, কিন্তু brain এখনো **mock** — উত্তর DRAFT। মুখে "send করো" বললে কাজ হয় না, শুধু **PENDING** হয়।
- Mic test এখনো হয়নি — প্রথম আসল mic test আপনার PC-তেই হবে।

### ধাপ ৩ — অফিসকে একটা কাজ দেওয়া

```bat
python scripts\run_office.py --business agency --task caption_write --input "{\"title\": \"Caption for Monday reel\"}"
```

- `--business`: `agency` | `products` | `content`
- Gated কাজ (send/publish/spend/delete) আপনার gate word ছাড়া **PENDING**-এ আটকায় — কখনো নিজে চলে না।
- Queue থেকে কাজ চালাতে: `python scripts\run_office.py --drain-queue --max 2`

## Dashboard-টা Master OS-এর সাথে কীভাবে যুক্ত?

```
আসল ফাইল (config.json, store/, gate0-status.md, pipeline.md)
        ↓  python scripts\sync_status.py
dashboards\status.json  ← সংখ্যা এখানে আসে (হাতে লেখা নয়)
        ↓  run_local.bat → local server (port 8765)
3D Dashboard (dashboard-3d.html)  ← সংখ্যা + বিল্ডিং-এর রঙ এখানে দেখায়
```

- Dashboard শুধু **দেখায়** — কাজ করে `run_office.py`। সংখ্যা তাজা করতে `sync_status.py` আবার চালান, তারপর dashboard-এ **🔄 সংখ্যা তাজা করুন** চাপুন।
- `status.json` না পেলে dashboard 2026-11-19-এর snapshot দেখায় — সেটা লেখা থাকে।

## কী LIVE নয় (সত্য কথা)

| জিনিস | অবস্থা |
|---|---|
| Brain | **mock** — ভাবনা DRAFT, live brain ফ্লিপ করা হয়নি |
| Email outreach | **PAUSED** (2026-11-14 থেকে) — SPF/DMARC DNS fix আপনার হাতে বাকি |
| Paying client | **০** · প্রথম মেইল ১৬২ |
| Gate 0 (Vet Kit) | **NOT PASSED** — Lemon Squeezy test আপনার step |
| n8n workflows | **READY, NOT LIVE** — import + connect + test বাকি |
| YouTube upload | **OFF** — "upload it" + credential লাগে |
| ২৪/৭ server | **নেই** — PC বন্ধ করলে অফিস থামে; চালু রাখতে paid server লাগবে |
| PC-র সীমা | RAM 8 GB (~১.৪ GB ফাঁকা), GPU 496 MB VRAM — Ollama বড় মডেল / GPU video **চলবে না**; CPU-তে ছোট মডেল (1–1.5B) শুধু |

## সমস্যা হলে

- **"Python পাওয়া যায়নি"** → Python reinstall করুন, "Add Python to PATH" টিক দিয়ে।
- **"Port 8765 busy"** → আগের server window বন্ধ করুন, আবার চালান।
- **3D দেখা যায় না, সংখ্যা দেখা যায়** → ইন্টারনেট চেক করুন (Three.js CDN লাগে); সংখ্যা তবুও ঠিক দেখাবে।
- **Mic কাজ করে না** → Windows Settings → Privacy → Microphone → Python/terminal-কে allow করুন।
- **"Module not found"** → repo ফোল্ডারের ভিতর থেকে চালাচ্ছেন তো? `run_local.bat` নিজে cd করে নেয়।

## ফাইলগুলো

- `run_local.bat` — এক ক্লিকে dashboard
- `scripts\sync_status.py` — সংখ্যা sync করে (এখন `status.json`-ও লেখে)
- `dashboards\dashboard-3d.html` — 3D dashboard (এই ফাইল)
- `dashboards\status.json` — আসল সংখ্যা (sync-এ বানানো)
- `dashboards\status.html` — পুরনো 2D status page (sync-এ বানানো)
- `scripts\run_office.py` — অফিসের runner
- `scripts\jarvis_voice_loop.py` — Jarvis voice loop
- `00-CEO-Core\VOICE-SETUP.md` — voice setup বিস্তারিত
