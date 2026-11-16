# Vet No-Show Recovery Kit — BLUEPRINT (নকশা, kit নিজে নয়)

**Price:** $49 one-time (প্রথম ৩০ buyer-এর জন্য launch price $39, তারপর $49)।
**Format:** Google Sheets + Google Docs + copy-paste script। কোড নেই, app
নেই, install করতে হয় না। Lemon Squeezy থেকে download link-এ দেওয়া হবে
(Gumroad backup listing)।
**কার জন্য:** Independent companion-animal vet clinic, ১–৫ vet, buyer =
front-desk / practice manager। Corporate chain নয় (ওদের central system
আছে), solo mobile vet নয় (খুব ছোট)।

> ⚠️ **এটা BLUEPRINT — kit নিজে এখনো বানানো হয়নি।** Gate 0 (Lemon
> Squeezy signup test) পাস না হওয়া পর্যন্ত kit বানানো/বেচা শুরু হবে না।
> এই ফাইলে যা আছে তা research report
> (`~/workspace/research_notes/digital-product-final-20261112/report.md`
> §4.1, §5) থেকে নেওয়া নকশা — কোনো sale, কোনো launch নয়।

## কেন এই kit (গবেষণা থেকে, source সহ)

- No-show rate **~11%** [VERIFIED — AAHA]। গড় vet visit **~$200**
  [VERIFIED — AVMA 2025]। একটা সাধারণ clinic-এর বছরে **~$50k–$150k**
  ঝুঁকিতে থাকে (labeled estimate — ২৫ appointment/day × 11% × 250 দিন)।
- US-এ **34,296** vet practice [VERIFIED — Census 2023]।
- আসল উদাহরণ: PAWS Clinic, 2025-এ 904 no-show, দিনে ৮–৯ খালি slot
  [VERIFIED — clinic Facebook post, 15 Jan 2026]।
- Vet = Talvenor-এর target niche #2 — kit-এর buyer মানেই pre-qualified
  receptionist prospect (wedge — UNTESTED: ২০ জন buyer-এর ১ জন
  $1,109/mo receptionist নিলে ~$11K/mo)।

## Kit-এর ৬ অংশ (সব বানাতে হবে — এখনো কোনোটা বানানো হয়নি)

### ১. Reminder Cadence Pack (Docs + script)
- T-72h / T-24h / T-2h — SMS + email + phone-call script, copy-paste।
- প্রতিটা script-এ [NAME] / [PET] / [TIME] field থাকবে।
- **Gate 1-এ যাচাই করতে হবে:** cadence + script AAHA/PetDesk-এর
  published guidance-এর সাথে মেলে কি না। মিল না হলে ঠিক করতে হবে।

### ২. Same-Day Rebooking Scripts (Docs)
- Client no-show করলে বা late cancel করলে front desk কী বলবে — যাতে
  slot-টা সেদিনই আবার ভরে যায়, হারিয়ে না যায়।
- Phone script + in-person script, দুটোই plain US English।

### ৩. Waitlist-Fill SOP (Docs, এক পাতা)
- Slot খালি হলে কাকে আগে ফোন করবে, কোন order-এ, exact call script সহ।
- এক পাতার procedure — front desk-এ লাগানো যায়।

### ৪. No-Show Log + $ Tracker (Sheets)
- প্রতিটা no-show log করবে; formula auto-total করবে: এই মাসে কত
  appointment miss হলো, আনুমানিক কত $ হারালো, recovery rate কত।
- Sample সংখ্যা দিয়ে formula test করতে হবে (build-এর সময়)।
- **এই $ figure-টাই আসল point:** clinic নিজের চোখে loss-টা দেখবে।

### ৫. Deposit / No-Show Policy Template (Docs)
- Clinic adopt করতে পারে এমন plain-words policy template।
- ⚠️ লেখা থাকবে: **"have your own attorney review before using"** —
  এটা legal advice নয়, Elora কখনো এটাকে legal advice হিসেবে দেবে না।

### ৬. Front-Desk Quick Card (Docs, এক পাতা)
- ৫ লাইন — যেগুলো মানলে বেশিরভাগ no-show ঠেকে। Reception desk-এ
  রাখার মতো এক পাতা।

## Build order (Gate 0-র পরে, ৩–৪ সপ্তাহ, দিনে ১ ঘণ্টা, $0)

| সপ্তাহ | কাজ | শেষ হলে |
|---|---|---|
| Week 0 — Gate 0 | Lemon Squeezy signup test (Boss-এর step) | Store খোলে, নইলে Polar → Gumroad test |
| Week 1 — Validate + list | (a) Cadence AAHA/PetDesk-এর সাথে যাচাই (Gate 1)। (b) PA list 100-এ পূর্ণ করা | 100-clinic list filed; cadence verified |
| Week 2 — Build | ৬ অংশ Sheets/Docs-এ বানানো; $ tracker formula sample-এ test; policy-তে attorney-review note | Kit সম্পূর্ণ; একবার পুরো read-through |
| Week 3 — Store + sales page | Lemon Squeezy listing (primary) + Gumroad (backup); sales page (source সহ $50k–$150k math, tracker-এর ৩ screenshot, FAQ, free sample: ১ reminder-script set) | দুটো listing live; Boss sales page review করবেন |
| Week 4 — Launch | দিনে ২৫ মেইল, 100 clinic-কে (৪ দিন); প্রতিটা reply + sale sheet-এ লেখা | 100 মেইল পাঠানো; reply/sale সংখ্যা জানা |

## Gate (kill criteria — আগে থেকে লেখা, পরে বদলানো যাবে না)

| Gate | কখন | পাস | ফেল → কী হবে |
|---|---|---|---|
| **Gate 0 — rail** | Week 0 | Lemon Squeezy (বা Polar/Gumroad) store খোলে, BD individual + BD bank payout | সব rail বন্ধ → **product track পুরো KILL**, Boss-কে জানানো |
| **Gate 1 — vet accuracy** | Week 1 | Cadence + script AAHA/PetDesk guidance-এর সাথে মেলে | মেলে না → একবার revise; তাও না মিললে **KILL বা re-scope** |
| **Gate 2 — channel** | Week 4–6 (100 মেইল, তারপর 200) | ≥2% reply rate AND 100 মেইলে ≥1 sale | 100 মেইলে **0 reply** → email বন্ধ, vet Facebook group ২ সপ্তাহ; তাও 0 → **KILL**। Reply আছে, 200 মেইলে 0 sale → $29 test একবার; তাও 0 → **KILL** |
| **Gate 3 — traction** | Month 3 | মোট ≥10 sale | <10 sale → **PAUSE** — Boss-এর সাথে price/offer/channel আবার ভাবা |

## সত্য অবস্থা (2026-11-16)

| জিনিস | অবস্থা |
|---|---|
| Gate 0 | **NOT PASSED** — Boss-এর Lemon Squeezy test বাকি |
| Kit-এর ৬ অংশ | কোনোটা বানানো হয়নি — শুধু এই blueprint আছে |
| PA list | **39 / 100** (যাচাই করা) |
| Sale | **0** |
| $10K/mo verdict (সৎ) | kit একা ৬–১২ মাসে $10K/mo দেবে না। Credible: **$300–$1,000/mo** (৬–২০ sale/mo), Gate 2 পাস করলে। $10K/mo-র একমাত্র পথ wedge — UNTESTED। |

## যা করা যাবে না

- Etsy-তে list করা যাবে না (Bangladesh-এর জন্য বন্ধ)।
- Policy template-কে legal advice হিসেবে দেওয়া যাবে না।
- কোনো clinic-কে দুইবার মেইল করা যাবে না।
- $49 price-এর কোনো verified sale আছে বলে দাবি করা যাবে না — price
  inference (পাশের product-এর anchor থেকে), observed traction নয়।
- PIMS (practice-management software) replace করার দাবি করা যাবে না —
  kit PIMS-এর পাশে কাজ করে (script, cadence, waitlist), 76.5% practice
  ইতিমধ্যে PIMS ব্যবহার করে [AVMA 2025]।
