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
