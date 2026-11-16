# Digital Product Engine — README (এক পাতা)

**Department:** 02-Digital-Product-Department — Vet No-Show Recovery Kit
**Chief:** Products Chief of Staff (`chief_of_staff_products.py` — REAL, Phase 2)
**Status: REAL* / BLOCKED** — engine আসল, কিন্তু kit বানানো/বেচা/launch Gate 0-তে আটকে আছে।

## Product (locked facts)

- **Vet No-Show Recovery Kit — $49 one-time** (প্রথম ৩০ buyer-এর জন্য launch
  price $39)। Google Sheets + Docs + copy-paste script। কোড নেই, app নেই।
- **কার জন্য:** Independent US vet clinic (animal care — allowed;
  dental/medical-patient targeting EXCLUDED)।
- **Pain:** no-show ~11% (AAHA) × গড় visit ~$200 (AVMA 2025) ≈ **$50k–$150k/yr**
  ঝুঁকিতে থাকে একটা সাধারণ clinic-এর। US-এ 34,296 practice।
- **Kit-এর ৬ অংশ:** Reminder Cadence Pack (T-72h/T-24h/T-2h), Same-Day
  Rebooking Scripts, Waitlist-Fill SOP, No-Show Log + $ Tracker, Deposit/
  No-Show Policy Template (attorney-review note সহ), Front-Desk Quick Card।

## এই engine-এ কী আছে

| জিনিস | সংখ্যা |
|---|---|
| Staff (`STAFF.md`) | **5 জন** — Kit Builder, Clinic Researcher, Launch Manager, Payment-Rails Checker, Support Drafter |
| Tools (`tools.json`) | **8টি** — mock **6টি** (kit_outline_read, research_notes, draft_email, draft_caption, draft_script, status_read), gated stub **2টি** (launch_kit — publish, sell_kit — spend) |
| Skills (`skills/`) | **5টি** — প্রতিটা staff role-এর জন্য একটা করে .md |
| Wrapper (`tool_calling.py`) | shared core (`00-CEO-Core/tool_calling.py`)-এর উপর thin wrapper — `call()` + `list_tools()` |

## কী আটকে আছে, কার উপর

- **Gate 0 — NOT PASSED।** Lemon Squeezy signup test Boss-এর নিজের ~15-min
  step (lemonsqueezy.com, individual হিসেবে, BD bank payout দেখা যায় কি না)।
  Boss ফলাফল না জানানো পর্যন্ত kit build / sale / launch সব BLOCKED। ফেল
  হলে fallback order: **Polar → Gumroad** (individual)। সব rail বন্ধ হলে
  product track পুরো KILL। **Etsy কখনো plan-এ নেই** (Bangladesh-এর জন্য বন্ধ)।
- **PA vet list 39/100** — বাকি 61 clinic Gate 0-র পরে পূর্ণ করা হবে। কোনো
  clinic-কে মেইল করা হয়নি; email channel PAUSED (2026-11-14 থেকে)।
- **Sale 0।** Wedge (১/২০ kit buyer → $1,109/mo receptionist) **UNTESTED** —
  অনুমান, fact নয়। $10K/mo verdict: kit একা ৬–১২ মাসে দেবে না; credible
  $300–$1,000/mo (৬–২০ sale/mo), Gate 2 পাস করলে।

## নিয়ম (সবসময়)

- Gated কাজ (send / publish / spend / delete) — Boss-এর exact gate word
  (ok / "post it" / "upload it" / send / go) ছাড়া কিছু চলে না। No auto-approve।
- $0 spend cap। কোনো client/testimonial/statistic বানানো হয় না। Brand =
  Talvenor only। কোনো clinic-কে মেইল করা হয় না।
- Source ফাইল: `chief_of_staff_products.py`, `kit-outline.md`,
  `gate0-status.md`, `pa-vet-list/` (README + CSV), `skills/chief-products.md`,
  `00-CEO-Core/config.json`,
  `~/workspace/research_notes/digital-product-final-20261112/report.md`।

## ফাইল

- `STAFF.md` — ৫ staff role
- `tools.json` — ৮ tool registry
- `skills/kit-builder.md`, `skills/clinic-researcher.md`,
  `skills/launch-manager.md`, `skills/payment-rails-checker.md`,
  `skills/support-drafter.md`
- `tool_calling.py` — thin wrapper
- `README.md` — এই ফাইল
