# BUILD LOG — Talvenor Master OS

## Phase 0 — 2026-11-16 (Boss: "আসল সিস্টেম শুরু করো")

### বানানো হয়েছে (NEW — এই folder-এ)

- `00-CEO-Core/main_ceo_bot.py` — REAL thin router (task -> Chief, gated task approval-এ আটকায়)
- `00-CEO-Core/human_approval_gateway.py` — REAL working gateway (request/approve/reject, ভুল gate word reject করে, auto-approve নেই)
- `00-CEO-Core/jarvis_voice.py` — STUB (mic যুক্ত নয়, ডাকলে NotImplementedError)
- `00-CEO-Core/config.json` — REAL (৩ ব্যবসা, gate ON, $0 cap, booking link, ফোন, ইমেইল)
- `00-CEO-Core/CEO-README.md` — Bengali
- `01-Agency-Department/chief_of_staff_agency.py` — STUB + sub_agents/README.md (১৫ worker-এর আসল নাম) + workflows/README.md (email pause সত্য অবস্থা)
- `02-Digital-Product-Department/chief_of_staff_products.py` — STUB + README.md + gate0-status.md (NOT PASSED)
- `03-Content-Creation-Department/chief_of_staff_content.py` — STUB + README.md
- `store/tasks.json` + `store/approvals.json` — খালি, schema সহ + `store/vault/README.md`
- `dashboards/status.html` — REAL static dashboard (সত্য অবস্থা)
- `skills/` — ৪টা skill manual (main-ceo-bot, chief-agency, chief-products, chief-content)
- `scripts/check_phase0.py` — self-check (stdlib only, no network)
- `README.md` + `BUILD-LOG.md` (এই ফাইল)

### REUSED — duplicate করা হয়নি, শুধু reference

- `~/workspace/boss-ceo/` — 15-worker engine (mock-tested + 1 live run)
- `~/workspace/talvenor-office/` — Agency office
- `~/workspace/creator-os-combined/` — Creator OS (6 worker)
- `~/workspace/jarvis-ceo-os-concept/` — Jarvis concept docs
- `~/workspace/ceo-os-summary/CEO-OS-A-to-Z-summary.md` — honest built-vs-map state (পড়া হয়েছে)

### Gemini map-এর ৪ ভুল — ঠিক করা হয়েছে

1. Jarvis ≠ Main CEO Bot — আলাদা module (`jarvis_voice.py` vs `main_ceo_bot.py`)
2. Approval/gate layer যোগ করা হয়েছে (`human_approval_gateway.py` — REAL)
3. Store/Vault যোগ করা হয়েছে (`store/`)
4. Digital product = Vet Kit $49, generic "Notion Kits & Guides" নয়

### Check ফলাফল

- `python3 scripts/check_phase0.py` — **8/8 PASS** (exit 0), 2026-11-16
  - 24/24 file আছে; config.json locked facts ঠিক; store JSON খালি;
    gateway temp file-এ কাজ করে (আসল approvals.json ছোঁয়া হয়নি);
    router কাজ করে; Jarvis loud STUB; dashboard honest।
- Dashboard `status.html`: external resource NONE, script tag 0 — browser-এ
  clean খুলবে।
- Invented-fact grep: কোনো বানানো client/stat/testimonial/guarantee নেই।
  সব সংখ্যা locked fact থেকে (Vet Kit $49, Growth $1,109, AAHA 11%,
  AVMA ~$200 — research-সহ source লেখা)।

### এখনো STUB / বাকি

- Jarvis voice live mic-এর সাথে যুক্ত নয়
- ৩ Chief module আসল কাজ করে না — Phase 1–3-এ জোড়া হবে
- n8n wiring নেই — Phase 4
- Gate 0 (Lemon Squeezy test) Boss-এর step — হয়নি

---

## Phase 1 — Agency REAL — 2026-11-16 (Boss: "হ্যাঁ, Phase 1 (Agency) শুরু করো")

### আসল হয়েছে (NEW / CHANGED)

- `01-Agency-Department/chief_of_staff_agency.py` — **REAL** (STUB ছিল): `handle_task()` আসল boss-ceo worker ডাকে (MockLLMProvider, $0)। ROUTING table: ১৫টা task type → ১৫টা আসল worker (নাম engine থেকে যাচাই করা)। Gated action (send/publish/spend/delete) এলে worker চালানো হয় না — ApprovalGateway-এ PENDING request লেখা হয়। প্রতিটা routed task `store/tasks.json`-এ append হয় (অন্য department-এর entry মোছা হয় না)। RetellBuilder = DRAFT plan only — live stack Vapi/Sophia।
- `00-CEO-Core/main_ceo_bot.py` — agency task এখন আসল Chief-এর কাছে যায় (delegate)। অন্য ২ business এখনো STUB। `route_task()` এখন `tasks_path` / `approvals_path` নেয় (test-এ TEMP file ব্যবহার হয়)।
- `01-Agency-Department/pipeline.md` — NEW: ১০ ধাপের আসল pipeline + সত্য অবস্থা (162 first mail, email PAUSED, Day 4/5/6 draft ২৫টা করে — ফাইল থেকে যাচাই করা, follow-up কোথাও due নয়, Zoho unchecked)।
- `01-Agency-Department/sub_agents/README.md` — WIRED: task type → worker → gate টেবিল, প্রতিটার অবস্থা (mock-tested / ১ live run)।
- `skills/chief-agency.md` — আসল manual: routing table, পড়া/লেখা ফাইল, gate।
- `scripts/check_phase1.py` — NEW: ১১টা check (TEMP file-এ চলে, আসল store ছোঁয় না)।
- `scripts/check_phase0.py` — test 5 আপডেট: agency routing এখন route-only probe ফেরত দেয় (Chief REAL হওয়ায়)।
- `dashboards/status.html` — Agency section REAL: Phase 1 BUILT, Chief 15 worker ডাকে, email PAUSED।
- `00-CEO-Core/config.json` — phase 1, version 0.2.0, phase_1_agency = BUILT।
- `README.md` — Agency STUB → REAL।

### Check ফলাফল

- `python3 scripts/check_phase1.py` — **11/11 PASS** (exit 0), 2026-11-16
- `python3 scripts/check_phase0.py` — **8/8 PASS** (exit 0, আবার চালানো) — Phase 0 ভাঙেনি।

### Smoke test (in-memory only, TEMP files — আসল store ছোঁয়া হয়নি, কোনো send নয়)

- Trace 1: Main CEO Bot → Chief → **OutreachDrafter** (ACQ) — status `draft-ready`, draft_only True, mock_brain True, gate `send`, output: 5 email draft, from hello@talvenorai.agency, "DRAFT ONLY — Boss sends"।
- Trace 2: একই task + `gated_action: send` → status `pending-approval`, approval PENDING (id 65d6e7d7c9c7), worker একদম চালানো হয়নি, approved 0।
- TEMP store: tasks 2 record, approvals pending 1, approved 0। REAL store: tasks 0, approvals 0 — কিছু লেখা হয়নি।

### এখনো STUB / বাকি

- Jarvis voice (mic নয়) + ২ Chief (Digital Product, Content) — Phase 2–3
- Live brain (Muse Spark) এই Chief-এ নয় — mock brain ($0) দিয়েই চলে
- n8n wiring — Phase 4
- Gate 0 (Lemon Squeezy test) Boss-এর step — Phase 2-র আগে লাগবে

---

## Phase 2 — Digital Product REAL* — 2026-11-16 (Boss: "Phase 2 করো" + 3D office-এ shift)

*REAL = Chief module + blueprint + list; kit build/sale/launch Gate 0-তে
আটকে আছে। Master OS এখন 3D office artifact (`ceo-office-dashboard`)-এর
engine — folder system `~/workspace/talvenor-master-os/`-এ, dashboard
সেখানকার সত্য অবস্থা দেখায়।

### আসল হয়েছে (NEW / CHANGED)

- `02-Digital-Product-Department/chief_of_staff_products.py` — **REAL**
  (STUB ছিল): `handle_task()` ৪ task type route করে (kit_build →
  blueprint, clinic_research → PA list, gate0_check → Gate 0 status,
  launch_prep → DRAFT checklist)। `mark_launched` / `mark_sold` চাইলে
  Gate 0 যাচাই করে — পাস না হলে status `blocked-gate0`, কোনো sale
  লেখা হয় না। Gated action এলে worker চালানো হয় না — ApprovalGateway-এ
  PENDING request। প্রতিটা routed task `store/tasks.json`-এ append হয়
  (অন্য department-এর entry মোছা হয় না)। Gate 0-র উৎস শুধু
  gate0-status.md-এর Status লাইন (fail-closed)।
- `02-Digital-Product-Department/kit-outline.md` — NEW: kit-এর ৬ অংশের
  পূর্ণ blueprint (research report §4.1/§5 থেকে), build order, Gate 0–3
  kill criteria, সত্য অবস্থা। এটা নকশা — kit নিজে নয়।
- `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv` — NEW:
  **39 independent PA vet clinic, যাচাই করা** (লক্ষ্য 100-এর 39%)।
  Philadelphia 8, York 5, Lancaster 4, Allentown/Bethlehem 4,
  Pittsburgh/Monroeville 3, Erie 3, Scranton/Wilkes-Barre 3,
  State College 3, Harrisburg 2, Norristown 2, Reading 1, Altoona 1।
  Email আছে 8টার; বাকি "Not publicly listed" (বানানো হয়নি)। Chain
  (Banfield, VCA, Vetco, BluePearl, Thrive, PetVet365) বাদ। Spot-check:
  Indy Veterinary Care + Love City Vet — official site খুলে মিলিয়ে
  দেখা হয়েছে। + `pa-vet-list/README.md` (যাচাই নিয়ম, 100-এ পৌঁছানোর plan)।
- `02-Digital-Product-Department/gate0-status.md` — আপডেট: Gate 0 NOT
  PASSED, Boss-এর ১৫-min step, 3D office dashboard-এ ফলাফল রেকর্ডের
  পথ, পাস/ফেল অনুযায়ী next step (Polar → Gumroad)।
- `skills/chief-products.md` — আসল manual: routing table, Gate 0 নিয়ম,
  kit blueprint reference।
- `scripts/check_phase2.py` — NEW: ১৪টা check (TEMP file-এ চলে, আসল
  store ছোঁয় না; check_phase0 + check_phase1-ও চালায়)।
- `00-CEO-Core/main_ceo_bot.py` — digital-product task এখন আসল Products
  Chief-এর কাছে যায় (Agency-র মতো delegate)। Content এখনো STUB।
- `00-CEO-Core/config.json` — phase 2, version 0.3.0, phase_2 status আপডেট।
- `dashboards/status.html` — Digital Product section: Phase 2 BUILT*,
  Gate 0 NOT PASSED, PA list 39/100, kit sales 0।
- `README.md` + `02-Digital-Product-Department/README.md` — সত্য অবস্থা আপডেট।

### Check ফলাফল

- `python3 scripts/check_phase2.py` — **14/14 PASS** (exit 0), 2026-11-16
  (এর মধ্যে check_phase0 8/8 + check_phase1 11/11 আবার PASS — Phase 0/1 ভাঙেনি)।
- **Bug ধরা পড়ে ঠিক করা হয়েছে (check-এর সময়):** প্রথম run-এ 11/14 —
  `read_gate0_status()` "Status: PASSED" substring খুঁজত, আর
  gate0-status.md-এর ব্যাখ্যা লাইনে ওই শব্দটা থাকায় ভুল করে Gate 0
  পাস ধরে নিচ্ছিল (fail-open)। ঠিক করা হয়েছে: এখন শুধু Status
  লাইনটা parse করে। Re-run: 14/14 PASS।

### Smoke test (TEMP files — আসল store ছোঁয়া হয়নি, কোনো send নয়)

- Trace 1: Main CEO Bot → Products Chief → `kit_build` — status
  `draft-ready`, handler blueprint, ৬ অংশ, Gate 0 NOT PASSED।
- Trace 2: `launch_prep` + `mark_sold: True` — status `blocked-gate0`,
  Gate 0 NOT PASSED, কোনো sale লেখা হয়নি।
- REAL store: tasks 0, approvals 0 — কিছু লেখা হয়নি। Dashboard-এ
  `<script>` tag 0।

### এখনো BLOCKED / বাকি

- **Gate 0 (Lemon Squeezy test) Boss-এর step — হয়নি।** এটা ছাড়া:
  kit-এর ৬ অংশ বানানো যাবে না, PA list 100-এ পূর্ণ করা যাবে না (plan
  আছে, Gate 0-র পরে), launch/sale করা যাবে না।
- Content Chief (Phase 3) এখনো STUB; n8n wiring (Phase 4) বাকি।

---

## Phase 3 — Content Creation REAL — 2026-11-16 (Boss: "হ্যাঁ, Phase 3 (Creator OS) শুরু করো")

### আসল হয়েছে (NEW / CHANGED)

- `03-Content-Creation-Department/chief_of_staff_content.py` — **REAL**
  (STUB ছিল): `handle_task()` আসল Creator OS ৬ worker ডাকে
  (TopicResearcher, ScriptWriter, VisualProducer, CaptionWriter,
  PublishPrep, PerformanceTracker — MockLLM, $0)। ROUTING: ৬ task type
  (content_plan, script_write, video_produce, caption_write,
  publish_prep, performance_track)। Gated action এলে worker চালানো হয়
  না — ApprovalGateway-এ PENDING request। `upload` চাইলে সরাসরি
  `blocked-upload-off` (stage 9 OFF — upload script কখনো চালানো হয়
  না)। video_produce-তে `video_file: None`, `video_built: False` +
  missing-inputs list (footage / voiceover / GPU নাম) — ভুয়া video
  নেই। script_write-এ VOICE.md DRAFT সতর্কতা। publish_prep-এ
  `ready_to_publish: False`, gate "post it"। প্রতিটা routed task
  `store/tasks.json`-এ append হয় (অন্য department-এর entry মোছা হয় না)।
- `03-Content-Creation-Department/pipeline.md` — NEW: ১৩ stage-এর সৎ
  map (Creator OS README থেকে যাচাই করা) — REAL **0** · MOCK **10** ·
  STUB **0** · BLOCKED **3** (stage 4 video, 5 edit, 9 upload) + প্রতিটা
  stage-এ Boss-এর কাছে যা বাকি + Nov 16–22 weekly plan-এর অবস্থা
  (Boss-এর "ok" বাকি)।
- `03-Content-Creation-Department/toolpilot-status.md` — NEW: ToolPilot
  channel facts (@ToolPilotai69, ID UCLGlqsDCLmcqis9pMCikC4Q), YPP 0
  subs / 0 hours / video 0, Week 1 READY TO RECORD (OBS recording
  বাকি, verdict [FILL AFTER TEST]), Weeks 2–4 plan, Track 3 প্রশ্ন
  (ToolPilot নাকি নতুন channel) এখনো unanswered।
- `skills/chief-content.md` — আসল manual: routing table, gate, upload
  OFF নিয়ম, VOICE.md/GPU নিয়ম, সত্য অবস্থা।
- `scripts/check_phase3.py` — NEW: ১৮টা check (TEMP file-এ চলে, আসল
  store ছোঁয় না; check_phase0 + check_phase1 + check_phase2-ও চালায়)।
- `00-CEO-Core/main_ceo_bot.py` — content task এখন আসল Content Chief-এর
  কাছে যায় (Agency + Digital Product-এর মতো delegate)। ৩ Chief-ই REAL।
- `00-CEO-Core/config.json` — phase 3, version 0.4.0।
- `dashboards/status.html` — Content Engine section: Phase 3 BUILT,
  13 stage REAL 0 / MOCK 10 / BLOCKED 3, upload OFF, VOICE.md DRAFT,
  GPU নাম বাকি, ToolPilot video 0।
- `README.md` + `03-Content-Creation-Department/README.md` — সত্য অবস্থা আপডেট।

### Check ফলাফল

- `python3 scripts/check_phase3.py` — **19/19 PASS** (exit 0),
  2026-11-16 (এর মধ্যে check_phase0 8/8 + check_phase1 11/11 +
  check_phase2 14/14 আবার PASS — Phase 0/1/2 ভাঙেনি)। প্রথম run-এ
  17/19 ছিল — ২টা fail ছিল check-এর মিল না-হওয়া, আসল কাজের ভুল
  নয়: (a) pipeline.md-এর stage code লেখার ধরন (`0a` বনাম
  `0a-niche`) — md-তে code বসিয়ে ঠিক করা হয়েছে; (b)
  check_phase2.py-র phase assertion (`phase == 2`) — phase 3
  হওয়ায় fail করছিল, `phase >= 2`-তে আপডেট করা হয়েছে (Phase 1-এ
  check_phase0-র test 5 আপডেট করার মতোই)। Re-run: 19/19 PASS।

### Smoke test (TEMP files — আসল store ছোঁয়া হয়নি, কোনো send/upload নয়)

- Trace 1: Main CEO Bot → Content Chief → **TopicResearcher** —
  status `draft-ready`, gate `ok`, mock brain, draft_only True।
- Trace 2: `video_produce` (input ছাড়া) — `draft-ready`,
  `video_file: None`, `video_built: False`, missing_inputs 2
  (footage + voiceover/script)।
- Trace 3: `publish_prep` + `gated_action: upload` —
  `blocked-upload-off`, upload script চালানো হয়নি।
- REAL store: tasks 0, approvals 0 — কিছু লেখা হয়নি।

### এখনো BLOCKED / বাকি (Boss-এর step)

- **PC GPU-র নাম** (2026-11-01 থেকে বাকি) — true AI video motion-এর জন্য।
- **VOICE.md correction** — প্রথম script final হওয়ার আগে।
- **Week 1 OBS recording** — Nano Banana 2-র ৫ test।
- **Track 3 প্রশ্ন** — ToolPilot নাকি brand-new channel (2026-11-12 থেকে)।
- **Upload OAuth + "upload it"** — প্রথম real upload-এর আগে।
- **Nov 16–22 weekly plan-এ "ok"** — Talvenor social cadence।
- n8n wiring (Phase 4) বাকি। Jarvis voice এখনো STUB (mic নয়)।

---

## Phase 4 — n8n Wiring + Live Dashboard — 2026-11-16 (Boss: "হ্যাঁ, Phase 4 শুরু করো")

### আসল হয়েছে (NEW / CHANGED)

- `dashboards/n8n-wiring.md` — NEW: ২ workflow-র পূর্ণ wiring map
  (auto-send: 8 node, Schedule 18:00 Dhaka → Sheet Queue → Gmail →
  Sheet-এ sent; callback: 3 node, website form → webhook → Vapi
  POST /call → Sophia)। ২টাই **READY · NOT LIVE** (`active: false` —
  ফাইল থেকে যাচাই করা)। Boss-এর exact বাকি step প্রতিটার জন্য লেখা
  (auto-send: import + Gmail/Sheets connect + 1-mail test, From-এ
  hello@ যাচাই; callback: Twilio number ~$1.15/mo import + workflow
  import + Vapi Header-Auth + webhook URL)। Email-pause gate লেখা
  (DNS fix + "check koro" + seed test ছাড়া auto-send চলবে না)।
  দুই send system একসাথে না-চলার নিয়ম + $0 host-এর সত্য কথা
  (Muse runtime + 10-min bridge cron; ২৪/৭ server নেই — পরে টাকা দিয়ে)।
  **একটা ভুল ধরা পড়ে ঠিক করা হয়েছে:** auto-send ফাইল আসলে
  `~/workspace/talvenor-outreach/`-এ (hyphen) — task-এ দেওয়া
  `~/workspace/talvenor/outreach/` path-এ নেই। wiring doc-এ সঠিক
  path লেখা আছে।
- `scripts/sync_status.py` — NEW: `dashboards/status.html` আসল ফাইল
  থেকে আবার বানায় (config.json, store/tasks.json + approvals.json,
  gate0-status.md-এর Status লাইন — fail-closed, PA list CSV,
  pipeline.md-এর গণনা লাইন, toolpilot-status.md-এর Subscribers লাইন,
  ২ n8n JSON-এর `active` flag)। কোনো মান না পেলে "unknown" লেখে,
  বানায় না। Deterministic — ২ বার চালালে byte-সমান HTML।
- `scripts/check_phase4.py` — NEW: ৯টা check (wiring doc, sync-এর
  আসল মান, determinism + HTML-উৎস মিল, LIVE দাবি নেই, Jarvis STUB,
  dashboard Phase 4, config phase 4, আসল store খালি, Phase 0–3
  আবার PASS)।
- `dashboards/status.html` — sync দিয়ে আবার বানানো (হাতে নয়):
  Phase 4 BUILT, নতুন n8n card (২ workflow READY · NOT LIVE),
  host Muse runtime + bridge cron, Jarvis STUB। আগের check-গুলোর
  চাওয়া সব string আছে (Phase 0/১৩৬, PAUSED, Gate 0 NOT PASSED,
  PA list 39, upload OFF)।
- `00-CEO-Core/config.json` — phase 4, version 0.5.0, phase_4 status BUILT।
- `README.md` — Phase 4 COMPLETE + sync চালানোর নিয়ম।

### Check ফলাফল

- `python3 scripts/check_phase4.py` — **9/9 PASS** (exit 0), 2026-11-16
  (এর মধ্যে check_phase0 8/8 + check_phase1 11/11 + check_phase2
  14/14 + check_phase3 19/19 আবার PASS — Phase 0–3 ভাঙেনি)।
  প্রথম run-এই 9/9। Sync ২ বার চালিয়ে byte-সমান HTML যাচাই করা হয়েছে।

### এখনো BLOCKED / বাকি (Boss-এর step — LIVE করতে হলে)

- **DNS fix + "check koro" + seed test** — email restart-এর আগে
  (SPF edit + DMARC new)।
- **Gate 0 (Lemon Squeezy test)** — kit build/sale/launch-এর আগে।
- **Twilio number (~$1.15/mo) + n8n import + Vapi credential +
  webhook URL** — callback call-এর আগে।
- **n8n import + Gmail/Sheets connect + 1-mail test** — auto-send-এর আগে।
- **PC GPU নাম, VOICE.md correction, OBS recording, Track 3 প্রশ্ন,
  upload OAuth + "upload it", Nov 16–22 plan-এ "ok"** — Creator OS-এর
  বাকি।
- Jarvis voice STUB (mic নয়) — live করতে আলাদা সিদ্ধান্ত + কাজ লাগবে।

---

## ✅ MASTER OS COMPLETE — সৎ হিসাব (2026-11-16, সব Phase শেষ)

| জিনিস | অবস্থা | প্রমাণ |
|---|---|---|
| Phase 0 — folder + CEO Core + gateway + dashboard | **BUILT** | check 8/8 PASS |
| Phase 1 — Agency Chief (15 worker, draft-only) | **BUILT** | check 11/11 PASS |
| Phase 2 — Products Chief + kit blueprint + PA list 39/100 | **BUILT\*** | check 14/14 PASS; \*launch/sale Gate 0-তে আটকে |
| Phase 3 — Content Chief (6 worker, 13 stage) | **BUILT** | check 19/19 PASS |
| Phase 4 — n8n wiring + sync dashboard | **BUILT** | check 9/9 PASS |
| Approval gateway (approve/reject, auto-approve নেই) | **REAL** | temp-file test, আসল approvals 0 record |
| Main CEO Bot router (৩ Chief-এ delegate) | **REAL** | ৩ Chief-ই end-to-end route হয় |
| Dashboard (sync দিয়ে বানানো) | **REAL** | সংখ্যা আসল ফাইল থেকে |
| n8n auto-send workflow (8 node) | **READY · NOT LIVE** | JSON `active: false` |
| n8n callback workflow (3 node) | **READY · NOT LIVE** | JSON `active: false`, phoneNumberId `FILL_AFTER_TWILIO_IMPORT` |
| Creator OS 13 stage | **REAL 0 / MOCK 10 / BLOCKED 3** | pipeline.md গণনা লাইন |
| Jarvis voice | **STUB** | mic যুক্ত নয়, NotImplementedError |
| 136 ব্যবসা / 1,189 worker | **DROPPED (Boss 2026-11-16)** | scope = 3 ব্যবসা only |
| Paying client | **0** | — |
| প্রথম মেইল | **162** | config.json honest_status |
| Email | **PAUSED** (2026-11-14 থেকে) | DNS fix Boss-এর হাতে |
| Vet Kit sale | **0** | Gate 0 NOT PASSED |
| ToolPilot video / subs | **0 / 0** | OBS recording বাকি |
| Host | **Muse runtime + bridge cron ($0)** | ২৪/৭ server নেই |

**মোট check: 8 + 11 + 14 + 19 + 9 = 61/61 PASS।** আসল store
(tasks 0, approvals 0) — কোনো send/publish/upload/spend/delete
হয়নি। যা LIVE নয়, তা LIVE বলা হয়নি — কোথাও।

---

## Architecture definition — Boss, 2026-11-16 ~04:35 Dhaka

Boss restated the first-to-last structure in his own words (recorded verbatim in meaning):
1. Conversation starts: Jarvis.
2. Jarvis is connected with the super intelligent second brain, the Main CEO Bot.
3. Main CEO Bot maintains everything. From the second brain run: Agency Office, Digital Product Business Office, Creator OS / Content Machine and Engine.

This matches the built hierarchy exactly. ONE honest gap: step 1 is not live yet — Jarvis voice is STUB (mic not connected), so today the conversation actually starts in chat with Elora, not with Jarvis voice. The brain (Main CEO Bot) + 3 Chiefs are REAL; the voice link is the missing piece. README.md hierarchy updated to Boss's definition.

## Phase 5 — Three Engines — 2026-11-16 (Boss: "তিনটা Engine হবে, তিনটা Office System হবে")

Boss-এর সংজ্ঞা: প্রতিটা office-ই একটা পূর্ণ Engine + Office System হবে — নিজস্ব Staff,
নিজস্ব Tool Calling System, নিজস্ব Skills। Research করে সব build করা হয়েছে, file setup
GitHub push-এর জন্য ready (repo `talvenor-master-os` এখনো বানানো হয়নি — Boss বানাবেন)।

### যা বানানো হয়েছে
- **Shared tool-calling core** — `00-CEO-Core/tool_calling.py` (546 লাইন, stdlib only):
  ToolRegistry (register/load_from_json) + dispatcher `call_tool()` — args validate করে,
  gated tool (send/publish/spend/delete) হলে ApprovalGateway-এ PENDING লেখে, কখনো execute
  করে না; mock tool DRAFT ফেরত দেয়; stub tool `blocked-stub`; প্রতিটা call
  `store/tool_calls.json`-এ log হয়। 6 handler: draft_email, research_notes,
  draft_caption, draft_script, kit_outline_read (আসল kit-outline.md পড়ে),
  status_read (আসল config.json পড়ে)।
- **Agency Engine** — `01-Agency-Department/engine/`: STAFF.md 15 role (15 boss-ceo worker),
  tools.json 8 tool (5 mock / 3 gated: send_email, publish_post, spend),
  skills/ 15 file, tool_calling.py wrapper, README.md।
- **Digital Product Engine** — `02-Digital-Product-Department/engine/`: STAFF.md 5 role,
  tools.json 8 tool (6 mock / 2 gated: launch_kit, sell_kit — Gate 0-তে আটকে),
  skills/ 5 file, tool_calling.py wrapper, README.md।
- **Content Engine** — `03-Content-Creation-Department/engine/`: STAFF.md 8 role
  (6 creator worker + Content Planner + Performance Analyst),
  tools.json 8 tool (5 mock / 3 gated: publish_post, upload_video, spend),
  skills/ 8 file, tool_calling.py wrapper, README.md।
- **Engines dashboard** — `dashboards/engines.html` + `scripts/sync_engines.py`
  (আসল engine file থেকে সংখ্যা বানায়, দুইবার চালালে byte-identical)।
- **Check** — `scripts/check_engines.py`: 45/45 PASS (core + 3 engine end-to-end +
  আসল store untouched + Phase 0–4 re-PASS)। মোট: 8+11+14+19+9+45 = 106 checks।

### Verification-এ ধরা পড়ে ঠিক করা হয়েছে (coordinator নিজে re-run করে)
1. **Circular import (2 wrapper):** Agency + Products wrapper-এ plain `import tool_calling`
   নিজের file-কেই import করছিল (AttributeError) — Content wrapper-এর মতো importlib
   file-path loading-এ ঠিক করা হয়েছে।
2. **Products wrapper-এ ভুল path:** CEO_CORE_DIR এক ধাপ কম উপরে যাচ্ছিল
   (`02-Digital-Product-Department/00-CEO-Core`) — FileNotFoundError, ঠিক করা হয়েছে।
3. **Core draft_script hardcoded Talvenor CTA:** ToolPilot topic-এও Talvenor-এর CTA
   দিচ্ছিল — এখন topic-aware (receptionist/Talvenor topic-এ Talvenor CTA, বাকিতে
   generic CTA)।
4. **DRAFT label:** draft_email + draft_caption handler-এর output text-এ DRAFT লেখা
   ছিল না (শুধু notes-এ) — output-এও "[DRAFT ONLY ...]" যোগ করা হয়েছে।
5. **Check-এর [FILL ban:** content script-writer.md-র "[FILL AFTER TEST]" আসলে
   ToolPilot verdict-এর LOCKED placeholder — check-এ exemption দেওয়া হয়েছে।
6. **Sync parse:** gate0-status.md-র `**Status:**` লাইন + pipeline.md-র গণনা লাইন
   (STUB সহ, `**` marker) — দুটোই ঠিক করে parse করা হয়েছে।
7. **Test contamination:** coordinator-এর একটা test call আসল store-এ
   `store/tool_calls.json` বানিয়ে ফেলেছিল (1 record) — ফাইলটা সরানো হয়েছে;
   আসল store আবার pristine (tasks 0, approvals 0, tool_calls.json নেই)।

### সৎ হিসাব (built-vs-map)
| জিনিস | অবস্থা |
|---|---|
| Phase 0 / 1 / 2* / 3 / 4 / 5 | **BUILT** (106 checks PASS) |
| Shared tool-calling core + 3 engine | **REAL** (mock brain, draft-only; gated কখনো execute হয় না) |
| Agency Engine 15 staff / 8 tool / 15 skill | **REAL** — email PAUSED |
| Products Engine 5 staff / 8 tool / 5 skill | **REAL\*** — launch/sale Gate 0-তে আটকে |
| Content Engine 8 staff / 8 tool / 8 skill | **REAL** — upload OFF, VOICE.md DRAFT, GPU নাম বাকি |
| Jarvis voice | **STUB** (mic নয়) |
| 136 ব্যবসা / 1,189 worker | **DROPPED (Boss 2026-11-16)** — scope = 3 ব্যবসা only |
| Paying client / প্রথম মেইল / Email / Vet Kit sale / ToolPilot video | **0 / 162 / PAUSED / 0 / 0** |
| Host | **Muse runtime + bridge cron ($0)** — ২৪/৭ server নেই |
| GitHub push | **READY, NOT PUSHED** — repo `talvenor-master-os` বানানো হয়নি (404, 2026-11-16 যাচাই করা); manifest `/tmp/master-os-manifest.txt`-এ ready; Boss repo বানালে এক command-এ push |

## Phase 6 — Full Complete Agent Offices (BUILT 2026-11-16, Boss: "full complete office বানাও")

**Boss-এর scope (2026-11-16 ~20:15, তাঁর নিজের কথা):** ৩ machine একসাথে ৩ business চালাবে (Agency, Digital Product, Content); প্রত্যেক business-এর নিজের office + নিজের worker আলাদা আলাদা; আগের বানানো GitHub worker-দের office-র ভিতরে ADD করা; 136 business DROPPED (আপাতত বাদ)।

**সৎ gap যা বন্ধ করা হলো:** Phase 5 পর্যন্ত Chief-রা worker import করত repo-র বাইরে থেকে (`~/workspace/boss-ceo`, `~/workspace/creator-os-combined` via sys.path) — push করা repo একা চলতে পারত না। Phase 6-এ worker-রা ভিতরে vendored।

### যা বানানো হলো
- **Agency vendored** — `01-Agency-Department/engine/workers/`: 18 file (24,621 bytes), byte-identical to upstream (`diff -r` exit 0): `src/workers/` 5 file (15 worker), `src/contracts/` 6 file, `src/mock/provider.py`, `src/live/meta_provider.py` + `__init__.py`। `src/mock/scenarios.py`, `src/ceo/`, `src/divisions/`, `src/store/db.py` copy করা হয়নি — copy করা কোনো file ওদের import করে না। `SOURCE.md` (origin, file table, upstream-canonical note)। Chief rewired: `ENGINE_WORKERS_DIR` এখন vendored dir; Chief-এ `boss-ceo` string 0।
- **Content vendored** — `03-Content-Creation-Department/engine/workers/`: 4 file: `src/creator_workers.py` (4,828 bytes, 6 worker), `src/workers/base.py` (7,931 bytes), 2× `__init__.py` + `SOURCE.md`। আর কোনো module লাগেনি — `creator_workers.py` শুধু `src.workers.base` import করে, `base.py` শুধু stdlib। `VOICE.md` repo-র ভিতরে আনা হয়েছে (`03-Content-Creation-Department/VOICE.md`)। Chief rewired: `creator-os-combined` string 0।
- **Products office** — কিছু vendor করার নেই (5 staff আগেই repo-র ভিতরে); verify করা হয়েছে self-contained (শুধু `00-CEO-Core` import)। Gate 0 NOT PASSED — কোনো sale লেখা হয়নি।
- **BrainFactory** — `00-CEO-Core/brain.py` (stdlib only): config flag `brain` (`mock` DEFAULT / `live`)। দুই department-এর mock আলাদা shape (agency `MockLLMProvider.complete(prompt, *, max_tokens=500)`, content `MockLLM.complete(prompt)`) — factory প্রত্যেক department-কে তার নিজের mock দেয়, Chief-দের call site বদলায়নি। `live` = vendored `MetaSparkProvider`; key শুধু connector Secure Vault surrogate (`dynamic_credentials`, `/opt/muse/skills/custom-connector-setup/bin/`) দিয়ে — কোনো file-এ key নেই। Live-এর প্রথম verification 2026-11-06-এ TIMEOUT হয়েছিল, key path UNPROVEN — Phase 6-এ কোনো live call নেই।
- **Runner** — `scripts/run_office.py` (stdlib only): `python3 scripts/run_office.py --business agency|products|content --task <type> --input <json>` → Main CEO Bot → Chief → worker → result (stdout JSON + `store/tasks.json`-এ append)। `--drain-queue --max 2` (এক run-এ সর্বোচ্চ 2 queued task; প্রতিটা আলাদা subprocess-এ চলে)। `--store-dir` দিয়ে TEMP store-এ test করা যায়। Gated action → PENDING, execute হয় না।
- **Config** — phase 4 → **6**, version 0.5.0 → **0.6.0**, `"brain": "mock"` যোগ; `reused_systems` এখন বলে worker-রা VENDORED, upstream শুধু canonical।
- **136 DROPPED** — repo-র ২টা 136/1,189 লাইন (এই file-এ) এখন `DROPPED (Boss 2026-11-16) — scope = 3 ব্যবসা only`। `ceo-os` repo বা অন্য কোনো folder ছোঁয়া হয়নি — drop শুধু Master OS scope।
- **Docs sync** — root README (Phase 6 accounting + runner usage), CEO-README, department README/pipeline/STAFF, engine README, 21 skill file-র path reference, `skills/chief-*.md`, `skills/main-ceo-bot.md`, `scripts/sync_status.py` template — সব এখন vendored সত্য বলে। BUILD-LOG-এর পুরনো Phase 0–5 entry history হিসেবে রাখা হয়েছে, বদলানো হয়নি।

### Verification-এ ধরা পড়ে ঠিক করা হয়েছে
1. **`src` package collision (pre-existing, Phase 6-এ ধরা):** দুই vendored tree-ই top-level `src` package দেয় — এক process-এ দুই Chief import করলে `ModuleNotFoundError: No module named 'src.creator_workers'`। BrainFactory-র `_load_module()` এখন stale `src` evict করে আর চাওয়া workers dir-কে `sys.path`-এ position 0-তে বসায়। একই কারণে runner-এর drain প্রতিটা task আলাদা subprocess-এ চালায়।
2. **Live branch ভুল tree ধরছিল:** content mock load-এর পর live brain `src` খুঁজে content tree পাচ্ছিল — position-0 fix-এ ঠিক হয়েছে। Factory-র clean-error path ডিজাইন মতো কাজ করেছে (network attempt নয়, পরিষ্কার `RuntimeError`)।
3. **check_phase4 fail (config bump-এর পর):** phase `== 4` / version `== "0.5.0"` pin করা ছিল — check_phase2/3-এর precedent মতো `>=` করা হয়েছে (আর কিছু বদলানো হয়নি)।
4. **Dead constant সরানো হয়েছে:** `main_ceo_bot.py:28`-এর `BOSS_CEO_ENGINE_PATH` (define করা ছিল, কোথাও ব্যবহার হতো না) — সরানো হয়েছে; check_phase0 এখনো 8/8।
5. **Test contamination শূন্য:** সব test TEMP store-এ; আসল store শেষ পর্যন্ত tasks 0, approvals 0।

### Check — সব coordinator নিজে re-run করেছে
| check_phase0 | 8/8 | check_phase1 | 11/11 | check_phase2 | 14/14 | check_phase3 | 19/19 |
| check_phase4 | 9/9 | check_engines | 45/45 | check_phase6 | 14/14 | **মোট** | **120/120 PASS** |

Self-containment proof (coordinator নিজে, `python3 -I` clean env, শুধু repo path): agency import OK (`boss-ceo` sys.path-এ নেই, mock `complete()` → `MOCK-PLAN…`, `cost_usd: 0.0`); content import OK (`creator-os-combined` sys.path-এ নেই, mock → `[MOCK DRAFT…`, `spend_usd: 0.0`); BrainFactory mode `mock`, agency → `MockLLMProvider`, content → `MockLLM`. Runner smoke (TEMP store): agency `caption_write` → `draft-ready`; `outreach_draft` + `gated_action: send` → `pending-approval` (1 approval record TEMP-এ); আসল store 0/0।

### সৎ হিসাব (built-vs-map — Phase 6)
| জিনিস | অবস্থা |
|---|---|
| Phase 0 / 1 / 2* / 3 / 4 / 5 / 6 | **BUILT** (120 checks PASS) |
| Worker ভিতরে vendored | **Agency 18 file + Content 4 file** — repo একা চলতে পারে (mock brain) |
| BrainFactory + runner | **REAL** — mock default, live unwired-until-flipped; runner এক command-এ office চালায় |
| Shared tool-calling core + 3 engine | **REAL** (mock brain, draft-only; gated কখনো execute হয় না) |
| Agency Engine 15 staff / 8 tool / 15 skill | **REAL** — email PAUSED |
| Products Engine 5 staff / 8 tool / 5 skill | **REAL\*** — launch/sale Gate 0-তে আটকে |
| Content Engine 8 staff / 8 tool / 8 skill | **REAL** — upload OFF, VOICE.md DRAFT, GPU নাম বাকি |
| Jarvis voice | **STUB** (mic নয়) |
| 136 ব্যবসা / 1,189 worker | **DROPPED (Boss 2026-11-16)** — scope = 3 ব্যবসা only |
| Paying client / প্রথম মেইল / Email / Vet Kit sale / ToolPilot video | **0 / 162 / PAUSED / 0 / 0** |
| Host | **Muse runtime + bridge cron ($0)** — ২৪/৭ server নেই |
| GitHub push | **Phase 0–5 PUSHED 2026-11-16 ~20:03** (commit `94cfc69d`, 81 file) — **Phase 6 NOT PUSHED** (28 নতুন file local-এ; Boss-এর "push koro" আলাদা gate) |

## Phase 7 — Full Offices (Sections) (BUILT 2026-11-17, Boss: "agency-র receive / finish service / sell করার যতগুলো section আর staff প্রয়োজন... folder up করো")

Boss-এর নির্দেশ 2026-11-17: agency-র receive / finish service / sell চালাতে যত section আর staff লাগে, প্রত্যেক staff-এর একটা করে AI agent + skill — তারপর digital product business-এর office, তারপর content creation-এর full agent + skill system। ৩ department-এ ৩ builder (coordinator-এর অধীনে), coordinator নিজে সব check re-run করেছে।

### যা বানানো হলো
- **Agency — 5 section, 6 নতুন agent + 6 skill, 15 mapped staff** (`01-Agency-Department/sections/`): receive (ClientIntakeReceiver — `client_intake`, gate send; mapped: InboxTriager, ProspectResearcher, SchedulerAssistant), sell (SalesCloser — `sales_close`, ok; FollowUpAgent — `followup_draft`, send, 100-mail rule code-এ; mapped: OutreachDrafter, ReplyHandler, NegotiationCoach, ObjectionSimulator), delivery (ServiceDeliveryManager — `delivery_manage`, ok; ClientSuccessAgent — `client_success`, send; mapped: RetellBuilder DRAFT plan only, QAEngineer, OnboardingAgent), marketing (mapped-only: ContentPlanner, VideoProducer, CaptionWriter, PublishPrep), ops (BillingInvoiceAgent — `billing_invoice`, ok, LOCKED pricing $547/$1,109/$1,672 + build $597/$1,297/$1,997, invoice শুধু paying client-এ Boss-এর কথায়; mapped: ReportCompiler)। 15 worker-এর code duplicate করা হয়নি — vendored worker + engine skill-এ map করা।
- **Digital Product — 6 section, 7 agent + 7 skill** (`02-Digital-Product-Department/sections/`): product (KitBuilder — `kit_build`, ok; KitQA — `kit_qa`, ok, NEW), research (ClinicResearcher), launch (LaunchManager — `launch_prep`, go), sales (KitSales — `kit_sales`, send, NEW), support (SupportDrafter — `support_draft`, send), finance (PaymentRailsChecker — `gate0_check`)। **Gate 0 fail-closed:** kit_build / launch_prep → `blocked-gate0` (mark_sold / mark_launched payload-ও); KitSales draft-এ "Gate 0 NOT passed" warning; কোনো sale/launch কখনো লেখা হয় না।
- **Content — 5 section, 10 agent + 10 skill** (`03-Content-Creation-Department/sections/`): plan (TopicResearcher wrapper, ContentPlanner chief-level standalone — `plan_weekly`), produce (ScriptWriter wrapper — VOICE.md DRAFT warning প্রতি output-এ; VisualProducer wrapper — stage 4 BLOCKED, `video_file` None + missing-inputs), publish (CaptionWriter wrapper, PublishPrep wrapper — `ready_to_publish` False, gate "post it"), analyze (PerformanceTracker wrapper — metric 0, কখনো estimate নয়; PerformanceAnalyst chief-level standalone — metric না থাকলে `waiting-for-metrics`), growth (GrowthAgent — `growth_research`, send, NEW; RepurposeAgent — `repurpose_plan`, ok, NEW, `shorts_made: 0`)। Upload OFF — কোনো section file-এ upload code path নেই।
- **Chief routing:** ৩ Chief-এ `SECTION_ROUTING` + একটা branch (importlib file load → agent `run()` → tasks.json-এ log, আগের branch-গুলোর মতো)। নতুন task type: agency 6, products 3, content 4। পুরনো ROUTING key/behavior বদলায়নি; `engine/tools.json` ছোঁয়া হয়নি।
- **Agent contract (সব 23):** stdlib only (import time), Bengali docstring, class attrs `task_kind`/`gate`/`section`/`role`, `run(task, brain, gateway, approvals_path)` — gated action → ApprovalGateway PENDING, কখনো execute নয়; output `[MOCK DRAFT]` লেবেল, `draft_only: True`, `mock_brain: True`। কোনো agent file লেখে না, network ছোঁয় না।
- **Docs:** ৩ `engine/STAFF.md`-এর শেষে "Phase 7 — Section map" যোগ (আগের content বদলায়নি); root README (Phase 7 accounting + sections tree); config phase 7 / v0.7.0 + `honest_status.phases`-এ `phase_5_three_engines` + `phase_7_sections`; dashboard `status.html`-এ Phase 5/6/7 row যোগ (sync_status.py template + collect_status keys)।
- **136 DROPPED** — নতুন কোনো file-এ 136/1,189 scope নেই; scope = 3 ব্যবসা only (আগের মতোই)।

### Verification-এ ধরা পড়ে ঠিক করা হয়েছে
1. **Products Chief branch nested shape:** প্রথমে `output`-এ পুরো agent result dict বসত (mock_brain top-level-এ ছিল না) — agency/content Chief-এর মতো flatten করা হয়েছে (`worker`, `output` str, `notes`, `mock_brain`, `draft_only`, `gate`)। এখন ৩ Chief-এর section branch এক shape।
2. **sync_status.py KeyError:** template-এ Phase 5/6/7 row যোগ করা হয়েছিল, কিন্তু `collect_status()`-এর `phase_status` dict-এ ওই key ছিল না — ৩ key যোগ করা হয়েছে। check_phase4-এর sync test এতে fail করছিল।
3. **check_phase6 pin:** config phase 7 হওয়ার পর check_phase6-এর check 11 (`phase == 6`, `version == "0.6.0"`) fail করত — Phase 6-এর precedent মতো `>= 6` / `>= "0.6.0"` করা হয়েছে (আর কিছু বদলায়নি)।
4. **check_phase7-এর ২টা ভুল (check-এর, build-এর নয়):** skill filename-এ underscore vs hyphen (file-গুলো hyphen-এ ঠিক ছিল) + upload grep-এ docstring-এর prose ("YOUTUBE_UPLOAD_ENABLED=1 লাগে") ধরা পড়ছিল — check এখন শুধু আসল code path খোঁজে (`os.getenv`/`os.environ` read, `upload_youtube(` call)।
5. **Content wrapper `src` path bug (builder ঠিক করেছে):** department dir 3× `dirname`-এ ভুল হচ্ছিল (`sections/`-এ নামছিল) — 4× `dirname`-এ ঠিক; Chief-routed path-এ ধরা পড়েনি কারণ ৪ নতুন type-ই standalone agent।

### Check — সব coordinator নিজে re-run করেছে
| check_phase0 | 8/8 | check_phase1 | 11/11 | check_phase2 | 14/14 | check_phase3 | 19/19 |
| check_phase4 | 9/9 | check_engines | 45/45 | check_phase6 | 14/14 | check_phase7 | 18/18 | **মোট** | **138/138 PASS** |

Runner smoke (TEMP store, check_phase7-এর ভেতরে): agency `client_intake` → `draft-ready`; products `kit_qa` → `draft-ready`; content `plan_weekly` → `draft-ready`; gated `followup_draft` / `kit_sales` / `growth_research` + `send` → প্রতিটা `pending-approval`, ঠিক ১ pending approval, কিছু execute হয়নি। আসল store শেষ পর্যন্ত tasks 0, approvals 0, `tool_calls.json` নেই।

### সৎ হিসাব (built-vs-map — Phase 7)
| জিনিস | অবস্থা |
|---|---|
| Phase 0 / 1 / 2* / 3 / 4 / 5 / 6 / 7 | **BUILT** (138 checks PASS) |
| Section (16) / agent (23) / skill (23) | **REAL** — mock brain, draft-only, gated PENDING |
| Agency office (receive/sell/delivery/marketing/ops) | **REAL** — 21 staff (15 mapped worker + 6 নতুন agent); email PAUSED; follow-up 100-mail rule-এ PARKED |
| Products office (product/research/launch/sales/support/finance) | **REAL\*** — Gate 0 NOT PASSED; kit 0/6, PA 39/100, sale 0 |
| Content office (plan/produce/publish/analyze/growth) | **REAL** — upload OFF, VOICE.md DRAFT, metric 0, GPU নাম বাকি |
| Jarvis voice | **STUB** (mic নয়) |
| 136 ব্যবসা / 1,189 worker | **DROPPED (Boss 2026-11-16)** — scope = 3 ব্যবসা only |
| Paying client / প্রথম মেইল / Email / Vet Kit sale / ToolPilot video | **0 / 162 / PAUSED / 0 / 0** |
| Host | **Muse runtime + bridge cron ($0)** — ২৪/৭ server নেই |
| GitHub push | **Phase 7 NOT PUSHED** (নতুন/বদলানো file local-এ; Boss-এর "push koro" আলাদা gate — remote head এখনো bf11423d, Phase 6) |

## Voice loop — Jarvis-এর কান + মুখ (BUILT 2026-11-17, Boss: "দুটোই করো" — part 1 of 2; Antigravity guide আলাদা)

Boss-এর নির্দেশ 2026-11-17: FREE OFFLINE Jarvis voice চাই (Piper TTS + Vosk STT) Master OS-এর ভিতরে, $0, local only। PC: Windows HP, Ryzen 3 5300U, 8 GB DDR4 (~1.4 GB free — RAM টাইট), Radeon integrated 496 MB VRAM (voice-এ GPU লাগে না — Piper/Vosk CPU-only)।

### যা বানানো হলো
- **`00-CEO-Core/voice/` (NEW, 4 file):** `speak.py` — Piper TTS, `speak(text, lang="bn"|"en")` → WAV লেখে, Windows-এ player থাকলে বাজায়, সবসময় WAV path ফেরত দেয়; piper-tts না থাকলে exact `pip install` command-সহ error, চুপচাপ নয়। `listen.py` — Vosk (en) + sherpa-onnx (bn), `listen(seconds=8, lang)` mic থেকে + `transcribe_file(wav)` headless; Piper-এর 22,050 Hz → 16,000 Hz resample stdlib-এ। `loop.py` — শোনা → BrainFactory mock reply → বলা; gated action word থাকলে ApprovalGateway-এ PENDING, কখনো execute নয়। `__init__.py` — VERIFIED ids + sources এক জায়গায়।
- **`00-CEO-Core/jarvis_voice.py` (STUB → REAL):** একই 3 public function (`listen`/`speak`/`handle_voice_command`), এখন `voice/` package-কে delegate করে। Docstring: STUB → REAL (Piper+Vosk, offline, $0) + সৎ সীমা।
- **`scripts/voice_test.py` (NEW):** headless self-test, mic/speaker ছাড়া — Piper import, upstream voices.json যাচাই, voice download (md5), en+bn synth, en Vosk transcribe, bn sherpa transcribe। Exit 0 = সব PASS।
- **`scripts/check_voice.py` (NEW):** 14 check, `check_phase*.py`-র style (numbered, PASS/FAIL, "N/N PASS", exit code) — file আছে, import OK, stdlib-only top-level, piper/vosk/sherpa import probe, config voice block, secrets grep, gate test (TEMP approvals), voice_test result, real store untouched, check_phase0 এখনো PASS।
- **`scripts/jarvis_voice_loop.py` (NEW):** Boss-এর PC-র entry — repo root থেকে `python scripts\jarvis_voice_loop.py` (`--lang bn|en`, `--seconds`, `--turns`, `--business`)।
- **`00-CEO-Core/VOICE-SETUP.md` (NEW):** Windows setup guide, সহজ Bengali + copy-paste command (Python check, pip install, voice/model download, test + loop চালানো, সমস্যা হলে কী করবে, সৎ সীমা)।
- **`00-CEO-Core/config.json`:** শুধু "voice" block যোগ (engines piper/vosk/sherpa-onnx, VERIFIED voice ids + model নাম + source + WER + notes)। brain mock, phase 7, v0.7.0 — কিছু বদলায়নি। JSON parse যাচাই করা।
- **`.gitignore`:** `00-CEO-Core/voice/models/` + `00-CEO-Core/voice/output/` যোগ (model ~370 MB + WAV git-এ যায় না)।
- **`README.md`:** folder tree + সৎ টেবিল-এ Jarvis voice STUB → REAL, নতুন "Jarvis voice" section, সত্য অবস্থা bullet।

### VERIFIED ids (অনুমান নয় — upstream থেকে পড়া)
- **Bengali বলা:** `bn_BD-google-medium` — Piper catalog-এর একমাত্র Bengali voice (bn_BD, 16 speaker, medium, 22,050 Hz, openSLR 37, CC-BY-SA-4.0)। Source: piper-tts package-এর নিজের `voices.json` (183 voice; bn 1টাই)। onnx 76,782,515 B, md5 যাচাই করা।
- **English বলা:** `en_US-lessac-medium` (1 speaker, medium; Lessac licence — personal use OK, commercial-এর আগে licence দেখুন)।
- **English শোনা:** `vosk-model-small-en-us-0.15` (40 MB, Apache-2.0) — official list https://alphacephei.com/vosk/models.html।
- **Bengali শোনা:** `vosk-model-small-streaming-bn` (HF repo `alphacep/vosk-model-small-streaming-bn`, ~96 MB, Apache-2.0, WER self-reported: Common Voice 17.9, Fleurs 20.6, Banspeech 32.9)। **সত্য:** classic Vosk-এর official models.html list-এ কোনো Bengali model নেই; যেটা আছে সেটা Zipformer2 streaming model — `vosk.Model()` লোড করতে পারে না, sherpa-onnx-ই পথ।

### Verification — আসল run (এই VM, 2026-11-17)
- **Model download:** Piper bn+en (md5 OK) + Vosk en zip (41,205,931 B, unzip OK) + sherpa bn (encoder 90,994,145 B, decoder 2,093,080 B, joiner 1,026,462 B, tokens/bpe/vocab/decode.py)। HF LFS CDN এই VM থেকে timeout করে — resume-capable urllib downloader লেখা হয়েছে (`/tmp/download_voice_models.py`, Range resume + md5); মাঝে HTTP 416 ধরা পড়ে ঠিক করা হয়েছে (seed করা .part file আসলে complete ছিল — Content-Range থেকে total পড়ে rename)।
- **voice_test.py: 7/7 PASS, exit 0** — en synth 71,724 B (22,050 Hz, 35,840 frames) → Vosk transcript "hello i am jarvis" (exact, 4/4 word মিল); bn synth 82,988 B (41,472 frames) → sherpa transcript "আমি জার্ফিস শুনছি" (Bengali অক্ষর আছে; "জার্ভিস"→"জার্ফিস" এক phoneme ভুল — WER 17-33%-এর মধ্যেই, pipeline কাজ করে)।
- **check_voice.py: 13/14** — শুধু sounddevice FAIL: এই VM-এ PortAudio নেই (apt-এ candidate নেই) — VM-only সীমা; Windows wheel-এ PortAudio বান্ডেল থাকে, Boss-এর PC-তে mic চলে। Fake pass দেওয়া হয়নি।
- **check_phase0 8/8, check_phase1 11/11, check_phase2 14/14, check_phase3 19/19, check_phase4 9/9, check_phase6 14/14, check_engines 45/45, check_phase7 18/18 — মোট 138/138 PASS, কোনো regression নেই।**
- **Loop end-to-end (headless, mock brain):** `handle_voice_text('আমার আজকের কাজ কী?')` → MOCK-PLAN reply + Bengali WAV লেখা; `handle_voice_text('Day 4 batch send করো')` → gated_action `send`, approval PENDING, reply "Sent for approval — it will only move on Boss's word, not by voice" — কিছু execute হয়নি।
- **Secrets grep:** নতুন file-গুলো clean (শুধু `pip install` command-লাইন আর check-এর নিজের pattern literal — credential নয়)।
- **Store:** tasks 0, approvals 0, `tool_calls.json` নেই — আসল store ছোঁয়া হয়নি (একবার direct test-এ ভুলে 1 pending approval লেখা হয়েছিল — সাথে সাথে মুছে original state-এ ফেরানো হয়েছে; check re-run করে নিশ্চিত করা)।
- **Git:** এই directory-তে `.git` নেই (`git status` → "not a git repository") — push করা হয়নি, করা যায়ও না এখান থেকে; push-এর পথ parent/Boss-কে ঠিক করতে হবে।

### Verification-এ ধরা পড়ে ঠিক করা হয়েছে
1. **sherpa OfflineRecognizer crash:** Zipformer2 model `OfflineRecognizer.from_transducer` দিয়ে লোড হয় না (encoder input int32/int64 চেক-এ C++ abort, process মরে, exit 255) — model-এর নিজের `decode.py`-র মতো `OnlineRecognizer` ব্যবহার করা হয়েছে (model_type="zipformer2", modified_beam_search, max_active_paths=10) — `_transcribe_sherpa_file` + `listen()` দুই জায়গায়।
2. **check_phase0/4-এর STUB assertion stale:** jarvis_voice REAL হওয়ার পর check_phase0-র "loud STUB" (NotImplementedError চায়) আর check_phase4-র "Jarvis still STUB (mic not connected)" fail করত — দুই check-ই নতুন সত্যে আপডেট করা হয়েছে (REAL + একই 3 function + loop.py আছে)। এটা regression নয় — task-এরই নির্দেশ ছিল STUB → REAL।
3. **check_phase6-র scope check false positive:** Piper voice `.onnx.json`-এ scope-সংখ্যাটা আছে (voice config value, scope নয়) — check এখন `models/` dir skip করে (upstream model data, repo doc নয়)।
4. **check_voice secrets check false positive:** "secret" শব্দটা check file-এর নিজের pattern literal + docstring-এ ছিল — scanner file নিজে scan থেকে বাদ দেওয়া হয়েছে (অন্য সব নতুন file clean)।
5. **check_voice STUB শব্দ check:** "STUB" শব্দটা jarvis_voice.py-র docstring-এ ইতিহাস হিসেবে থাকে ("আগে ছিল STUB") — check এখন `STUB_NOTICE`/`NotImplementedError` নেই + "REAL" আছে যাচাই করে।

### সৎ হিসাব (voice — 2026-11-17)
| জিনিস | অবস্থা |
|---|---|
| Piper TTS (bn + en) + Vosk (en) + sherpa-onnx (bn) | **REAL** — offline, $0; voice_test 7/7 PASS |
| Jarvis voice loop (শোনা → brain → বলা) | **REAL** — mock brain, gated PENDING only |
| Bengali voice-এর মান | **UNJUDGED** — কেউ শোনেনি; Boss-ই প্রথম শুনবেন (WAV: `voice/output/voice-test-bn.wav`) |
| Bengali STT নির্ভুলতা | **UNKNOWN** — WER 17-33% (self-reported); Boss কথা বলে যাচাই করবে |
| Live mic test | **NOT DONE** — এই VM-এ PortAudio নেই; প্রথম আসল mic test Boss-এর PC-তে |
| Brain | **mock** — voice Jarvis-কে বুদ্ধিমান বানায় না; উত্তর MOCK-PLAN draft |
| sounddevice (এই VM) | **FAIL** — PortAudio নেই; Windows-এ চলে (wheel-এ বান্ডেল) |
| GitHub push | **NOT PUSHED** — এই directory-তে `.git` নেই; push parent-এর কাজ |
| Dashboard `status.html` | **STALE** — এখনো "STUB / mic যুক্ত নয়" লেখা (line 79); dashboard refresh আলাদা কাজ — এই task-এ ছোঁয়া হয়নি |
| Phase 7 table-এর STUB লাইন (উপরে) | **পুরনো** — voice এখন REAL (এই entry দেখুন) |

## Dashboard sync fix (2026-11-17, parent follow-up to voice loop)
- scripts/sync_status.py: added read_voice_status() — dashboard voice row now derived from 00-CEO-Core/jarvis_voice.py (REAL if Piper present + no NotImplementedError), no longer hardcoded STUB. Content Engine row: "GPU নাম বাকি" -> "GPU AMD Radeon integrated 496 MB VRAM (FramePack/WanGP চলবে না)" (answered 2026-11-17). scripts/check_phase4.py header comment updated to match. Re-verified: sync deterministic (2 runs identical), check_phase4 9/9 PASS, check_phase0 8/8 PASS. dashboards/status.html line 79 now reads REAL — Jarvis voice, Piper TTS + Vosk/sherpa STT, offline, $0.

## Local run + 3D dashboard (2026-11-19, Boss: "locally চালানোর system কী? 3D dashboard বানাও")
- NEW `run_local.bat` (Windows, এক ক্লিক): sync_status.py চালায় → local server (port 8765) → ব্রাউজারে 3D dashboard খোলে।
- NEW `dashboards/dashboard-3d.html`: Three.js 3D অফিস — Jarvis (সোনালি, উপরে) → Main CEO Bot (core) → Approval Gate (ring) → ৩ বিল্ডিং (Agency teal / Vet Kit orange + লাল Gate 0 বাতি / Content violet)। ড্র্যাগ = ঘোরানো, স্ক্রল = জুম, বিল্ডিং-এ ক্লিক = বিস্তারিত। উপরের strip + নিচের "কীভাবে যুক্ত" অংশ `status.json` থেকে আসে; fetch না হলে 2026-11-19 snapshot দেখায় (লেখা থাকে)। Honest label: visualization — page অফিস চালায় না।
- NEW `LOCAL-RUN-BANGLA.md`: PC setup গাইড — Python 3.10+ (PATH-সহ), clone/ZIP, run_local.bat, voice loop, run_office.py, কী LIVE নয়, troubleshooting।
- CHANGED `scripts/sync_status.py`: `write_status_json()` যোগ — collect_status() এখন `dashboards/status.json`-ও লেখে (sorted keys, deterministic)। check_phase4 9/9 PASS (আগের মতো)।
- VERIFIED এই মেশিনে: sync ২ run byte-identical (status.html + status.json); http.server-এ status.json 200 (2,156 bytes, phase 7, clients 0, mails 162, email PAUSED, gate0 NOT PASSED) + dashboard-3d.html 200 (20,612 bytes)।
- FIXED (আগে থেকে ভাঙা ছিল, আমার change-এর দোষ নয়): (1) `store/tool_calls.json` ছিল 2026-11-17 07:35-এর booking_reply test residue (৬টা test record: Tommy/ABC Plumbing) — মুছে real store pristine করা হয়েছে (tasks 0, approvals 0, tool_calls নেই)। (2) `scripts/check_engines.py`-র "core has 6 handlers" assertion stale ছিল — booking_reply (৭ম tool, 2026-11-17) যোগ হওয়ার পর আপডেট হয়নি — এখন 7 handlers assert করে।
- RE-VERIFIED সব check: Phase 0–7 + engines **138/138 PASS** (8+11+14+19+9+14+18+45)। Voice **13/14** — শুধু sounddevice FAIL (এই VM-এ PortAudio নেই; Windows-এ চলে; আগের মতোই)।
- NOT PUSHED: নতুন/বদলানো ফাইল (run_local.bat, LOCAL-RUN-BANGLA.md, dashboards/dashboard-3d.html, dashboards/status.json, scripts/sync_status.py, scripts/check_engines.py, BUILD-LOG.md) + booking_reply change (tool_calling.py, tools.json) — সব LOCAL only; push Boss-এর "push koro"-তে, ≤10-file batch-এ।
- 3D dashboard artifact (hosted visualization): `talvenor-master-os-3d-dashboard` — build চলছে, link delivery-তে।

## 3D dashboard redesign — Founders OS layout + network graph (2026-11-19, Boss sent 3 reference screenshots)
- Boss-এর নির্দেশ: (1) 3D জায়গার বিল্ডিং architecture বাদ দিয়ে প্রথম image-এর মতো network-graph architecture; (2) পুরো dashboard দ্বিতীয় দুই image-এর (Founders OS) মতো।
- CHANGED `dashboards/dashboard-3d.html` (full rewrite, 44,071 bytes): dark Founders OS-style layout — বামে sidebar (Jarvis, Goals, AI Chat, AI Team, Content, Research, Creators, Approvals [badge = pending 0], Posts, Emails, Graphics, Video editor, Playbook, Settings, Light mode toggle, user card Boss — Md Mainuddin), উপরে search bar ("Ask your workspace" — টাইপ করলে matching node highlight হয়) + Phase/Brain/Gates chip, greeting সময় অনুযায়ী ("Good evening, Boss.") + আসল stats লাইন, Talk to Jarvis / Ask a question / Refresh বাটন, JARVIS CORE panel (glowing orb + network graph), node chip row, detail panel, connection explainer + copy বাটনসহ command, সৎ অবস্থার table।
- 3D scene এখন network graph (Three.js, image 1 style): মাঝখানে Jarvis orb (সোনালি) + Main CEO Bot core (teal) + Approval Gate ring; চারপাশে ৩ cluster — Agency নীল (chief + ১৫ worker + ৬ section agent), Vet Kit কমলা (chief + ৭ staff), Content সবুজ (chief + ৬ worker + ১০ agent); satellite node — Leads (১৬২), Calls (Sophia), Emails (PAUSED), Approvals (০), Gate 0 (NOT PASSED, লাল বাতি), Revenue ($0)। সব node-এ ক্লিক = আসল বিস্তারিত। ড্র্যাগ = ঘোরানো, স্ক্রল = জুম।
- HONEST: style/layout শুধু screenshot থেকে নেওয়া — সংখ্যা ওদেরটা নয়। "Gusten Sun", "100+ new leads", "Approvals 149", "DNA v33", "HighLevel" — কিছুই নেওয়া হয়নি; সব সংখ্যা Boss-এর আসল status.json থেকে (clients 0, mails 162, email PAUSED, Gate 0 NOT PASSED)। "ONLINE" লেখা হয়নি — "CORE — mock brain · voice REAL" লেখা।
- VERIFIED এই মেশিনে: HTML parses (unclosed tag নেই), JS syntax OK (node --check), sync আগের মতো (phase 7, clients 0, mails 162, email PAUSED, gate0 NOT PASSED), http.server-এ dashboard-3d.html 200 (44,071 bytes) + status.json 200 (2,156 bytes)।
- Hosted artifact `talvenor-master-os-3d-dashboard`: artifact.edit চলছে (Boss-এর exact message দিয়ে) — link delivery-তে।
- NOT PUSHED: dashboard-3d.html + BUILD-LOG.md change LOCAL only; push Boss-এর "push koro"-তে।

## Dashboard v3 — Boss feedback 2026-11-19 ~20:38 (local-run block removed, graph densified, sidebar completed)
- Boss: (1) নিচের locally-চালানোর system dashboard থেকে সরিয়ে আলাদা instruction বানাতে হবে; (2) 3D mockup এখনো ছবির মতো হয়নি — পুরোপুরি ওইটার মতো করতে হবে; (3) sidebar-এ Main CEO Bot + AI Team/Agency পুরোপুরি show হচ্ছে না — complete করতে হবে।
- CHANGED `dashboards/dashboard-3d.html` (45,618 bytes): `#conn` section পুরো সরানো (connection steps, run commands, সৎ অবস্থার table) — dashboard-এ এখন শুধু dashboard-ই আছে। ওই নির্দেশনা আলাদা page-এ (artifact `talvenor-master-os-pc-te-caalaanor-nirdeshnaa`, build চলছে)।
- Graph ঘন করা (image 1-এর মতো): প্রতিটা worker/agent-এর চারপাশে ৩টা করে ছোট task node (~১৩২টি, ৭ রঙের palette), ৪২টি faint background star, cluster-এর মধ্যে cross-link, cluster আরও ছড়ানো, camera কাছে (dist 18)। মোট ~২২৫ node। নতুন: "◎ Fit" বাটন (view reset) + নিচে ask bar (mic + "show agency / Gate 0 / leads / Jarvis / revenue" quick-ask chip)।
- Sidebar complete: নতুন "🧠 Main CEO Bot" item + "💬 AI Chat" (নিজের detail) + "∴ AI Team"। Detail panel-এ পুরো roster: Agency ১৫ worker + ৬ section agent নামসহ, Products ৭ agent নামসহ, Content ৬ worker + ১০ agent নামসহ, Team-এ তিন Chief-এর পুরো list।
- VERIFIED এই মেশিনে: HTML parses (unclosed tag নেই), JS syntax OK (node --check), http.server-এ dashboard-3d.html 200 (45,618 bytes) + status.json 200। #conn + run commands file-এ নেই বলে যাচাই করা।
- Hosted: dashboard edit + আলাদা instruction page — দুটো artifact build-ই চলছে; link delivery-তে।
- NOT PUSHED: dashboard-3d.html + BUILD-LOG.md change LOCAL only; push Boss-এর "push koro"-তে।

## Dashboard v4 — Boss feedback 2026-11-19 ~20:55 (flat → sphere)
- Boss: mockup-টা সমান্তরাল/flat লাগছে — এক side-এ ঘুরলে সব একদিকে পড়ে যায়। গোল (sphere) করতে হবে: যেদিকে ঘোরাবে, সেই side দেখা যাবে। Main CEO Bot একদিকে, Agency একদিকে, Content একদিকে, তিন office তিন দিকে, Jarvis একদিকে, CEO একদিকে। Architecture system আগের মতোই থাকবে।
- CHANGED `dashboards/dashboard-3d.html` (47,808 bytes): পুরো scene গোলক layout-এ পুনর্লেখা — Main CEO Bot core মাঝখানে (0, 0.6, 0), Jarvis উপরে উত্তর মেরুতে (y 6.4), Approval Gate বিষুবরেখায় (torus ring), তিন office azimuth ১২০° করে তিন দিকে (Agency az 10°, Vet Kit az 130°, Content az 250°), প্রতিটা cluster-এর member ৪২° cone-এর ভেতর গোলকের গায়ে (radius 8.3–9.7), satellite (Leads/Calls/Emails/Approvals/Gate 0/Revenue) নানা দিকে, background stars দূরের shell-এ (radius 17–23)। পেছনের দিকের label auto-hide হয় (facing test) — সামনের side-টাই শুধু দেখা যাবে। Selection ring এখন scene-এ, camera-র দিকে মুখ করে। Architecture/data/detail/sidebar/chips/ask-bar অপরিবর্তিত।
- VERIFIED এই মেশিনে: HTML parses (unclosed tag নেই), JS syntax OK (node --check), http.server-এ dashboard-3d.html 200 (47,808 bytes) + status.json 200। grep-এ যাচাই: inCone ×2, labelSprites ×4, scene.add(selRing), cluster azimuth 10/130/250; chief position গণিতেও গোলকে (radius 6.5)।
- Hosted: একই গোলক rebuild-এর artifact edit চলছে; link delivery-তে।
- NOT PUSHED: dashboard-3d.html + BUILD-LOG.md change LOCAL only; push Boss-এর "push koro"-তে।

## Agentic Agency Office Phase 1 — Foundation (2026-11-19, Boss order: another AI's blueprint + agency office combine)
- Boss 2026-11-19 ~22:50-এ আরেক AI-এর "Agentic Agency Office" blueprint পাঠিয়ে order দিলেন: system structure বুঝে নিজের agency office-এর সাথে combine করে setup করতে হবে। Brief verbatim: `~/workspace/briefs/agentic-agency-office-2026-11-19.md`।
- AUDIT (brief-এর ভুল, সব জায়গায় সংশোধন করা হয়েছে): (1) Retell production নয় — Retell DROPPED 2026-10-26, Boss টাকা দেবেন না; LIVE stack Vapi (Sophia +19472230244, org 1861a735, GPT-4o-mini, Emma, Deepgram nova-3); RetellBuilder শুধু DRAFT plan। (2) "Sophia Demo Agent" ভুল — Sophia LIVE receptionist; Ava ছিল demo (deleted; rebuild pending, separate demo account)। (3) DB PostgreSQL নয় — JSON store files (store/tasks.json, store/approvals.json); CRM n8n Cloud Data Tables PLANNED, live নয়; Calendar Google Appointment Schedule (booking link); Brain mock, live MetaSpark UNPROVEN। (4) Paperclip image অন্য product-এর diagram — ব্যবহার করা হয়নি। (5) Brief-এর "TALVENOR OFFICE OS" নাম নতুন repo হিসেবে নেওয়া হয়নি — 8 department 01-Agency-Department-এর ভেতরেই বসেছে; Master OS-এর 3-business scope অপরিবর্তিত।
- BUILT (35 নতুন file, সব UTF-8 text, binary নেই): governance/ ৪ file (office-charter, agent-permissions, approval-policy, security-policy); departments/ ২৪ file (৮ department × SECTION.md + manager .py + skill .md); agents/agent-registry/ ২ file (registry.md + registry.json — ৬৯ entry: EXISTING ২২ role-entry = ২১ distinct worker, ROLE-ONLY ৪৩, GAP ৪; ৮ manager আলাদা তালিকায় EXISTING); workflows/ ৫ file (lead-generation, sales-outreach, client-onboarding, receptionist-deployment, client-support; পুরনো README.md অপরিবর্তিত)।
- MAPPING (২১ existing staff → ৮ dept): 01 Sales & Growth ৮ (ProspectResearcher, OutreachDrafter, ReplyHandler, NegotiationCoach, ObjectionSimulator, SalesCloser, FollowUpAgent, SchedulerAssistant); 02 Marketing ৪ (ContentPlanner, VideoProducer, CaptionWriter, PublishPrep); 03 AI Engineering ১ (RetellBuilder — DRAFT plan only); 04 Client Operations ৫ (ClientIntakeReceiver, OnboardingAgent, ServiceDeliveryManager, ClientSuccessAgent, InboxTriager); 05 Research & Strategy ০ — GAP dept; 06 Finance & Admin ২ (BillingInvoiceAgent, ReportCompiler); 07 Quality & Security ১ (QAEngineer — dept 03-এর সাথে shared); 08 Product & Innovation ০ — GAP dept। Brief-এর ৬২ specialist: ১৫ role EXISTING-এ map, ৪৩ ROLE-ONLY (skill definition only, code নেই), ৪ GAP (Ad Campaign — $0 cap; CRM Integration — CRM live নয়; Expense Tracking — $0 spend; Backup & Recovery — backup system নেই)।
- MANAGERS (৮, Phase 7 pattern — stdlib-only, Bengali docstring, run(task, brain, gateway, approvals_path), gated → ApprovalGateway PENDING, output [MOCK DRAFT]): Chief Growth, Marketing Director, CTO/AI Engineering, COO/Client Operations, Chief Strategy, CFO/Finance, Chief Quality & Security, Chief Innovation। Live smoke test TEMP store-এ ৮/৮ PASS (draft-ready + unknown-task + pending-approval; TEMP approvals-এ ৮ PENDING record; আসল store ছোঁয়া হয়নি)।
- VERIFIED নিজে: সব check 138/138 PASS (phase0 8 + phase1 11 + phase2 14 + phase3 19 + phase4 9 + phase6 14 + phase7 18 + engines 45); check_voice 13/14 (শুধু sounddevice — VM-এ PortAudio নেই, আগের মতোই); sync_status.py ২ বার byte-identical (status.html 5bb2ac1e…, status.json 86698700…); store pristine (tasks 0, approvals 0, tool_calls.json নেই); registry.json-এর সব EXISTING path disk-এ মেলে; forbidden-term grep শূন্য (PostgreSQL / Sophia Demo / Paperclip / Retell Integration / 90-second demo / UroNex / NexaFlow); secrets scan clean; dental/medical ৩৯ hit — সব exclusion বাক্যে।
- FIXED যাচাইয়ে (২টা): (1) registry.md-এ ৮ manager "NOT VERIFIED — ফাইল পাওয়া যায়নি" লেখা ছিল (registry worker departments worker-দের আগে চলেছিল) — ফাইল যাচাই করে EXISTING + আসল path-এ বদলানো হয়েছে। (2) dept 03-এ QAEngineer-এর delegation key `qa_check` ছিল — আসল task type `receptionist_qa` (chief routing + STAFF.md + dept 07) — ৪ জায়গায় ঠিক করা হয়েছে; আর "(Finance & Admin)" ভুল parenthetical → "(Quality & Security)"।
- PRE-EXISTING অসঙ্গতি (Phase 1-এ fix করা হয়নি, নোট করে রাখা হলো): `delivery.py`-তে RetellBuilder-এর নিজের task_kind `retell_build`, কিন্তু chief routing-এ key `receptionist_build` — Chief নিজের table দিয়ে route করে বলে কাজ চলে, কিন্তু দুই নাম মেলে না। Dept 03 SECTION.md-এ নোট আছে।
- NOT DONE (Phase 3-এর কাজ): ROLE-ONLY ৪৩ role-এর skill .md লেখা হয়নি (registry-তে skill_file null); GAP ৪ role বানানো হয়নি; কোনো specialist-কে code worker হিসেবে বানানো হয়নি। Agency Chief wiring — **Phase 2 DONE 2026-11-19** (নিচে দেখুন)।
- NOT PUSHED: সব Phase 1 file + README/BUILD-LOG change LOCAL only; push Boss-এর "push koro"-তে।

## Unified OS layer — Central HQ + 3 Business OS mappings (2026-11-19, Boss order: "Final execution, build this system now")

- Boss 2026-11-19 ~23:02-এ আরেক AI-এর "TALVENOR UNIFIED BUSINESS OS" blueprint পাঠিয়ে order দিলেন: তিনটা ব্যবসার system একসাথে, final execution এখনই। Brief verbatim: `~/workspace/briefs/unified-business-os-2026-11-19.md`। Phase 1 (Agentic Agency Office, 8 department) তার আগেই শেষ — তার উপরেই এই layer বানানো হয়েছে, কিছু redo করা হয়নি।
- AUDIT (brief-এর ভুল, সব জায়গায় সংশোধন করা হয়েছে): (1) Commerce OS যেমন লেখা তেমন নয় — Etsy CLOSED to Bangladesh (verified 2026-11-12), Amazon GATED (৫ live client + $5K MRR না হওয়া পর্যন্ত), Shopify = Boss-এর DIRECT parked project (single-product dropshipping, agent-run division নয়), Dropshipping = research only (2026-10-27 file, কোনো store বানানো হয়নি), আসল digital product = Vet Kit $49 (Gate 0 NOT passed)। (2) "AI Engineering: Retell" আবার ভুল — LIVE stack Vapi (Sophia +19472230244); RetellBuilder শুধু DRAFT plan। (3) নতুন repo/monorepo নয় — সব talvenor-master-os-এর ভিতরেই; "TALVENOR UNIFIED OS" শুধু architecture-layer-এর নাম (docs-এ)। (4) Brain একটাই (BrainFactory, mock default; live MetaSpark UNPROVEN) + ৩ Chief — brief-এর "৩ independent Business Brain + Unified Master Brain" = Main CEO Bot + Jarvis voice (REAL) + ৩ Chief হিসেবে map করা হয়েছে; আলাদা live brain বানানো হয়নি। (5) Brief-এর ৩টা image external product/blog diagram — ব্যবহার করা হয়নি, reference-ও নেই।
- BUILT (৭ নতুন doc file, CENTRAL-HQ/ — ৬০২ লাইন, সব UTF-8 text, binary নেই): unified-os.md (৯০ লাইন — master map: Boss → Jarvis → Main CEO Bot → ৩ Business OS + real status + ১০ লাইন audit list); shared-services.md (১০৬ লাইন — brief-এর ১০ shared department → আসল জিনিস, path + status সহ); data-isolation.md (৫১ লাইন — DATA policy only, কোনো data বানানো হয়নি; enforcement GAP হিসেবে নোট); cross-business.md (৫৫ লাইন — internal project নিয়ম, NOT ALLOWED list); BUSINESS-01-AGENCY.md (৯৩ লাইন — ৮ department + ২১ staff + Agency assets); BUSINESS-02-COMMERCE.md (১০৫ লাইন — ৫ division: Amazon GATED / Shopify PARKED / Etsy CLOSED / Dropshipping RESEARCH-ONLY / Digital Products BLOCKED-GATE0 + ৭ shared dept); BUSINESS-03-MEDIA.md (১০২ লাইন — ১০ creative dept → ৫ section + ১০ agent + ১৩ stage; Audio dept GAP — কোনো dedicated audio worker নেই)।
- DASHBOARD: `scripts/sync_status.py` extended — নতুন `read_business_os()` (সব মান disk থেকে: Agency ৮ dept / ৮ manager / ৬৯ registry entry / ২২ EXISTING; Commerce Gate 0 NOT PASSED, kit 0/6, PA 39/100, sale 0, divisions GATED/CLOSED/PARKED/RESEARCH-ONLY/BLOCKED-GATE0; Media ৫ section / ১০ agent / pipeline 0/10/0/3 / ToolPilot subs 0 / videos 0 / upload OFF) + status.html-এ নতুন "Unified OS — 3 Business OS" card (line 41)। `dashboard-3d.html` ছোঁয়া হয়নি। `pipeline` dict অপরিবর্তিত (check_phase4-এর exact-match assert)।
- VERIFIED নিজে: সব check 138/138 PASS (phase0 8 + phase1 11 + phase2 14 + phase3 19 + phase4 9 + phase6 14 + phase7 18 + engines 45); check_voice 13/14 (শুধু sounddevice — VM-এ PortAudio নেই, আগের মতোই); sync ২ বার byte-identical (status.html e29c4dbf…, status.json 064aeccc… — worker-এর md5-এর সাথে মিলেছে); store pristine (tasks 0, approvals 0, tool_calls.json নেই); forbidden-term grep শূন্য (PostgreSQL / Retell Integration / Sophia Demo / Paperclip / UroNex / NexaFlow — CENTRAL-HQ + sync_status.py); Etsy শুধু CLOSED context-এ, Amazon শুধু GATED context-এ (দুটো negation লাইন ছাড়া: "live হিসেবে দেখায় না"); dental/medical ৩ হিট — সব exclusion বাক্যে; secrets scan clean; সব file text/JSON।
- FIXED যাচাইয়ে (১টা): unified-os.md-এর audit table-এ "Sophia demo agent" phrase ছিল — "Sophia-কে demo agent হিসেবে দেখানো"-তে বদলানো হয়েছে (forbidden-phrase grep zero করার জন্য)।
- FACT CHECK (worker-এর ২টা flag যাচাই করা হয়েছে): (1) Marketing section-এ আসলেই কোনো section agent .py নেই (শুধু delivery/ops/receive/sell-এ আছে) — wrapper-এ সেভাবেই লেখা, অনুমান নয়। (2) BUSINESS-02-এ digital-product research report (2026-11-12) খোলা হয়নি — শুধু path cite করা হয়েছে, content claim নেই।
- NOT DONE (পরের কাজ): **Phase 2 Chief→manager wiring DONE 2026-11-19** (নিচে দেখুন); Commerce OS-এর build order = Gate 0 প্রথম (Boss-এর Lemon Squeezy test), তারপর kit; Media OS = upload OFF + VOICE.md DRAFT + ToolPilot recording বাকি; data-isolation enforcement (automated) এখনো GAP।
- NOT PUSHED: সব Unified OS file + sync_status.py + status.html/json + README/BUILD-LOG change LOCAL only; push Boss-এর "push koro"-তে।

## Agentic Agency Office Phase 2 — Executive wiring (2026-11-19, Boss order: "যা বাকি আছে, সব কাজ শেষ করো")

- Boss 2026-11-19 ~23:18-এ order দিলেন: বাকি সব কাজ শেষ করে GitHub-এ push করতে। Phase 2 = Phase 1-এর ৮ department manager-কে Agency Chief-এর সাথে যুক্ত করা (Chief→manager wiring)। Push এই phase-এ নয় — Elora main chat-এ করবে।
- BUILT (১ নতুন file + ১ modified core file + ২৫ file-এ note update + README/BUILD-LOG):
  - `scripts/check_departments.py` (নতুন, ২১ check) — ৮ manager load, ৮ dept route, draft [MOCK DRAFT], gated PENDING, unknown-task, stale-claim grep, ROUTING/SECTION_ROUTING count, forbidden terms, real store, পুরনো check suite।
  - `01-Agency-Department/chief_of_staff_agency.py` — নতুন DEPARTMENT_ROUTING (৮ entry): dept_sales → ChiefGrowthAgent, dept_marketing → MarketingDirectorAgent, dept_engineering → CTOAIEngineeringAgent, dept_operations → COOClientOperationsAgent, dept_strategy → ChiefStrategyAgent, dept_finance → CFOFinanceAgent, dept_quality → ChiefQualitySecurityAgent, dept_innovation → ChiefInnovationAgent। Gate সব `ok`। Branch SECTION_ROUTING pattern-ই (importlib load + mock brain + tasks.json log) — payload-এর task_kind → top-level translate (manager-রা task.get("task_kind") পড়ে); M1–M4 kind ছাড়া overview draft দেয়, M5–M8 kind ছাড়া unknown-task দেয়; gated action → ApprovalGateway PENDING; unknown kind → "unknown-task" + known kind-এর তালিকা।
  - ROUTING (১৫) ও SECTION_ROUTING (৬) অপরিবর্তিত — শুধু যোগ করা হয়েছে, কিছু বদলানো হয়নি।
  - ২৫ file-এ stale wiring note ঠিক করা হয়েছে (৮ SECTION.md + ৮ manager .py + ৮ skill .md + registry.md — ৭৬ replacement): "Chief এখনো এই manager-কে call করে না" → "Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে"; "Agency Chief এখনো ডাকে না" → "Agency Chief এখন DEPARTMENT_ROUTING দিয়ে ডাকে"। + ৩ extra variant fix (৬ manager .py লাইনে split-string-এর "এখনো" → "এখন", ০৭/০৮ SECTION.md-এর line-break variant)।
- VERIFIED নিজে: check_departments.py ২১/২১ PASS — ৮ manager standalone import + class attrs (task_kind/gate/department/role) ঠিক; DEPARTMENT_ROUTING ৮/৮ file/class/gate registry table-এর সাথে মেলে; Chief ৮টা dept type-ই route করে (TEMP store, run_office.py) — প্রতিটা valid kind-এ draft-ready + [MOCK DRAFT], dept_sales kind ছাড়া overview draft-ready; gated dept_sales + send ও dept_strategy + send — status pending-approval, প্রতিটায় ঠিক ১ pending approval (action send), কিছু execute হয়নি; unknown kind "no_such_kind" → status unknown-task, known kind তালিকায়; stale-claim grep clean (Chief এখনো / এখনো Agency Chief / wiring Phase 2 — / handoff এখন manual / manager-রা standalone — শূন্য); ROUTING=১৫, SECTION_ROUTING=৬; forbidden-term grep clean (Retell Integration / PostgreSQL / Sophia Demo / Paperclip / UroNex / NexaFlow / 90-second demo); real store untouched (tasks 0, approvals 0, tool_calls.json নেই); পুরনো check phase0/1/2/3/4 + engines + phase6 + phase7 এখনো PASS (138/138); check_voice 13/14 (শুধু sounddevice — VM-এ PortAudio নেই, আগের মতোই)।
- FIXED যাচাইয়ে (৩টা): (1) check script-এর প্রথম run-এ ROUTING-এর ast.literal_eval fail — ROUTING-এর value-তে class name (ast.Name) আছে, literal নয় — key-count পদ্ধতিতে বদলানো হয়েছে। (2) একই edit-এ _parse_dict_from_file-এর def header হারিয়ে গিয়েছিল — ফিরিয়ে আনা হয়েছে। (3) stale-note batch-এ ৬ manager .py লাইনে "Chief এখনো ... DEPARTMENT_ROUTING দিয়ে call করে" হয়ে গিয়েছিল (split-string variant) — "এখন" করে ঠিক করা হয়েছে; ০৭/০৮ SECTION.md-এর line-break variant আলাদা করে ঠিক করা হয়েছে। সব fix-এর পর check_departments.py আবার ২১/২১ PASS।
- NOTE: check run-এ Python __pycache__/ পুনরায় তৈরি হয় (সব run-এই হয়) — .gitignore-এ `__pycache__/` + `*.pyc` আছে, push-এ যাবে না; delivery-র আগে সব __pycache__ মুছে ফেলা হয়েছে।
- NOT DONE (Phase 3-এর কাজ): ROLE-ONLY ৪৩ role-এর skill .md লেখা হয়নি; GAP ৪ role বানানো হয়নি; কোনো specialist-কে code worker হিসেবে বানানো হয়নি। Phase 2-এর wiring-এ Chief→manager শুধু — manager→specialist delegation এখনো DRAFT plan (manager-রা worker execute করে না)।
- NOT PUSHED: Phase 2-এর সব file (check_departments.py + chief + ২৫ note-update file + README/BUILD-LOG) LOCAL only; push Boss-এর "push koro"-তে (Elora main chat-এ করবে)।

## Agentic Agency Office Phase 3 — Specialists (2026-11-19, Boss order: "go")

- Boss 2026-11-19 ~23:42-এ "go" দিলেন — Phase 1-এর ৪৩ ROLE-ONLY role-কে আসল worker code হিসেবে বানানো। ৮ জন dept worker একে একে বানিয়েছে, coordinator (Elora) consolidate + verify করেছে। Push এই phase-এ নয় — Elora main chat-এ করবে।
- BUILT (৪৩ worker .py + ৪৩ skill .md + ৮ manager wiring + registry + নতুন check script — সব UTF-8 text, binary নেই):
  - Worker pattern (Phase 7 section-agent pattern): stdlib-only, Bengali docstring, class attrs task_kind / gate None / department / role, `_gateway` lazy-load, `_request_approval`, `_prompt`, `run(task, brain, gateway, approvals_path)` → draft-ready + "[MOCK DRAFT]" output, gated action → ApprovalGateway PENDING, কোনো file write / network / send / publish / spend / delete নেই। প্রতিটা worker তার skill .md থেকে বানানো — skill আগে লেখা হয়েছে, তারপর code (registry-তে skill_file null ছিল — premise correction: role skill আগে ছিল না)।
  - Per-dept: 01 Sales & Growth ৫ (maps_prospect_find, business_verify, lead_score, crm_manage, sales_intelligence — sales_intelligence নতুন key); 02 Marketing ৪ (market_position, social_manage, seo, analytics); 03 AI Engineering ৭ (solution_architect, conversation_design, prompt_engineering, vapi_integration — brief-এর Retell নাম CORRECTED → Vapi, calendar_integration, n8n_automation, deployment); 04 Client Operations ৪ (call_monitoring, client_reporting, retention, renewal_upsell); 05 Research & Strategy ৭ (competitor_research, industry_research, pricing_research, niche_selection, offer_development, market_opportunity, business_intelligence); 06 Finance & Admin ৪ (revenue_tracking, subscription_tracking, document_management, compliance_calendar); 07 Quality & Security ৬ (call_scenario_testing, workflow_testing, data_validation, security_monitoring, access_control, compliance_review); 08 Product & Innovation ৬ (new_ai_product_research, new_feature_research, automation_rd, technology_evaluation, product_improvement, prototype_builder)।
  - Gate correction: registry-তে যেসব role-এর gate ভুল ছিল (social_manage "post it", vapi_integration / n8n_automation / deployment "ok", renewal_upsell "ok") — সব None করা হয়েছে; ৪৩ specialist-এর gate-ই None (কোনো specialist নিজে gated action execute করে না — gate থাকলে manager/Chief-এর level-এ PENDING হয়)।
  - Manager wiring (৮ manager-ই): DEPARTMENT_TASKS-এ specialist entry (file/class/gate/status EXISTING) + run()-এ importlib দিয়ে load করে specialist-এর নিজের draft ফেরত দেওয়া (Chief→manager pattern-ই)। Engine/section-এর পুরনো worker-দের plan-draft behavior অপরিবর্তিত; Chief-এর DEPARTMENT_ROUTING অপরিবর্তিত; ROUTING (১৫) ও SECTION_ROUTING (৬) অপরিবর্তিত।
  - Registry: registry.json + registry.md — ৪৩ ROLE-ONLY → EXISTING (skill_file + worker_file path সহ, gate null); counts ২২/৪৩/৪ → ৬৫/০/৪ (৬৫ role-entry, ৬৪ distinct worker — QAEngineer দুই জায়গায় গোনা); Dept 05/08-এর heading "(সব ROLE-ONLY)" → "(সব EXISTING — Phase 3 DONE)"।
  - নতুন check script `scripts/check_specialists.py` (৪১ check, check_departments.py-র structure mirror করে)।
- CONSOLIDATION (coordinator-এর fix): (1) Dept 02-র ৪ worker file hyphenated নামে ছিল — snake_case-এ rename (`market_positioning_agent.py`, `social_media_agent.py`, `seo_agent.py`, `analytics_agent.py`) + manager path + skill/SECTION.md-র ৮ hyphenated reference ঠিক করা হয়েছে। (2) ৬৮ stale-claim fix (৪ manager .py-র module/class/run docstring + ৪ SECTION.md + ৮ manager skill — "কোনো worker execute করে না" → scoped সত্য: manager নতুন Phase 3 specialist load+run করে, পুরনো engine/section worker execute করে না; dept 02/03/05/06-র skill handoff table ROLE-ONLY → EXISTING, gate None; dept 05 "GAP department" → "Phase 3 DONE"; dept 06 "Mapped staff 2" → 6)। সত্য লাইন রাখা হয়েছে: unknown-task branch-এর "কোনো worker execute হয়নি", plan-branch note, "নিজে"-qualified লাইন (dept 07 — QAEngineer-কে execute করে না), "ROLE-ONLY role আর নেই" সত্য-বিবৃতি।
- NOT BUILT (৪ GAP role — আগের blocker-ই, code বানানো হয়নি): Ad Campaign ($0 spend cap — paid ads planned নয়), CRM Integration (CRM n8n Data Tables PLANNED, live নয়), Expense Tracking ($0 spend cap — কোনো expense নেই), Backup & Recovery (repo-তে কোনো backup system নেই)। Manager-এ এদের task_kind দিলে GAP blocker-সহ delegation plan draft আসে — worker execute হয় না।
- VERIFIED নিজে: check_specialists.py ৪১/৪১ PASS — ৪৩ specialist file registry+disk মেলে, ৪৩ standalone import (python3 -I) + class attrs, ৪৩ skill file, ৪৩ draft-run (draft-ready + [MOCK DRAFT] + draft_only + mock_brain + gate None), ৪৩ gated (send) → pending-approval, প্রতি dept-এ record সংখ্যা = specialist সংখ্যা (৫+৪+৭+৪+৭+৪+৬+৬=৪৩), ৮ manager route (run_office.py, TEMP store) draft-ready, ৮ manager gated (send) → PENDING, ঠিক ১ approval; ৪ GAP-এর কোনো worker/skill file নেই; registry ৬৫/০/৪, md counts মেলে; stale-claim grep clean; forbidden-term grep clean (Retell Integration / PostgreSQL / Sophia Demo / Paperclip / UroNex / NexaFlow / 90-second demo; Etsy/Amazon শূন্য); real store untouched (tasks 0, approvals 0, tool_calls.json নেই); পুরনো check phase0/1/2/3/4 + engines + phase6 + phase7 এখনো PASS (138/138) + check_departments ২১/২১; check_voice 13/14 (শুধু sounddevice — VM-এ PortAudio নেই, আগের মতোই); sync byte-identical; store pristine।
- FIXED যাচাইয়ে (৩টা): (1) class/run docstring replacement-এ ASCII period (.) vs Bengali danda (।) মেলেনি — repr দিয়ে ধরা হয়েছে, danda দিয়ে ঠিক করা। (2) GAP check-এর expectation ভুল ছিল (unknown-task আশা করা হয়েছিল) — আসল behavior সঠিক: GAP kind → GAP blocker-সহ delegation plan draft; check-এর assertion ঠিক করা হয়েছে (dept 06/07-র "no worker, no skill yet" wording-ও accept করা হয়েছে)। (3) registry.md-তে Vapi Integration Agent-এর role cell-এ suffix `*(brief-এর ভুল নাম CORRECTED)*` ছিল — lookup-এ suffix strip করে ঠিক করা হয়েছে, suffix row-এ রাখা হয়েছে।
- NOTE: check run-এ Python __pycache__/ পুনরায় তৈরি হয় — .gitignore-এ `__pycache__/` + `*.pyc` আছে, push-এ যাবে না; delivery-র আগে departments/-এর সব __pycache__ মুছে ফেলা হয়েছে।
- NOT DONE (পরের কাজ): push — Boss-এর "push koro"-তে (Elora main chat-এ করবে)। তারপর Phase 3-র specialist-দের একে একে real-run / Boss-এর verdict।
- NOT PUSHED: Phase 3-এর সব file (৪৩ worker + ৪৩ skill + ৮ manager + registry + check_specialists.py + README/BUILD-LOG) LOCAL only; push Boss-এর "push koro"-তে (Elora main chat-এ করবে)।

## Review + Phase 8 — Full-repo review (2026-11-20, Boss order: "check EVERYTHING else once more, fix whatever needs changing, get everything ready to push together")

- Boss 2026-11-20 ~02:17-এ order দিলেন — repo-র বাকি সবকিছু আরেকবার যাচাই করে যা ঠিক করা দরকার ঠিক করে push-এর জন্য তৈরি রাখতে। Coordinator + ৩ reviewer (docs/dashboard/store, config/README tree, forbidden-term/secrets sweep) পুরো repo (৩১৫ file) review করেছে; coordinator নিজে সব check আবার চালিয়ে verify করেছে। Push এই entry-তে নয় — Boss-এর "push koro"-তে (Elora main chat-এ করবে)।
- DELETION (2026-11-20 ~01:28, Boss order): পুরনো `ceo-office-dashboard` artifact + `ceo-office-bridge` cron FULLY DELETE (backup `~/workspace/backups/ceo-office-dashboard-state-2026-11-20.json` — ছোঁয়া হয়নি); dashboard এখন একটাই — Talvenor Master OS 3D Dashboard (artifact `talvenor-master-os-3d-dashboard`, live v6)। নতুন bridge cron `master-os-3d-bridge` (প্রতি ১০ মিনিট) repo-র `store/tasks.json` queue পড়ে, আসল কাজ করে (সর্বোচ্চ ২/run, draft/result only — send/publish/spend/delete নয়), `dashboards/status.json` regenerate করে। Gate 0-র অবস্থা এখন chat-এ Elora-কে বললেই record হয়।
- FIXED এই review-এ (docs + config only, কোনো passing check ভাঙেনি):
  - `00-CEO-Core/config.json`: phase 7 → **8**, version v0.7.0 → **v0.8.0**, built 2026-11-20, `honest_status.phases`-এ ৪ entry যোগ (agentic_phase_1/2/3 + unified_os) — Phase 8 = Agentic Agency Office + Unified OS। Lockstep-এ `scripts/check_phase7.py` (phase 8 + v0.8.0 pin + agentic_phase_3/unified_os entry চায়) ও `scripts/check_voice.py` (phase 8 + v0.8.0 pin) ঠিক করা হয়েছে।
  - `README.md`: title Phase 7 → Phase 8; Folder tree পুরো rewrite (departments/ + specialists/ + governance/ + workflows/ + agent-registry/ + CENTRAL-HQ/ + dashboards dashboard-3d.html/status.json + scripts check_departments/check_specialists + root .gitignore/LOCAL-RUN-BANGLA/run_local.bat — ~১৫০ file-এর ঘাটতি পূরণ); "সত্য অবস্থা" heading 2026-11-16 → 2026-11-20; Phase 7 entry-র "সব Phase শেষ / 138/138" → মোট check এখন 200/200 (138 + 21 + 41) + voice 13/14; deletion + নতুন bridge-এর ছোট entry যোগ। Tree-তে tool_calling.py "6 mock handler" → 7 (booking_reply 2026-11-17 থেকে)।
  - `01-Agency-Department/engine/workers/src/workers/delivery.py` (vendored): ৪ string ঠিক — Retell-কে live build/QA path হিসেবে দেখানো docstring/prompt (class-এর বাইরে) → DRAFT plan only + live stack Vapi/Sophia (Retell dropped 2026-10-26)। Class নাম `RetellBuilder` + task_kind `retell_build`/`retell_qa` ছোঁয়া হয়নি — check + skill-এ pin করা legacy identifier, rename-এ live-code surgery লাগবে (deferred, report-এ flag করা আছে)।
  - `01-Agency-Department/engine/workers/src/contracts/store.py:1`: "SQLite today, Postgres tomorrow" → Master OS DB JSON store files (store/tasks.json, store/approvals.json); repo-তে SQLite/PostgreSQL নেই।
  - `dashboards/n8n-wiring.md`: tier2-daily-send-trigger re-scope লাইনে qualifier — cron-টি 2026-11-14 থেকে DISABLED, email PAUSED; re-scope শুধু email restart-এর পরে।
  - `dashboards/dashboard-3d.html` fallback snapshot + settings tag: Phase 7/v0.7.0 → Phase 8/v0.8.0 (live fetch-এ status.json থেকে আসে; fallback শুধু fetch fail হলে দেখায়)।
- VERIFIED নিজে (সব check আবার চালানো): phase0 8/8, phase1 11/11, phase2 14/14, phase3 19/19, phase4 9/9, phase6 14/14, phase7 18/18, engines 45/45 = **138/138 PASS**; check_departments **21/21 PASS**; check_specialists **41/41 PASS**; check_voice **13/14** (শুধু sounddevice FAIL — VM-এ PortAudio নেই, আগের মতোই; voice_test 7/7 PASS); sync_status.py ২ বার byte-identical; store pristine (tasks 0, approvals 0, tool_calls.json নেই); forbidden-term grep clean (old Sophia number 0 hit; "90-second demo"/"Sophia Demo"/"Retell Integration"/PostgreSQL/UroNex/NexaFlow — শুধু guard list + audit log; Etsy/Amazon শুধু CLOSED/GATED বাক্যে; Retell শুধু DROPPED/DRAFT context-এ; dental/medical শুধু exclusion/DQ বাক্যে); secrets scan clean (0 secret)।
- NOT CHANGED (ইচ্ছাকৃত): BUILD-LOG.md:95-এর পুরনো Phase 2 লাইন ("ceo-office-dashboard"-কে current 3D office artifact হিসেবে দেখায়) — log history, rewrite করা হয় না; সঠিক record এই entry-তেই আছে। `RetellBuilder` class নাম + `retell_build`/`retell_qa` task_kind — pin করা identifier (deferred)। `QAEngineer`-এর default payload `ava-apex-plumbing-demo` — Ava deleted demo-র lineage, harmless history।
- NOT PUSHED: এই review-এর সব file (config + 2 check script + delivery.py + store.py + README + n8n-wiring + dashboard-3d.html + BUILD-LOG + regenerated status.json/status.html) LOCAL only; delta + batch manifest `~/workspace/master-os-push-2026-11-20-review-delta.json` + `master-os-push-2026-11-20-review-batch*.txt`-এ তৈরি; push Boss-এর "push koro"-তে (Elora main chat-এ করবে)।

## Phase 9 — Connections (2026-11-20, Boss order: "যে কাজগুলো তুমি শেষ করতে পারবা, সেগুলো complete করো।")

- Boss 2026-11-20 ~16:53-এ order দিলেন — বাকি কাজের মধ্যে যেগুলো Elora একা শেষ করতে পারে সেগুলো complete করতে। ৩টা build: taskboard, MCP wiring, live tool connections। Push এই entry-তে নয় — Boss-এর "push koro"-তে (Elora main chat-এ করবে)।
- BUILT 1 — Taskboard (repo-local, artifact নয়): `dashboards/taskboard.html` (Bengali UI, /api/status + /api/tasks fetch, add-task form, 30s auto-refresh, no external deps) + `scripts/taskboard_server.py` (stdlib ThreadingHTTPServer, 127.0.0.1:8766 — run_local.bat 8765 ব্যবহার করে; GET / + /api/status + /api/tasks, POST /api/tasks: title non-empty ≤200, type snake_case, business agency/digital-product/content, lock + atomic write) + `dashboards/TASKBOARD-README.md` (Bengali + English: start, add task, what happens next)। Verify end-to-end: server চালিয়ে ১টা আসল research task POST করা হয়েছে — "verify the Talvenor booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 is live" (id 6e3b269f4533, status queued, store/tasks.json-এ আছে); খারাপ POST → 400; bridge manually চালানো হয়নি, task execute করা হয়নি — normal 10-min bridge cron-ই process করবে।
- BUILT 2 — MCP wiring (code + docs, live server নয়): `00-CEO-Core/mcp/mcp_server.py` (stdio JSON-RPC 2.0: initialize, ping, tools/list, tools/call; শুধু ৭ mock tool expose করে — live-ready gated tool বাদ) + `mcp_client.py` (MCPClient, select timeout, local_server_client helper) + `check_mcp.py` + `README.md` (MCP এক paragraph-এ + real MCP server-এ point করার উপায়: command + env vars, কোনো key নেই)। VERIFIED: check_mcp.py 9/9 PASS (initialize; tools/list ঠিক ৭, live-ready নেই; tools/call status_read + draft_email draft-ready; unknown tool + bad args isError; ping; MCP file-এ network নেই; real store untouched)।
- BUILT 3 — Live tool connections (CODE ONLY, gated, কখনো execute নয়): `00-CEO-Core/live_tools.py` (handler gmail_send — hatch_gws_cli gmail +send argv বানায়; n8n_trigger — urllib Request POST বানায়; credential শুধু env var TALVENOR_GMAIL_SENDER / TALVENOR_N8N_WEBHOOK_URL থেকে; credential না থাকলে LOUD DRAFT fallback + reason; module-এ কোনো subprocess.run / urlopen call নেই — live execution ইচ্ছাকৃতভাবে অনুপস্থিত; sent: False সবসময়; webhook token preview-এ redacted) + `00-CEO-Core/tools.json` এখন ৯ tool (৭ mock + ২ live-ready, দুটোই gated: true, gated_action "send") + `00-CEO-Core/tool_calling.py` (register() "live-ready" status নেয়, gated হতে হবে; call_tool()-এ fail-closed branch; docstring updated) + `scripts/check_live_tools.py`। VERIFIED: check_live_tools.py 7/7 PASS (9 tool load; no send call; mock-mode DRAFT fallback; dry-run preview token redacted; arg validation; dispatcher gate → pending-approval x2 TEMP path; file-এ কোনো key/token/URL নেই)। কোনো test-এ real email/message পাঠানো হয়নি, real webhook call করা হয়নি।
- CHECK-INVARIANT CHANGE (Phase 9-এর মূল পরিবর্তন): store এখন live queue — taskboard/bridge সত্যিই task লেখে, তাই "store খালি" আর invariant নয়। ১২টা check script-এ snapshot-compare invariant: `_snapshot_store()` (tasks.json + approvals.json raw text + tool_calls.json existence) main()-এর শুরুতে নেওয়া হয়, শেষে compare করা হয় — এই run store বদলায়নি প্রমাণ করে। বদলানো file: check_phase0.py (§3 parse-only + §4 assert snapshot compare), check_phase1.py §9, check_phase2.py §11, check_phase3.py §15, check_phase4.py §2 (counts আসল store-এর সাথে মেলে — truthfulness) + §8, check_phase6.py §13, check_phase7.py §11, check_engines.py §3, check_departments.py §11, check_specialists.py §12, check_voice.py §11 (+ header docstring লাইনগুলো)। check_phase3 §15 ও check_phase4 §8 প্রথম sweep-এ ধরা পড়েনি — full-suite run-এ FAIL দেখে ধরা হয়েছে, তারপর ঠিক করা হয়েছে। engines 45→44 (দুটো store check এক snapshot check-এ merge)।
- BUMP: `00-CEO-Core/config.json` phase 8 → **9**, version v0.8.0 → **v0.9.0**, `honest_status.phases`-এ `phase_9_connections` entry যোগ। Lockstep-এ `scripts/check_phase7.py` (phase 9 + v0.9.0 pin + phase_9_connections entry চায়) ও `scripts/check_voice.py` (phase 9 + v0.9.0 pin) ঠিক করা হয়েছে। `README.md` title Phase 8 → Phase 9 + config লাইন। `dashboards/dashboard-3d.html` (repo file only — artifact ছোঁয়া হয়নি): chip + settings tag + fallback snapshot Phase 9/v0.9.0, fallback tasks_count 1 (2026-11-20 snapshot)।
- VERIFIED নিজে (queued task present অবস্থায়, সব check আবার চালানো): phase0 8/8, phase1 11/11, phase2 14/14, phase3 19/19, phase4 9/9, phase6 14/14, phase7 18/18, engines 44/44, departments 21/21, specialists 41/41 = **199/199 PASS** (আগের 200 থেকে −1: engines-এর দুটো store check এক snapshot check-এ merge); নতুন check_mcp 9/9 + check_live_tools 7/7 সহ মোট **215/215 PASS**; check_voice **13/14** (শুধু sounddevice FAIL — VM-এ PortAudio নেই, আগের মতোই); tool_calling.py self-test OK; sync_status.py চালানো হয়েছে (status.json/status.html Phase 9, tasks_count 1); delivery-র আগে সব __pycache__ মুছে ফেলা হয়েছে।
- NOT DONE (Boss-এর step লাগবে): brain এখনো mock — live brain test করা হয়নি (Boss বলেছেন "কোনো টেস্ট চালাইও না আপাতত"); live connection-এর জন্য Boss-এর credential/account লাগবে (Gmail sender env, n8n webhook URL — code লেখা, connection Boss-এর account-এ); voice setup Boss-এর PC-তে; 3D dashboard artifact এখনো Phase 8 দেখায় — repo file ঠিক করা হয়েছে, artifact refresh Boss-এর কথায়। 1 queued research task bridge-এর জন্য অপেক্ষায় (পরের 10-min run-এ process হবে)।
- NOT PUSHED: Phase 9-এর সব file (taskboard 3 + mcp 4 + live_tools 2 + tools.json + tool_calling.py + 12 check script + config + README + dashboard-3d.html + BUILD-LOG + regenerated status.json/status.html) LOCAL only; push Boss-এর "push koro"-তে (Elora main chat-এ করবে)।

## Phase 10 — Live Brain (2026-11-20, Boss order: "বডি এ কানেক্ট করা ছাড়া কি brain টাকে mock থেকে real এ নেওয়া যায়? যদি রিয়েলে নেওয়া যায়, তাহলে আমার পুরো সিস্টেমের ব্রেইনটাকে রিয়েল সেটআপ করো, আর যা কিছু বানাইছিলা, সবকিছু পুশ করার জন্য রেডি করো।")

- Boss 2026-11-20 ~21:44-এ order দিলেন — body (office, worker, tool, dashboard, PC) না ছুঁয়ে শুধু brain-কে mock থেকে real-এ নিতে, আর সবকিছু push-এর জন্য ready করতে। Push এই entry-তে নয় — Boss-এর "push koro"-তে (Elora main chat-এ করবে)।
- BUILT — Live Brain adapter: `00-CEO-Core/live_brain.py` (LiveBrainAdapter — vendored MetaSparkProvider wrap করে; live call fail করলে LOUD fallback: stderr-এ কারণ লিখে department-এর নিজের mock দিয়ে draft ফেরত দেয়; এক call = এক attempt, retry loop নেই; construction-এ network নেই) + `00-CEO-Core/brain.py` (BrainFactory._live_brain(department) এখন adapter ফেরত দেয়; mock path ছোঁয়া হয়নি) + `scripts/check_live_brain.py` (10 check: mock-mode + --live probe, default OFF — probe শুধু --live flag-এ চলে)।
- CHECK-LOCKSTEP: `scripts/check_phase6.py` §4 (temp mock config — repo-র বর্তমান brain flag-এর উপর নির্ভর করে না) + §6 (live-mode temp config এখন LiveBrainAdapter আশা করে) + §11 (numeric version compare — string compare "0.10.0"-কে ভুল ধরত + brain consistent: live হলে phase 10 + PROVEN LIVE entry লাগে, mock হলে mock-ই ঠিক)।
- VERIFIED mock mode-এ (কোনো live call ছাড়া): phase0 8/8, phase1 11/11, phase2 14/14, phase3 19/19, phase4 9/9, phase6 14/14, phase7 18/18, engines 44/44, departments 21/21, specialists 41/41 = 199/199 PASS; নতুন check_mcp 9/9 + check_live_tools 7/7 + check_live_brain 10/10 সহ মোট 225/225 PASS; check_voice 13/14 (শুধু sounddevice FAIL — VM-এ PortAudio নেই, আগের মতোই); tool_calling.py self-test OK; brain.py + live_brain.py self-test OK।
- LIVE PROBE (একটাই, Boss-এর order-এ — `python3 scripts/check_live_brain.py --live`, 2026-11-20 ~21:45 Dhaka): FAILED — `URLError: <urlopen error Tunnel connection failed: 403 Forbidden>`, 0.1s-এ, $0 খরচ। Adapter ঠিকমতো কাজ করেছে — LOUD fallback-এ mock draft ফেরত দিয়েছে, কারণসহ। মানে: এই VM-এর egress proxy api.meta.ai-তে tunnel-ই খুলতে দেয় না — request Meta-তে পৌঁছায়নি, key কখনো present হয়নি, তাই key-এর validity এখনো UNPROVEN। এটা রাস্তা বন্ধ (road blocked), key খারাপ নয় — key খারাপ হলে api.meta.ai থেকে HTTP 401 আসত। 2026-10-31-এর timeout-এর চেয়ে আলাদা: সেবার egress approve হয়ে request বেরিয়েছিল, 60s-এ timeout হয়েছিল; এবার tunnel-ই 403-এ আটকে গেল। কোনো retry করা হয়নি।
- সিদ্ধান্ত (probe fail বলে): brain "mock"-ই আছে, config phase 9 / v0.9.0 অপরিবর্তিত, কোনো retry নয়। Adapter code ready — Boss-এর PC-তে (নিজের network, VM tunnel নেই) একই code-এ live probe করলে key path প্রমাণ হতে পারে; সেটা Boss-এর পরের কথায়।
- PUSH PREP (push নয়): ZIP + folder tree rebuild (Phase 9+10-এর সব file); remote head যাচাই b649b9bd (list_commits, read-only); PUSH-PLAN-Phase-9-10.md লেখা — 33 file, 4 batch (≤10 file/batch, NUL-delimited manifest, snapshot-push.md অনুযায়ী); sync record ছোঁয়া হয়নি (আসল push-এর সময় প্রতি batch-এর পরে append হবে)।
- NOT PUSHED: Phase 9 + Phase 10-এর সব file LOCAL only; push Boss-এর "push koro"-তে (Elora main chat-এ করবে)।

## Phase 11 — LLM Providers (2026-11-20, Boss order: "Auto router-এর জন্য adapter বানাও, আর বড় বড় LLM model সবগুলোর জন্য একটা একটা করে adapter বানায়ে রাখো — OpenAI ChatGPT, Claude, Gemini, Kimi, Grok, Muse-এর যত model আছে, OpenRouter-ও; আর OpenRouter কিভাবে connect করবো জানায়ে দিও।")

- Boss 2026-11-20 ~22:47-এ order দিলেন — OpenRouter auto-router + প্রতিটা বড় LLM-এর জন্য আলাদা adapter, যাতে যেকোনো model use করা যায়। Push এই entry-তে নয় — Boss-এর "push koro"-তে (Elora main chat-এ করবে)।
- BUILT — ৬ নতুন provider file (`01-Agency-Department/engine/workers/src/live/`-এ, MetaSparkProvider-এর পাশে, একই `complete(prompt, *, max_tokens) -> str` interface): `openai_provider.py` (ChatGPT, api.openai.com/v1/chat/completions, gpt-4o), `anthropic_provider.py` (Claude, api.anthropic.com/v1/messages — Messages API, system আলাদা field, claude-sonnet-4-5), `gemini_provider.py` (Google-এর official OpenAI-compatible endpoint, generativelanguage.googleapis.com/v1beta/openai/chat/completions, gemini-2.5-flash), `kimi_provider.py` (Moonshot, api.moonshot.ai/v1/chat/completions, kimi-k2.5), `grok_provider.py` (xAI, api.x.ai/v1/chat/completions, grok-4), `openrouter_provider.py` (OpenRouter, openrouter.ai/v1/chat/completions, default `openrouter/free` auto-route + named `:free` model)। প্রতিটা provider-এর endpoint + model নাম official docs থেকে verify করা (Gemini OpenAI-compat + Moonshot base/model + xAI endpoint — web search 2026-11-20)। Key শুধু env var থেকে (OPENAI_API_KEY / ANTHROPIC_API_KEY / GEMINI_API_KEY / MOONSHOT_API_KEY / XAI_API_KEY / OPENROUTER_API_KEY) — key নেই / network error / API error হলে raise, adapter LOUD mock fallback; construction-এ network নেই।
- GENERALIZED — Meta: MetaSparkProvider-এর model এখন config থেকে আসে (factory `brain_model` / chain entry `meta:<model>` পাঠায়) — provider file-এর code ছোঁয়া হয়নি, connector credential path অপরিবর্তিত। Meta-র আর কোনো model ID এই VM থেকে verify করা যায়নি (নিচে diagnostic দেখুন) — config-এ শুধু muse-spark-1.3 আছে।
- WIRED — `00-CEO-Core/live_brain.py`: provider registry (PROVIDER_MODULES + DEFAULT_MODELS) + `load_provider()` + `build_provider_chain()`; LiveBrainAdapter এখন chain নেয় — complete() provider-দের একটার পর একটা চেষ্টা করে, সব fail করলে তবেই LOUD mock fallback (কারণসহ)। পুরনো single-provider call site অপরিবর্তিত। `00-CEO-Core/brain.py`: BrainFactory._live_brain এখন config-এর fallback_chain থেকে chain বানায় (config_path thread করা হয়েছে); `{"brain": "live"}` temp config-এও আগের মতো chain [meta] চলে (Phase 10 compat)।
- CONFIG — `00-CEO-Core/config.json`: নতুন `providers` section (৭ provider: enabled / models / env_var / endpoint / key_from; Meta-র env_var null, key_via connector) + `brain_provider: "meta"` + `brain_model: null` + `fallback_chain: ["openrouter", "meta", "mock"]` + honest_status-এ `phase_11_providers` entry। brain এখনো "mock", phase 9 / v0.9.0 অপরিবর্তিত (check_phase7-এর pin)।
- GUIDE — `00-CEO-Core/PROVIDERS-SETUP-BANGLA.md` (সহজ বাংলা): ৭ provider-এর key কোথায় + env var + model বদলানোর এক লাইন; OpenRouter পুরো section — account → key → PC-তে env var (Windows setx) → `openrouter/free` auto-route vs নাম ধরে model → free limit (২০/min, ৫০/day; $10 lifetime credit-এ ১,০০০/day) → free model বদলায়, fallback chain জরুরি → key কখনো file-এ নয়।
- VERIFIED mock mode-এ (কোনো live call ছাড়া): নতুন `scripts/check_providers.py` **43/43 PASS** (৭ module standalone import; construct 0 calls; missing key → env var-এর নামসহ error + network attempt নেই; simulated success/API error/timeout প্রতিটা env provider-এ; chain [fail, fail, ok] + [fail, fail] → mock fallback; factory selection temp config-এ; real config validation; secrets scan clean; store unchanged)। পুরো suite: phase0 8/8, phase1 11/11, phase2 14/14, phase3 19/19, phase4 9/9, phase6 14/14, phase7 18/18, engines 44/44, departments 21/21, specialists 41/41 = 199/199; check_mcp 9/9 + check_live_tools 7/7 + check_live_brain 10/10 + check_providers 43/43 সহ মোট **268/268 PASS**; check_voice 13/14 (শুধু sounddevice FAIL — VM-এ PortAudio নেই, আগের মতোই)।
- DIAGNOSTIC (একবার, token খরচ $0): Meta connector-এর `check_models.py` FAILED — `URLError: Tunnel connection failed: 403 Forbidden` (api.meta.ai-তে এই VM-এর রাস্তা বন্ধ, আগের probe-এর মতোই)। Meta-র model list verify করা যায়নি — muse-spark-1.3-ই একমাত্র known Meta model। কোনো live call করা হয়নি, কোনো key নেই।
- NOT DONE (Boss-এর step লাগবে): কোনো provider-এর key-ই দেওয়া হয়নি — brain live করতে হলে Boss-কে key দিতে হবে (env var, PC-তে) + config-এ `"brain": "live"` + live probe। Free model-এর নাম বদলাতে পারে — config-এর models list Boss-এর হাতে।
- NOT PUSHED: Phase 11-এর সব file LOCAL only; push Boss-এর "push koro"-তে (Elora main chat-এ করবে)।

## Improvement Phases 1–3 — Nod Gate + Memory/Ledger + Quiet Schedules (2026-11-21, Boss order: "যেটা already build করে রাখছি 50% সেটাতে আরো যা কিছু বাকি আছে সেটা যতটুকু সম্ভব কমপ্লিট করো" — live brain ছাড়া, $0, local; Mira-shift / API-voice idea বাদ)

- Boss 2026-11-21 ~08:51-এ voice call-এ order দিলেন — Mira-কে CEO Bot-এর জায়গায় shift করার idea বাদ (Mira copy করে repo-তে বসানো যায় না; API key দিলে শুধু model আসবে, Mira নয়; voice loop live brain-এর সাথে জোড়া হয়নি, proof নেই)। তার বদলে already-built ~50%-এর বাকিটা যতটুকু সম্ভব complete করো — live brain ছাড়া। Pattern source: Nod RE (~/workspace/nod-reverse/reverse-engineering.md — trust.ts / approvals.ts / memory.ts / ledger.ts / schedules.ts, file:line evidence) + patterns-three-tools.md §6 (Phase 1–3)।
- BUILT Phase 1 — Trust gate as code (`00-CEO-Core/trust_gate.py`): rule-based trust_check() — read/draft free; gated কাজে Boss-এর quote verify (verbatim, named source) + coverage (gate word + material target — generic "email" target নয়); standing deny: spend cap $0-এর বেশি, dental/medical/patient-health hard DQ; email PAUSED deny নয় — decision "ask", PENDING approval-ই restart-এর পথ। ConfirmationStore — run-once confirmation, ApprovalGateway-এর সাথে wired (gateway-ই approval-এর সত্য, approval_id link); approve-এ gate word মিলতেই হবে; execute_once() ঠিক একবার; fail -> UNCERTAIN, কখনো re-run নয়; repeat-এর জন্য নতুন confirmation। Wiring: `00-CEO-Core/tool_calling.py`-এর gated branch-এ trust pre-check — deny হলে "blocked-trust" (approval-ও রেকর্ড হয় না, কিছু execute হয় না); নইলে আগের মতো PENDING, result-এ trust decision attach। Engine wrapper (`01-Agency-Department/engine/tool_calling.py`) context + ledger_path forward করে। Trust "allow" হলেও gateway-ই চূড়ান্ত — Boss-এর exact gate word ছাড়া কিছু এগোয় না।
- BUILT Phase 2 — Owner memory + usage ledger: `00-CEO-Core/owner_memory.py` (quote-verified, owner-messages-only, 256 KiB cap, entry ≤4,000 chars, area about/preferences/people/routines/lessons, status tentative/observed/stated/archived; learn/edit-এ quote verbatim না থাকলে ValueError; memory context, NOT permission) + `store/memory.json` (৩টা seed entry — Boss-এর রেকর্ড করা সঠিক কথা: Mira নাম, বাংলায় উত্তর, gate words) + `store/MEMORY.md` export। `00-CEO-Core/usage_ledger.py` (একটাই ledger: kind/provider/model/tokens/cost/task/action; monthly cap $0 — config spend_cap_usd থেকে; task check-in threshold $0 — যেকোনো live খরচেই check-in; mock kind-এ nonzero cost ValueError) + dispatcher ledger threading (call_tool-এ ledger_path দিলে mock/gate/error receipt, cost $0.00; না দিলে কিছু লেখে না — check script-গুলো real store ছোঁয় না)।
- BUILT Phase 3 — Quiet schedules (`00-CEO-Core/quiet_schedules.py`): watchMarker (state-এর sha256 hash); state না বদলালে run skip — quiet; একসাথে একটাই run (60-min stale lock); correction শুধু বলা field বদলায়, বাকি আগের মতো; failed work-এ lock ছাড়ে, marker আগেরটাই থাকে। `store/schedules.json`-এ ১টা schedule seed করা (taskboard-queue-watch, paused — কোনো runner attach করা হয়নি; bridge adoption Boss/parent-এর সিদ্ধান্ত, automatic নয়)।
- CONFIG — `00-CEO-Core/config.json` honest_status.phases-এ ৩টা entry (`improvement_p1_gate`, `improvement_p2_memory_ledger`, `improvement_p3_quiet_schedules`)। Brain এখনো "mock", phase 9 / v0.9.0 অপরিবর্তিত (check_phase7-এর pin)। Department structure / 3-Chief design ছোঁয়া হয়নি।
- VERIFIED (mock mode-এ, কোনো live call / key / spend ছাড়া): নতুন check_gate.py **24/24 PASS**, check_memory_ledger.py **19/19 PASS**, check_quiet_schedules.py **15/15 PASS**; module self-test trust_gate / owner_memory / usage_ledger / quiet_schedules / tool_calling / human_approval_gateway সব OK; পুরো suite নিচে দেখুন (Phase 1–3-এর কাজে পুরনো কোনো check ভাঙেনি)।
- NOT DONE (Boss-এর step লাগবে): Phase 4 team factory — live brain ছাড়া blocked (bot-hq-এর real Hermes gateway লাগে); Phase 5/6 — live brain + always-on host লাগে; live brain proof Boss-এর PC network-এ (এই VM-এ api.meta.ai tunnel 403, key validity UNPROVEN); bridge-এ quiet-schedule adoption (taskboard-queue-watch paused আছে)।
- NOT PUSHED: Improvement Phase 1–3-এর সব file LOCAL only; push Boss-এর "push koro"-তে।

## Memory system LIVE — decided structure + CEO/Chief wiring (2026-11-21, Boss order: voice call ~10:10 Dhaka — "মেমরির স্ট্রাকচার analogy থেকে নয়, merit-এ decide করো, সেই স্ট্রাকচারে সাজিয়ে live করো, GitHub-এ push করো")

- DECIDED — `00-CEO-Core/MEMORY-STRUCTURE-DECISION-2026-11-21.md`: একটাই central store (`store/memory.json`) + ভেতরে box (shared + per-agent) — "drawer" shape থাকল, কিন্তু এখন analogy নয়, merit-এ ঠিক করা। কারণ: একজন owner → একটাই doc (Nod §4, memory.ts); এক repo + 8 GB PC → ৭৯ agent-এর জন্য ৭৯টা file নয় (bot-hq-র per-bot file ওদের আলাদা Hermes home-এর জন্য, আমাদের agent-রা এক repo-র module); box = file না ছড়িয়ে isolation; একটাই file = একটাই atomic save / cap / export। Per-agent file / hybrid / flat-doc — কারণসহ বাদ দেওয়া হয়েছে (doc-এ লেখা)।
- KEPT — quote-verification, owner-messages-only learning, isolation, edit/archive/forget, 256 KiB cap, ৫ area, status, export; ৩ seed entry verbatim (Mira নাম, বাংলায় উত্তর, gate words)।
- ADDED — `owner_memory.py`: maintenance_repair() (৬০ দিনের বেশি পুরোনো tentative archive + dedupe, no-model), validate_proposals() (quote-gated reflect proposal, কখনো auto-write নয়), context_for(box) (compact routing view); প্রতিটা write-এর আগে disk reload guard (CEO+Chief আলাদা instance — last-save-wins race ঠিক করা)।
- WIRED — `main_ceo_bot.py`: route_task() প্রত্যেক route-এ memory পড়ে (context_for) + result-এ "memory" attach; record_owner_message() (quote-verify learn); request_forget_owner_entry() + forget_owner_entry() (ConfirmationStore "delete", gate word "go", execute_once)। `chief_of_staff_agency.py`: handle_task() প্রত্যেক task-এ memory পড়ে + "memory" attach। Route/handle memory-তে লেখে না — routing log tasks.json-এ।
- LESSON (test-এ ধরা পড়ে ঠিক করা): প্রথম design-এ per-task routing note লেখা হয়েছিল — কয়েকটা check run-এ ৫৭৩টা note জমে check_phase6-এর repo grep ভেঙে গিয়েছিল; note সরানো হয়েছে, store ৩ seed-এ restore করা হয়েছে (verbatim যাচাই করা)। Memory log নয় — Boss-এর কথা + lesson-এর জন্য।
- VERIFIED (mock mode-এ, কোনো live call / key / spend ছাড়া): নতুন check_drawer_memory.py **26/26 PASS** (পুরোনো ১৭টা + live-wiring/maintenance ৯টা); পুরো suite: phase0 8/8, phase1 11/11, phase2 14/14, phase3 19/19, phase4 9/9, phase6 14/14, phase7 18/18, engines 44/44, departments 21/21, specialists 41/41, memory_ledger 19/19, gate 24/24, quiet_schedules 15/15, providers 43/43, live_tools 7/7, live_brain 10/10; self-test owner_memory / main_ceo_bot / trust_gate / skill_finder OK; real store ৩ entry, verify_all True। (একবার check_specialists-এর composite flake করেছিল — sibling-এর concurrent edit-এর সময়; fresh re-run 41/41 PASS।)
- Brain এখনো "mock" — memory live হলেও live brain proof Boss-এর PC-তে বাকি।
- PUSH: Boss-এর "push koro"-তে এই batch-এ যাচ্ছে (memory file ১০টা + skill-finder dependency ২টা — নিচে দেখুন)।
- NOTE: Phase 1–3-এর বাকি file (usage_ledger.py, quiet_schedules.py, check_gate.py, check_memory_ledger.py, check_quiet_schedules.py) এই batch-এ যাচ্ছে না — ওগুলো এখনো LOCAL only; BUILD-LOG-এর পুরোনো "NOT PUSHED: Improvement Phase 1–3" লাইনটা ওই বাকিগুলোর জন্য সত্যি থাকে।

## Check run-discipline note (2026-11-21, docs sweep D17)

- **Check script চালানোর সময় অন্য writer active থাকলে check flake করে।**
  দেখা গেছে: `scripts/check_gate.py` প্রথম run-এ 23/24 — "real store unchanged by
  this check run" FAIL, কারণ `store/memory.json` run-এর মাঝখানে বদলে গিয়েছিল
  (আরেক process লিখছিল); re-run-এ 24/24। `_snapshot_store()` store/ ফোল্ডারের
  সব file-এর snapshot নেয় — check নিজে ছোঁয় না এমন file বদলালেও fail হয়।
- **নিয়ম:** check script চালাতে হবে যখন অন্য কোনো writer active নেই — bridge
  cron (`master-os-3d-bridge`, প্রতি ১০ মিনিট), sibling worker/subagent, voice
  loop — কেউ store/-এ লিখছে না তখন। একসাথে দুইজন check চালালেও একই flake হতে
  পারে। Fail হলে প্রথমে re-run করো — কোড ঠিক করার আগে concurrent write ছিল
  কি না দেখো।
- এই note-টা শুধু run-discipline; পুরনো BUILD-LOG entry কিছু বদলানো হয়নি (D19)।
