# Agency Engine — Talvenor AI Receptionist (Phase 5)

**ব্যবসা:** Talvenor AI Receptionist Agency — US home-service ব্যবসার
(plumbing, HVAC, roofing, garage door, septic, tree, foundation,
restoration, pest, vet) জন্য AI receptionist। Boss-এর প্রথম ব্যবসা, MAIN।
Dental / medical / patient-health — কখনো target নয়।

## এক নজরে

| জিনিস | সংখ্যা |
|---|---|
| Staff (role) | **15** — vendored boss-ceo worker (Phase 6), ভিতরে আছে |
| Tools | **8** — mock 5, gated (stub) 3 |
| Skills | **15** — প্রতি role-এ একটা করে |
| Chief | `../chief_of_staff_agency.py` (REAL, Phase 1) — routing-ই সত্যের উৎস |

## Staff (15)

ACQ: Prospect Researcher, Outreach Drafter, Reply Triager, Negotiation Coach ·
DEL: Receptionist Builder (DRAFT plan only — live stack Vapi/Sophia),
QA Engineer, Onboarding Agent ·
MKT: Content Planner, Video Producer, Caption Writer, Publish Prep,
Objection Simulator ·
OPS: Inbox Triager, Report Compiler, Scheduler।

বিস্তারিত: `STAFF.md` — প্রতি role-এ worker class, division, কাজ, input,
output, gate word।

## Tools (8)

- **Mock (5)** — DRAFT বানায়, কিছু পাঠায়/বদলায় না:
  `draft_email`, `research_notes`, `draft_caption`, `draft_script`, `status_read`
- **Gated / stub (3)** — কখনো execute করে না, handler null:
  `send_email` (gated: send), `publish_post` (gated: publish),
  `spend` (gated: spend, cap $0)
- Registry: `tools.json` · Wrapper: `tool_calling.py` — shared core
  (`00-CEO-Core/tool_calling.py`)-এর `ToolRegistry.load_from_json` +
  `call_tool` ব্যবহার করে; নিজে কিছু execute করে না।

## Skills (15)

`skills/` — প্রতি role-এ একটা `.md`: role, input, step-by-step পদ্ধতি
(worker + agency-os SOP থেকে), output format, gate, সৎ সীমা।
যেখানে Boss-এর input সত্যিই লাগে, সেখানে "BOSS INPUT REQUIRED" লেখা —
কখনো বানানো তথ্য নয়।

## Status: REAL / MOCK / BLOCKED

| অংশ | Status |
|---|---|
| Chief routing (15 worker) | **REAL** — vendored engine ডাকে |
| Worker brain | **MOCK** — MockLLMProvider, $0; সব output DRAFT |
| Draft লেখা (email/DM/caption/script/plan) | **MOCK** — draft-ready |
| Receptionist build | **DRAFT plan only** — RetellBuilder plan লেখে, live build Vapi/Sophia-তে Boss-এর কাজ |
| Email পাঠানো | **BLOCKED — PAUSED** |
| Publish / upload | **BLOCKED — gate** (`post it` / `upload it`) |
| খরচ | **BLOCKED — cap $0** |

## কী আটকে আছে, আর কার হাতে

1. **Email PAUSED (2026-11-14 থেকে)** — SPF-এ Gmail include নেই, DMARC
   নেই। Fix Boss-এর DNS panel-এ: SPF-এ `include:_spf.google.com` যোগ করা,
   `_dmarc` TXT record (`p=none`) বসানো। তারপর Boss "check koro" বললে
   আবার যাচাই হবে। ততদিন draft-ই শেষ কথা — Day 4/5/6-এর 25+25+25 draft
   READY, পাঠানো হয়নি।
2. **Send / publish / spend / delete** — Boss-এর exact gate word
   (`send` / `post it` / `ok` / `upload it` / `go`) ছাড়া কিছু হয় না;
   কোনো auto-approve পথ নেই। পাঠানো/publish-এর কাজ Boss নিজে করেন।
3. **Paying client 0, প্রথম মেইল 162** — Gmail-এ দেখা reply 0;
   hello@-র reply Zoho-তে যায়, Boss-কে Zoho check করতে হয়।
4. **Follow-up** — কোথাও due নয় (100-mail rule; FL ceiling 98)।
   20টা ready PA follow-up draft PARKED আছে।
5. **Shared core** — `00-CEO-Core/tool_calling.py` parallel build-এ
   তৈরি হচ্ছে; এই engine-এর wrapper সেটা ছাড়া run করা যায় না
   (build-এর সময় file-টা ছিল না — live run যাচাই হয়নি)।

## নিয়ম (locked)

- Brand Talvenor only · কোনো বানানো client/testimonial/statistic/price নয় ·
  $0 spend cap · stdlib only, no network, no pip ·
  কোনো send/publish/spend/delete নয় · Booking:
  https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।

## ফাইল

- `STAFF.md` · `tools.json` · `tool_calling.py` · `README.md` (এই ফাইল)
- `skills/` — 15টা skill `.md`
- Source (reference only, copy করা হয়নি): `../chief_of_staff_agency.py`,
  `../pipeline.md`, `01-Agency-Department/engine/workers/src/workers/` (vendored; upstream `~/workspace/boss-ceo/src/workers/`),
  `~/workspace/agency-os/` (20 skill + SOP)।
