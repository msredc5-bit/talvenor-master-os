# CEO Core — এটা কী করে

**সহজ কথায়:** এই folder-টা Master OS-এর "মাথা"। Boss কথা বলেন Jarvis-কে
(voice), Jarvis পাঠায় Main CEO Bot-কে (brain), Main CEO Bot ঠিক করে কোন
ব্যবসার Chief of Staff কাজটা করবে, আর gate-এর কাজ হলে Boss-এর অনুমোদন
ছাড়া এক পা-ও এগোয় না।

## ভেতরে যা আছে

| ফাইল | অবস্থা | কাজ |
|---|---|---|
| `main_ceo_bot.py` | REAL (thin router) | Task পড়ে ঠিক Chief-এর দিকে পাঠায়; gated কাজ approval-এ আটকায় |
| `human_approval_gateway.py` | REAL (working) | send / publish / spend / delete — approve()/reject() ছাড়া কিছু হয় না; auto-approve নেই |
| `jarvis_voice.py` | STUB | Voice interface — এখনো live mic-এর সাথে যুক্ত নয় |
| `config.json` | REAL | ৩ ব্যবসা, gate ON, $0 cap, booking link, ফোন, ইমেইল — সব locked fact |
| `CEO-README.md` | এই ফাইল | — |

## Hierarchy (Boss-এর সিদ্ধান্ত)

Boss → Jarvis (voice) → Main CEO Bot (brain) → ৩ Chief of Staff →
specialized worker → ফলাফল ফিরে আসে Main CEO Bot-এ → দরকার হলে Boss-এর
অনুমোদন।

**Jarvis আর Main CEO Bot আলাদা** — Jarvis শুধু কথা শোনে/বলে, brain
Main CEO Bot। Gemini-র map-এ ওরা একসাথে ছিল, সেটা ঠিক করা হয়েছে।

## Gate (আইন)

- `ok` = plan/asset approval
- `post it` = publish
- `upload it` = video upload
- `send` / `পাঠাও` = send
- `go` = পরের phase-এ যাওয়া

কোনো gate word ছাড়া send/publish/spend/delete হবে না — কোডেও সেই
পথ রাখা হয়নি।

## আসল ইঞ্জিন কোথায়

১৫ worker-এর আসল engine `~/workspace/boss-ceo/`-তে আছে (mock-tested +
১টা live worker run)। এখানে সেটা duplicate করা হয়নি — Phase 1-এ
এই router সেখান থেকে worker ডাকবে।
