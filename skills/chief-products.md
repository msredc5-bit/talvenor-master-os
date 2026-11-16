# Skill: Chief of Staff — Digital Product

**Role:** Vet No-Show Recovery Kit ($49 one-time)-এর Chief — list করা,
kit blueprint রাখা, launch-এর checklist draft করা, Gate 0 দেখা।
**Status: REAL (Phase 2)** — Chief module আসল কাজ করে, কিন্তু kit
বানানো/বেচা/launch Gate 0-তে আটকে আছে।

## Inputs

- Main CEO Bot থেকে routed task
- Gate 0 ফলাফল — `02-Digital-Product-Department/gate0-status.md`
  (একমাত্র উৎস; "Status: PASSED" না থাকলে NOT PASSED)
- Kit blueprint — `02-Digital-Product-Department/kit-outline.md`
- PA vet list — `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv`
- Research report — `~/workspace/research_notes/digital-product-final-20261112/report.md`

## Outputs

- Kit blueprint (নকশা) — kit নিজে নয়
- PA list সারাংশ — যাচাই করা row শুধু
- Launch checklist DRAFT — launch নয়
- Gate 0 status — gate0-status.md থেকে পড়া
- Sale / reply report — শুধু আসল সংখ্যা (এখন sale 0)

## Routing table (task type → কাজ → gate)

| Task type | কাজ | Gate |
|---|---|---|
| `kit_build` | Blueprint ফেরত (kit-outline.md) — kit বানানো নয় | `ok` |
| `clinic_research` | PA list সারাংশ (row সংখ্যা, শহর) | — |
| `gate0_check` | Gate 0-র সত্য অবস্থা | — |
| `launch_prep` | Launch checklist DRAFT — launch নয় | `go` |

## Gate — এখানেই থামে

- **Gate 0 পাস না হওয়া পর্যন্ত kit launched/sold চিহ্নিত করা যাবে
  না** — `mark_launched` / `mark_sold` চাইলে status `blocked-gate0`।
- Email পাঠাতে `send` লাগে — এই Chief কখনো মেইল পাঠায় না।
- Price $49 (launch $39 প্রথম ৩০ buyer) — public-এ quote করার আগে
  Boss confirm করবেন।
- Dental/medical (patient-health) কখনো target নয় — এটা animal care।

## Tools (REUSED / rail)

- Lemon Squeezy (Gate 0 পাস হলে) — backup: Polar, তারপর Gumroad
  (individual)। Etsy বন্ধ — plan-এ নেই।
- Google Sheets / Docs (kit — Gate 0-র পরে বানানো হবে)।
- PA list — 39/100 (2026-11-16, যাচাই করা)।

## সত্য অবস্থা (Phase 2, 2026-11-16)

- Gate 0 **NOT PASSED** — Lemon Squeezy test Boss-এর step।
- Kit-এর ৬ অংশ বানানো হয়নি — শুধু blueprint আছে।
- PA list 39/100 — বাকি 61 Gate 0-র পরে।
- Sale 0। $10K/mo verdict: kit একা দেবে না (৬–১২ মাসে $300–$1,000/mo
  credible); wedge (১/২০ buyer → receptionist) UNTESTED।
