# মেমরি সিস্টেম — স্ট্রাকচার সিদ্ধান্ত (2026-11-21)

> **Boss-এর rule (voice call 2026-11-21 ~10:10 Dhaka):** ড্রয়ার layout ছিল
> Mira-র সাজানো, Boss-এর analogy থেকে। মেমরির স্ট্রাকচার analogy থেকে নয়,
> **merit-এ decide** করতে হবে, তারপর সেই স্ট্রাকচারে মেমরি সিস্টেম সাজিয়ে
> **live** করতে হবে (wired + GitHub push)। এই file-ই সেই সিদ্ধান্ত।

## সিদ্ধান্ত (এক লাইনে)

**একটাই central store file (`store/memory.json`) — ভেতরে আলাদা box
(shared + প্রত্যেক agent-এর নিজের box)।** অর্থাৎ "drawer" shape-টাই থাকল,
কিন্তু এখন এটা analogy নয় — নিচের merit-এ ঠিক করা structure।

## কেন এই structure — merit-এ বিচার

তিনটে option ছিল। প্রতিটা Nod আর bot-hq-র RE থেকে যাচাই করা হয়েছে
(নিচে source সহ)।

### Option A — একটাই central store + ভেতরে box (এটাই নেওয়া হলো)

- **একজন owner → একটাই memory doc।** Nod-এর lesson
  (`~/workspace/nod-reverse/reverse-engineering.md` §4, `memory.ts`):
  এক owner-এর memory একটাই private JSON doc (256 KiB cap, ৫টা area)।
  Boss একজন — তাঁর কথা এক জায়গায় থাকবে, duplicate হবে না। Duplicate
  হলে একদিন পুরোনো/ভুল copy-ই "সত্য" হয়ে যায়।
- **একটাই repo, একটাই PC (8 GB) → ৭৯টা file নয়।** bot-hq-র per-bot
  file (`~/workspace/bot-hq-reverse/reverse-engineering.md` §5,
  `engine-memory.ts`) ওদের আলাদা Hermes home-এর জন্য — প্রত্যেক bot
  আসলেই আলাদা machine slice। আমাদের agent-রা আলাদা home নয়, এক
  repo-র module। ৭৯ agent-এর জন্য ৭৯টা memory file মানে ছড়ানো সত্য,
  কোনো single source নেই — আর Boss-এর shared কথা প্রতিটা file-এ
  copy করতে হতো, নইলে cross-file খোঁজা লাগত (যেটা আসলে Option A-ই
  আবার বানানো, খারাপভাবে)।
- **Box = file ছড়ানো ছাড়াই per-agent isolation।** Shared compartment-এ
  শুধু Boss-এর কথা (সবাই পড়ে, কেউ আটকাতে পারে না); প্রত্যেক agent-এর
  কাজের note শুধু তার নিজের box-এ (অন্য box পড়তে পারে না — code-এ
  enforce করা)। Boss-এর শর্ত (2026-11-21 ~09:45) — per-agent note যাতে
  না মেশে — এভাবেই মেটে, file না বাড়িয়ে।
- **একটাই file = একটাই atomic save, একটাই cap, একটাই backup/export।**
  256 KiB cap, একটাই `store/MEMORY.md` export — Boss এক file-এ সব
  দেখতে পারেন।

### Option B — Per-agent file (bot-hq style) — নেওয়া হয়নি

প্রত্যেক agent-এর নিজের `MEMORY.md`/`USER.md`, `§`-separated entry।
ভালো দিক: agent-এর note আলাদা file-এ দেখা যায়, delete করা সহজ।
কিন্তু এই repo-তে: agent-রা আলাদা home নয়; shared Boss-কথা duplicate
বা cross-ref ছাড়া চলে না; ৭৯টা file-এর consistency (কোনটা latest?)
code-এ আলাদা করে বানাতে হতো। bot-hq-তেই ওদের `memories` SQLite table
legacy/unused হয়ে পড়ে আছে — দুটো source মানেই একটা মরে যায়।

### Option C — Hybrid (shared central + note per-agent file) — নেওয়া হয়নি

Owner-কথা central, কাজের note per-agent file। দেখতে সুন্দর, কিন্তু
isolation দুটো mechanism-এ ভাগ হয় (shared-এ code, note-এ filesystem),
note-র lifecycle (edit/archive/forget) দুটো code path লাগে, আর export-ও
দুটো source মেলাতে হয়। Single-file design-এ `read_box()`/`list_own()` +
box-wise export-ই একই view দেয় — complexity-র বদলে কোনো merit নেই।

### Option D — Flat doc, box ছাড়া (Nod-এর original) — নেওয়া হয়নি

একটাই doc, ৫টা area, কোনো per-agent split নেই। সহজ, কিন্তু Boss-এর
শর্ত মানে না — worker-এর note আর Boss-এর কথা এক list-এ মিশে যায়,
শুধু area/slug-এ আলাদা। Box code আগেই আছে, 17/17 pass — D-তে ফেরার
কোনো লাভ নেই।

## যা আগের মতোই থাকল (ভালো জিনিস)

- **Quote-verification:** memory শুধু Boss-এর নিজের message থেকে শেখে;
  quote source message-এ verbatim না থাকলে entry হয় না (Nod §4)।
- **Memory context, NOT permission:** memory-তে লেখা থাকলেই কোনো কাজের
  অনুমোদন হয় না — অনুমোদন শুধু trust_gate + ApprovalGateway-এ।
- **Isolation:** shared-এ শুধু Boss-এর কথা; কাজের note শুধু নিজের box-এ;
  ভুল box থেকে read/edit/forget বারণ।
- **Visible + editable:** দেখা / বদলানো / archive / ভুলে যাওয়া (forget);
  Markdown export (`store/MEMORY.md`)।
- **Cap:** 256 KiB doc, entry ≤ 4,000 chars, ৫ area
  (about / preferences / people / routines / lessons), status
  tentative / observed / stated / archived।
- **৩টা seed entry verbatim অপরিবর্তিত:** Mira নাম, বাংলায় উত্তর,
  gate words (`store/memory.json`)।

## যা নতুন যোগ হলো (merit review-তে পাওয়া gap)

1. **Maintenance — repair (no-model, Nod-এর repair-এর আদলে):**
   `OwnerMemory.maintenance_repair()` — ৬০ দিনের বেশি পুরোনো
   tentative entry (একবার বলা, আর repeat হয়নি) archive করে; একই
   (box, area, slug)-এর duplicate থাকলে পরেরটা archive করে।
   কোনো model লাগে না, কোনো live call নেই। Stated/observed entry
   কখনো auto-archive হয় না (ওগুলো confirmed/learned)।
2. **Reflect — শুধু proposal, কখনো auto-write নয়:**
   `OwnerMemory.validate_proposals()` — candidate list নিয়ে কোনটা
   quote-verify পাস করে (শেখার জন্য ready) আর কোনটা reject — ফেরত
   দেয়, কিছু লেখে না। Proposal লেখে ভবিষ্যৎ live brain / Mira;
   server শুধু quote-verify করা note-ই নেয় (Nod: "server keeps a
   note only if a cited owner message contains its quote verbatim")।
3. **Compact context view:** `OwnerMemory.context_for(box)` — CEO/Chief
   routing-এ যা attach করে: shared entry + নিজের box-এর note, ছোট
   আকারে (source_message ছাড়া)।
4. **Gate-দিয়ে forget (Nod: ভুলে যাওয়া trust check চায়):**
   `Main CEO Bot`-এ `request_forget_owner_entry()` — ConfirmationStore-এ
   "delete" confirmation বানায় (gate word "go"); `forget_owner_entry()`
   শুধু approved confirmation-ই `execute_once()` দিয়ে চালায় — approve
   ছাড়া মোছা যায় না, fail হলে UNCERTAIN, কখনো re-run নয়।
5. **Reload guard (multi-instance safety):** প্রতিটা write
   (learn/note/edit/forget/repair) আগে disk থেকে fresh পড়ে — CEO আর
   Chief একই file-এর আলাদা instance ধরলেও একজনের save অন্যজনের
   note মুছে দেয় না।

## Live wiring (এটাই "live" হওয়ার মানে)

- **Read path — সবসময়:** `Main CEO Bot.route_task()` প্রত্যেক route-এ
  memory পড়ে (`context_for("main_ceo_bot")`) আর result-এ `memory`
  হিসেবে attach করে — routing সিদ্ধান্ত Boss-এর কথা (নাম, ভাষা, gate
  words) দেখেই হয়। Agency Chief-ও `handle_task()`-এ একইভাবে
  `context_for("chief_of_staff_agency")` পড়ে।
- **Write path — Owner-কথা:** `Main CEO Bot.record_owner_message()` —
  Boss-এর নতুন কথা quote-verify করে শেখায় (learn)। Boss-এর কথা ছাড়া
  কেউ শেখাতে পারে না। এই write path-টা live flow-র entry point থেকে
  ডাকা হয় (Mira/chat layer Boss-এর কথা পেলে) — task text থেকে
  auto-learn করা হয় না (task text Boss-এর verbatim message নয়)।
- **Write path — কাজের note:** `note_work()` explicit call-এ চলে
  (lesson শেখা হলে) — route/handle থেকে auto-call করা হয় না।
  Routing-এর log `store/tasks.json`-এ থাকে; memory Boss-এর কথা +
  lesson-এর জন্য। প্রথম design-এ per-task routing note লেখা হয়েছিল —
  test-এ কয়েকটা check run-এ ৫৭৩টা note জমে `check_phase6`-এর repo
  grep ভেঙে গিয়েছিল, তাই সরানো হয়েছে (2026-11-21 ~10:24, এই ভুল
  থেকে শেখা: memory log নয়)।
- **Write path — ভুলে যাওয়া:** শুধু gate-এর অনুমোদনে (উপরে ৪ নম্বর)।
- Brain এখনো **mock**, $0, কোনো key / live call নেই। Memory local
  file read/write — API key লাগে না।

## File-গুলো

- `00-CEO-Core/owner_memory.py` — memory code (maintenance + context
  + proposal validation + reload guard যোগ; আগের API অপরিবর্তিত)।
  Reload guard: CEO আর Chief একই file-এর আলাদা instance ধরে — তাই
  প্রতিটা write-এর আগে disk থেকে fresh পড়া হয়; নইলে শেষ save আগের
  note মুছে দিত।
- `00-CEO-Core/check_drawer_memory.py` — check script (পুরোনো ১৭টা +
  নতুন live-wiring/maintenance check; সব pass)।
- `00-CEO-Core/main_ceo_bot.py` — CEO wiring (read + write + gated
  forget)।
- `01-Agency-Department/chief_of_staff_agency.py` — Chief wiring
  (read only — প্রত্যেক handle-এ context attach)।
- `store/memory.json` — ৩ seed entry, verbatim (এই change-এ file
  বদলায়নি — শুধু push হচ্ছে)।
- `store/MEMORY.md` — export, seed থেকে regenerate করা।

## যা এখনো বাকি (Boss-এর সিদ্ধান্ত লাগবে)

- Live brain proof (Boss-এর PC network) — Phase 4 team factory-র
  আগে। Memory live হলেও brain এখনো mock।
- Reflect-এর proposer (live brain / Mira থেকে candidate আসা) — এখন
  শুধু validator আছে, proposer নয়।
