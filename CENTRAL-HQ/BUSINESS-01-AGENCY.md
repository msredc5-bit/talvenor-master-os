# BUSINESS-01 — AI Receptionist Agency OS (Agency Wrapper)

**তারিখ:** 2026-11-19 | **Status:** Wrapper doc — DRAFT, Boss-এর review-এর জন্য
**Source:** Boss-এর পাঠানো brief `~/workspace/briefs/unified-business-os-2026-11-19.md` §2 (as-is সংরক্ষিত, design হিসেবে adopt করা হয়নি — নিচে audit করা হয়েছে)
**Points at:** `01-Agency-Department/` (Master OS repo-র Agency বিভাগ)
**এই ফাইলের নিয়ম:** শুধু wrapper — নতুন code নয়, নতুন worker নয়, কিছু live নয়। যা আছে তার দিকে আঙুল তোলা, যা নেই তা সৎভাবে লেখা।

## Brief-এর audit (যা ভুল ছিল, ঠিক করা হয়েছে)

| Brief-এ যা ছিল | সত্য অবস্থা |
|---|---|
| AI Engineering: Retell | **ভুল।** Retell DROPPED 2026-10-26 — কখনো production নয়। Live voice stack **Vapi** — Sophia, live receptionist, +1 (947) 223-0244, org `1861a735`, GPT-4o-mini, Emma voice, Deepgram nova-3। |
| Agency-র নিজস্ব "Master Brain" | **ভুল।** তিন ব্যবসার আলাদা live brain নেই। **ONE brain: BrainFactory, mock default ($0)**; live MetaSpark UNPROVEN। Agency-র Chief (Agency Chief of Staff) আছেন, আলাদা live brain নয়। |
| Agency-র নিজস্ব Database | **ভুল।** DB = **JSON store files** (`store/tasks.json`, `store/approvals.json`)। কোনো আলাদা database schema নেই। |
| Agency CRM | **PLANNED, live নয়।** CRM = n8n Cloud Data Tables — এখনো live হয়নি। |

## ৮টি Department (Phase 1, 2026-11-19)

Source: `01-Agency-Department/agents/agent-registry/registry.md` (69 entry: brief-এর 62 role + brief-এর বাইরে 7 existing worker) + ৮টি `departments/*/SECTION.md`।

| # | Department | Manager | Mapped existing staff | Status |
|---|---|---|---|---|
| 01 | Sales & Growth | Chief Growth Agent | 8 | EXISTING — manager + staff আছে; Chief wiring Phase 2 |
| 02 | Marketing | Marketing Director Agent | 4 | EXISTING — manager + staff আছে; Chief wiring Phase 2 |
| 03 | AI Engineering | CTO / AI Engineering Agent | 2 | EXISTING — manager + staff আছে; Chief wiring Phase 2 |
| 04 | Client Operations | COO / Client Operations Agent | 5 | EXISTING — manager + staff আছে; Chief wiring Phase 2 |
| 05 | Research & Strategy | Chief Strategy Agent | 0 | **GAP** — manager EXISTING, কিন্তু mapped staff ০; ৭টি role-ই ROLE-ONLY |
| 06 | Finance & Admin | CFO / Finance Agent | 2 | EXISTING — manager + staff আছে; Chief wiring Phase 2 |
| 07 | Quality & Security | Chief Quality & Security Agent | 1 | EXISTING — manager + staff আছে (QAEngineer, dept 03-এর সাথে shared); Chief wiring Phase 2 |
| 08 | Product & Innovation | Chief Innovation Agent | 0 | **GAP** — manager EXISTING, কিন্তু mapped staff ০; ৬টি role-ই ROLE-ONLY |

**গণনা:** মোট 69 entry — EXISTING 22, ROLE-ONLY 43, GAP 4। QAEngineer দুই department-এ গোনা হয়েছে (dept 03 + dept 07, একই worker) — তাই আলাদা worker **21** (15 engine worker + 6 section agent)। ৮ manager-ই EXISTING (`.py` + skill ফাইল disk-এ আছে), কিন্তু **Chief wiring Phase 2** — Agency Chief এখনো কোনো manager-কে ডাকে না; manager-রা standalone, DRAFT-only।

**২টি GAP department:** Research & Strategy (0 staff) এবং Product & Innovation (0 staff) — manager আছে, worker নেই।

## ৫টি Section + ২১ staff (Phase 7)

Source: `00-CEO-Core/config.json` (Phase 7) + registry।

| Section | Section agent (যাচাইকৃত) | Gate |
|---|---|---|
| receive | ClientIntakeReceiver (`client_intake`) | `send` |
| sell | SalesCloser (`sales_close`), FollowUpAgent (`followup_draft`) | `ok` / `send` |
| delivery | ServiceDeliveryManager (`delivery_manage`), ClientSuccessAgent (`client_success`) | `ok` / `send` |
| marketing | Section আছে; section agent ফাইল এই task-এ যাচাই হয়নি | — |
| ops | BillingInvoiceAgent (`billing_invoice`) | `ok` |

এর সাথে engine-এর **15 worker** (`01-Agency-Department/engine/workers/`) — মোট **21 staff** (15 worker + 6 section agent)। সবাই mock brain ($0)-এ চলে, DRAFT-only — কেউ কিছু পাঠায় না, পোস্ট করে না, deploy করে না।

**FollowUpAgent — 100-mail rule: PARKED।** Pennsylvania-তে প্রথম মেইল 37 — কোনো state-এ 100 first mail না হলে সেই state-এ follow-up নয় (Boss-এর 2026-11-10 rule)।

## Agency-র নিজস্ব Assets (brief §2 — সৎ status সহ)

| Asset (brief-এর নাম) | আসল অবস্থা | Status |
|---|---|---|
| Agency CRM | n8n Cloud Data Tables — **PLANNED, live নয়**। CRM ছাড়া CRM manager-এর worker হয় না। | READY NOT LIVE |
| Client Database | Leads-organized filing + `store/` (JSON store files)। আলাদা client database নেই — paying client 0। | BUILT (filing + store) |
| Agent Development Workspace | `01-Agency-Department/engine/workers/` — 15 worker vendored (`~/workspace/boss-ceo/` upstream, আর runtime dependency নয়)। | BUILT |
| Client Delivery Pipeline | `workflows/` — ৫টি workflow ফাইল। n8n workflows **READY, NOT LIVE** — Boss-এর import + test বাকি। | READY NOT LIVE |
| Agency Finance Records | LOCKED pricing (internal only, 2026-11-12) + BillingInvoiceAgent — **invoice শুধু paying client-এর জন্য, Boss-এর কথায়**। Client 0 — এখনো কোনো invoice বানানো হয়নি। | BUILT (template only) |
| Agency Knowledge Base | `engine/skills/` + SOPs (Talvenor office SOPs)। | BUILT |

**Pricing LOCKED, internal only (prospect-কে কখনো quote নয়):** Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build।

**Live voice product:** Vapi — Sophia, live receptionist, +1 (947) 223-0244। Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (Talvenor Demo, 15 min, New York Time)।

## সত্য অবস্থা (Real Status Block — 2026-11-19)

| জিনিস | অবস্থা |
|---|---|
| Email outreach | **PAUSED** — 2026-11-14 থেকে (SPF/DMARC DNS fix Boss-এর কাছে বাকি) |
| প্রথম মেইল | **162** |
| Paying client | **0** |
| Revenue | **$0** |
| Spend cap | **$0** |
| Brain | Mock default ($0); live MetaSpark UNPROVEN |
| GAP department | 2 — Research & Strategy (0 staff), Product & Innovation (0 staff) |
| Chief wiring | **Phase 2 — NOT DONE** এই phase-এ। ৮ manager standalone; Agency Chief এখনো কাউকে ডাকে না |
| Dental/medical | কখনো target নয় — সবসময় DQ |
| Gates | ON — `ok` / `"post it"` / `send` / `go` / `"upload it"`; Boss-এর exact word ছাড়া send/publish/spend/delete কিছু হয় না |

## পরের ধাপ (Boss-এর সিদ্ধান্তে)

1. **Phase 2 — Chief wiring:** ৮ manager-কে Agency Chief-এর সাথে সংযুক্ত করা (Boss-এর "go" লাগবে)।
2. **Email restart:** DNS fix (SPF + DMARC) Boss প্রয়োগ করলে, Boss "check koro" বললে — তারপরই Day 4/Day 5 draft (২৫ + ২৫, READY, unsent) নিয়ে ভাবা।
3. **GAP department:** Research & Strategy এবং Product & Innovation-এ worker বানানো হবে কি না — Boss-এর সিদ্ধান্ত; এখন plan-ও নেই।
4. **প্রথম paying client:** Agency-র একমাত্র আসল লক্ষ্য — client 0 থেকে 1।

## যা এই wrapper করে না

- কোনো worker/manager বানায় না, কোনো wiring করে না।
- কোনো client-কে contact করে না, কোনো মেইল পাঠায় না।
- কোনো দাম prospect-কে জানায় না, কোনো guarantee দেয় না, কোনো invented client/testimonial/stat ব্যবহার করে না।
