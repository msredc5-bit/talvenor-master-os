# Skill: Kit QA (NEW)

**Role (ভূমিকা):** Vet No-Show Recovery Kit-এর ৬ অংশের QA checklist DRAFT লেখা — কোনো অংশ বানানো হয়েছে কি না, হলে কী যাচাই করতে হবে।
**Agent:** `sections/product/agents/kit_qa.py` — `KitQAAgent` (task kind `kit_qa`, section `product`)
**Status: NOTHING TO QA YET** — kit-এর ৬ অংশের কোনোটা বানানো হয়নি (0/6)। Agent ফেরত দেয়: "NOT BUILT — nothing to QA yet" + প্রতিটা অংশের QA checklist DRAFT।

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (প্রথম ৩০ buyer-এর জন্য launch price **$39**)। Format: Google Sheets + Google Docs + copy-paste script।
- **কার জন্য:** Independent companion-animal vet clinic, ১–৫ vet। Corporate chain নয়, solo mobile vet নয়।
- **Kit-এর ৬ অংশ (kit-outline.md থেকে):** (1) Reminder Cadence Pack — T-72h / T-24h / T-2h SMS + email + call script; (2) Same-Day Rebooking Scripts — phone + in-person; (3) Waitlist-Fill SOP — এক পাতা; (4) No-Show Log + $ Tracker — Sheets, formula সহ; (5) Deposit / No-Show Policy Template — attorney-review note সহ; (6) Front-Desk Quick Card — ৫ লাইন, এক পাতা।

## Inputs

- `02-Digital-Product-Department/kit-outline.md` — blueprint (একমাত্র উৎস, read-only); ৬ অংশের বিবরণ এখান থেকে।
- Gate 1 যাচাই: cadence + script AAHA/PetDesk guidance-এর সাথে মেলে কি না (build-এর পরে)।
- Gate 0 status: `gate0-status.md` — এখন NOT PASSED, তাই QA করার মতো কিছু নেই।

## Step-by-step method (checklist DRAFT — build-এর পরে ব্যবহার হবে)

### প্রতিটা অংশের QA checks
1. **Reminder Cadence Pack** — T-72h / T-24h / T-2h তিনটে touch আছে কি না; [NAME] / [PET] / [TIME] field আছে কি না; Gate 1: cadence + script AAHA/PetDesk guidance-এর সাথে মেলে কি না।
2. **Same-Day Rebooking Scripts** — phone + in-person script দুটোই plain US English কি না; slot সেদিনই ভরার কথা আছে কি না।
3. **Waitlist-Fill SOP** — এক পাতা কি না; কাকে আগে ফোন করবে + কোন order-এ + exact call script আছে কি না।
4. **No-Show Log + $ Tracker** — formula auto-total করে কি না (sample সংখ্যা দিয়ে test); মাসের miss / আনুমানিক $ loss / recovery rate তিনটে দেখায় কি না।
5. **Deposit / No-Show Policy Template** — "have your own attorney review before using" লেখা আছে কি না; legal advice হিসেবে দেওয়া হয়নি তো।
6. **Front-Desk Quick Card** — ৫ লাইন কি না; এক পাতা কি না; desk-এ রাখার মতো কি না।

### Global checks (সব অংশে)
- "Talvenor" বানান সব জায়গায় ঠিক কি না।
- কোনো invented client / testimonial / statistic নেই তো।
- PIMS replace করার দাবি নেই তো — kit PIMS-এর পাশে কাজ করে (76.5% practice ইতিমধ্যে PIMS ব্যবহার করে — AVMA 2025)।
- $49-এর verified sale আছে বলে দাবি নেই তো।
- কোনো clinic-কে দুইবার মেইল করার plan নেই তো।

## Output format

- মাথায়: "NOT BUILT — nothing to QA yet" (এখন)।
- তারপর per-part checklist DRAFT: প্রতিটা অংশ — status NOT BUILT + checks।
- শেষে verdict: কোনো অংশ QA পাস করেনি — কিছু বানানোই হয়নি। Checklist DRAFT only।
- Output-এ status সত্য লেখা থাকবে — কখনো বানানো "PASS" নয়।

## Tools used (টুল)

- Read-only file read: `kit-outline.md` (৬ অংশের বিবরণ)।
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — checklist DRAFT লেখায়, live call নয়।
- Gated কাজে ApprovalGateway (PENDING record)।
- কোনো live tool, network, বা file write নয়।

## Gate

- QA ফলাফল ব্যবহার করতে Boss-এর `ok` লাগে।
- Gate 0 পাস + build-এর পরেই আসল QA হবে; এখন শুধু checklist DRAFT।

## Honest limits

- **0/6 built** — QA করার মতো কিছু নেই। এই skill-এর আসল test এখনো হয়নি।
- Gate 1 (cadence AAHA/PetDesk যাচাই) এখনো হয়নি।
- $49 price unproven — কোনো verified sale নেই।

## যা কখনো করে না

- কোনো অংশ pass বলে দাবি করে না (কিছু বানানোই হয়নি)।
- Kit বানায় না; কোনো file লেখে না; client/testimonial/statistic বানায় না।
- Policy template-কে legal advice হিসেবে দেয় না।

## Worked example (আসল repo fact দিয়ে)

- **Task:** `{"type": "kit_qa", "title": "QA the 6 kit parts"}` → `KitQAAgent.run()`।
- **Agent করে:** `kit-outline.md` পড়ে ৬ অংশের নাম নেয়; কোনো অংশ built নয় বলে প্রতিটার status লেখে NOT BUILT।
- **ফলাফল:** status `draft-ready`; output-এ "NOT BUILT — nothing to QA yet" + ৬ অংশের checklist DRAFT (যেমন Reminder Cadence Pack-এর Gate 1 check: AAHA/PetDesk guidance-এর সাথে মিল; No-Show Log + $ Tracker-এর formula sample test)। কোনো অংশ pass নয় — verdict সত্য লেখা।
