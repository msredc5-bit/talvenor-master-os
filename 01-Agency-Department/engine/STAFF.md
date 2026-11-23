# STAFF.md — Agency Engine staff list (Phase 5)

Talvenor AI Receptionist Agency — Boss's first business, MAIN.
The 15 roles in this list = the 15 real ones in `01-Agency-Department/engine/workers/src/workers/` (vendored copy; upstream `~/workspace/boss-ceo/src/workers/`)
workers, not one invented. Names, divisions, gates — taken verbatim from the Chief's ROUTING
(`../chief_of_staff_agency.py`).

True status (2026-11-16): Email PAUSED (since 2026-11-14, DNS fix pending) —
the draft is the final word, not sending. Paying client 0. First mail 163.
Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 · Phone +1 (947) 223-0244.
All workers run on MockLLMProvider (mock brain, $0) — all output is DRAFT.
Live stack Vapi/Sophia — RetellBuilder's output is only a DRAFT build plan.

Gate word meaning: the exact word from Boss needed to send/use the output.
None = the draft itself is safe, no gate.

---

## 1. Prospect Researcher

- **Worker:** `ProspectResearcher` · **Division:** ACQ · **Task type:** `prospect_research` · **Gate:** None
- **What it does:** finds US home-service SMBs (plumbing, HVAC, roofing, garage door, septic, tree, foundation, restoration, pest, vet) — with the owner's name, missed-call pain signal, tech gap, and personalization angle. Never dental/medical/patient-health.
- **Input:** `niche` (default: plumbing), `region` (default: Texas).
- **Output:** research notes for 10 prospects — fields: name, owner, pain_signals, angle.
- **Skill:** `skills/prospect-researcher.md` · **SOP basis:** agency-os SKILL 02-lead-generation + SOP prospect-qualification-talvenor.md.

## 2. Outreach Drafter

- **Worker:** `OutreachDrafter` · **Division:** ACQ · **Task type:** `outreach_draft` · **Gate:** `send`
- **What it does:** writes drafts of cold email / Instagram DM — short, plain US English, hook first, one CTA (short call). Email 20–30/day, IG 5–10/day warm-up. Draft ONLY — sending is Boss's job.
- **Input:** `channel` (email | instagram, default: email).
- **Output:** 5 drafts — if email, from `hello@talvenorai.agency`; if IG, `@talvenor_ai`. No price, guarantee, or invented client.
- **Skill:** `skills/outreach-drafter.md` · **SOP basis:** agency-os SKILL 16-sales-outreach. **Limit:** Email PAUSED — the draft is the final word.

## 3. Reply Triager

- **Worker:** `ReplyHandler` · **Division:** ACQ · **Task type:** `reply_triage` · **Gate:** `send`
- **What it does:** sorts a prospect's reply — interest / question / pricing / demo request / decline. On a decline, a polite exit; the rest are DRAFT reply only — no price quote, offer of a short call, flag Boss with name + platform + message.
- **Input:** `reply_type` (default: interest).
- **Output:** Triage verdict + draft reply (gate `send` on an interest-type reply, gate None on a decline).
- **Skill:** `skills/reply-triager.md` · **SOP basis:** agency-os SKILL 16-sales-outreach (reply rule 2026-10-14).

## 4. Negotiation Coach

- **Worker:** `NegotiationCoach` · **Division:** ACQ · **Task type:** `negotiation_prep` · **Gate:** `ok`
- **What it does:** prepares the Founder for a live sales call — 3 likely questions + strong answers, 2 traps to avoid, and a 60-second opening script (plain US English). Boss takes the call himself — this is only prep.
- **Input:** `prospect` (profile, default: empty), `goal` (default: book the demo call).
- **Output:** Prep pack — 3 Q&A, 2 traps, 60-sec opening script. Anything needing Boss's decision is flagged as a GATE. No price quote.
- **Skill:** `skills/negotiation-coach.md` · **SOP basis:** agency-os SKILL 16-sales-outreach (call prep / objection handling).

## 5. Receptionist Builder

- **Worker:** `RetellBuilder` · **Division:** DEL · **Task type:** `receptionist_build` · **Gate:** `ok`
- **What it does:** writes a **DRAFT build plan** for the client's receptionist — agent prompt, knowledge base, recording script. Live stack Vapi/Sophia (Boss will not pay for Retell) — so this worker never builds live, only the plan.
- **Input:** `business` (default: Apex Plumbing), `trade` (default: plumbing).
- **Output:** DRAFT plan — agent-prompt, knowledge-base, recording-script. In-prompt schedule, emergency flow, callback handling, FAQ, honest AI disclosure, fictional AP- confirmation number, end_call only. No invented pricing.
- **Skill:** `skills/receptionist-builder.md` · **SOP basis:** agency-os SKILL 06-vapi-voice-agent (Vapi layer) + 05-agent-architecture.

## 6. QA Engineer

- **Worker:** `QAEngineer` · **Division:** DEL · **Task type:** `receptionist_qa` · **Gate:** None
- **What it does:** runs a QA checklist of 12 checks before calling the demo receptionist READY — prompt completeness, no broken tool reference, emergency flow, pricing honesty, transfer number real-or-absent, end_call behavior.
- **Input:** `agent` (default: BOSS INPUT REQUIRED).
- **Output:** Checklist + verdict: READY or CHANGES. The verdict is not the final word — delivery needs Boss's ok.
- **Skill:** `skills/qa-engineer.md` · **SOP basis:** agency-os SKILL 18-qa-testing (mandatory gate).

## 7. Onboarding Agent

- **Worker:** `OnboardingAgent` · **Division:** DEL · **Task type:** `onboarding_draft` · **Gate:** `ok`
- **What it does:** writes a draft of the onboarding pack for a new client — business info form, hours/services/price-list request, transfer number confirmation, live-in-7-days terms (3-month minimum, then month-to-month).
- **Input:** `client` (default: new client).
- **Output:** Onboarding pack — info-form, terms, timeline. No invented detail; without the client's real information, "BOSS INPUT REQUIRED".
- **Skill:** `skills/onboarding-agent.md` · **SOP basis:** agency-os SKILL 20-agency-operations (onboarding).

## 8. Content Planner

- **Worker:** `ContentPlanner` · **Division:** MKT · **Task type:** `content_plan` · **Gate:** `ok`
- **What it does:** builds the next week's 5-post plan every Sunday 6 PM (Dhaka) — Facebook / Instagram / LinkedIn, pillars: missed-call pain, AI receptionist demo, founder voice, social proof (without invented clients), CTA. Per post: platform, format, hook, best US-Eastern time.
- **Input:** (no default payload — the week's plan is the input).
- **Output:** 5-post plan. Nothing is built without Boss's "ok".
- **Skill:** `skills/content-planner.md` · **SOP basis:** agency-os SKILL 17-marketing.

## 9. Video Producer

- **Worker:** `VideoProducer` · **Division:** MKT · **Task type:** `video_produce` · **Gate:** `ok`
- **What it does:** builds a Reel package — hook in the first 2 seconds, REAL footage (frame-verified, not stills-motion), US-English voiceover, karaoke caption, Talvenor end card (wave logo, never redrawn), "Illustrative example" on hypotheticals. Format 9:16.
- **Input:** `topic` (default: missed call = lost job).
- **Output:** Reel package (script + shot list + voiceover + caption spec). Publish/upload needs gate `upload it` — this worker never uploads itself.
- **Skill:** `skills/video-producer.md` · **SOP basis:** agency-os SKILL 17-marketing + reel-factory SOP.

## 10. Caption Writer

- **Worker:** `CaptionWriter` · **Division:** MKT · **Task type:** `caption_write` · **Gate:** None
- **What it does:** writes the caption + hashtag + CTA pack for a finished creative — hook in the first line, plain US English, one CTA ("link in bio" only when the real booking link exists). Hashtags: IG 5–8, LinkedIn 3, Facebook 0–2.
- **Input:** `platform` (default: instagram).
- **Output:** Caption pack — caption, hashtags, CTA. No price, no guarantee. Publishing still needs a gate (`post it`) — a caption is not a publish.
- **Skill:** `skills/caption-writer.md` · **SOP basis:** agency-os SKILL 17-marketing + caption-pack SOP.

## 11. Publish Prep

- **Worker:** `PublishPrep` · **Division:** MKT · **Task type:** `publish_prep` · **Gate:** `post it`
- **What it does:** prepares an approved post for publishing — final file + caption + first comment + scheduled time (US Eastern). Only PREPARE — it does not publish. Detached auto-publish is forbidden (2026-10-10 lesson).
- **Input:** `count` (default: 2).
- **Output:** Publish-ready pack. Publishing only from the main chat, when Boss says "post it".
- **Skill:** `skills/publish-prep.md` · **SOP basis:** agency-os SKILL 17-marketing + 2026-10-10 publishing lesson.

## 12. Objection Simulator

- **Worker:** `ObjectionSimulator` · **Division:** MKT · **Task type:** `objection_sim` · **Gate:** `ok`
- **What it does:** tests the draft by playing a skeptical prospect before real outreach — 5 likely objections, in the prospect's own words, ranked by likelihood, with a one-line rebuttal angle for each. It must be tough — a weak draft cannot survive.
- **Input:** `draft`, `prospect` (both default empty).
- **Output:** 5 objections + rebuttal angle. REVIEW ONLY — never sent to the prospect.
- **Skill:** `skills/objection-simulator.md` · **SOP basis:** agency-os SKILL 16-sales-outreach (objection handling).

## 13. Inbox Triager

- **Worker:** `InboxTriager` · **Division:** OPS · **Task type:** `inbox_triage` · **Gate:** None
- **What it does:** organizes the inbox — urgent / prospect / vendor / noise. Writes draft replies in Boss's voice (short, plain). Flags Boss when money, a promise, or sending is involved. Sends nothing.
- **Input:** (no default payload — the inbox is the input).
- **Output:** Triage list + draft reply. Sends: False — DRAFT ONLY.
- **Skill:** `skills/inbox-triager.md` · **SOP basis:** agency-os SKILL 20-agency-operations + 15-crm-lead-machine.

## 14. Report Compiler

- **Worker:** `ReportCompiler` · **Division:** OPS · **Task type:** `report_compile` · **Gate:** None
- **What it does:** builds the weekly performance report — what was posted, best/worst using platform numbers that can actually be seen, lead list (name/platform/message/next step), what changes next week. Without numbers it says "none" and asks Boss to paste them — never a guess or invented metric.
- **Input:** (no default payload — the week's work + platform numbers are the input).
- **Output:** Report — posted, performance, leads, next-week. Metrics policy: visible-only.
- **Skill:** `skills/report-compiler.md` · **SOP basis:** agency-os SKILL 20-agency-operations (reporting) + 15-crm-lead-machine.

## 15. Scheduler

- **Worker:** `SchedulerAssistant` · **Division:** OPS · **Task type:** `schedule_help` · **Gate:** None
- **What it does:** helps with scheduling — proposes 3 slots (Asia/Dhaka + US-Eastern equivalent), writes a draft invite. Nothing is sent before Boss confirms.
- **Input:** `what` (default: client demo call).
- **Output:** 3 slots + draft invite. Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time).
- **Skill:** `skills/scheduler.md` · **SOP basis:** agency-os SKILL 20-agency-operations.

---

**Source:** `01-Agency-Department/engine/workers/src/workers/{acquisition,delivery,marketing,admin}.py` (vendored; upstream `~/workspace/boss-ceo/src/workers/`)
(task_kind / default_payload / requires_gate) · `../chief_of_staff_agency.py` (ROUTING)
· `../pipeline.md` · `~/workspace/agency-os/SOP/prospect-qualification-talvenor.md`
· agency-os SKILL 02, 03, 06, 15, 16, 17, 18, 20.

---

## Phase 7 — Section map (2026-11-17)

15 mapped staff (the list above) + 6 NEW section agents = **21 staff**.
Mapped staff workers' code stays vendored in the engine
(`engine/workers/src/workers/`), not duplicated — only mapped here.
NEW agents are real `.py` files in `sections/<section>/agents/` + their own skill
(`sections/<section>/skills/`). The Chief's `SECTION_ROUTING` gets 6 new
task types (the ROUTING's 15 are unchanged).

| Section | Staff | Task type | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|---|---|
| receive | ClientIntakeReceiver | `client_intake` | `sections/receive/agents/client_intake_receiver.py` | `sections/receive/skills/client-intake-receiver.md` | `send` | NEW |
| receive | InboxTriager | `inbox_triage` | `engine/workers/src/workers/admin.py` | `engine/skills/inbox-triager.md` | None | MAPPED |
| receive | ProspectResearcher | `prospect_research` | `engine/workers/src/workers/acquisition.py` | `engine/skills/prospect-researcher.md` | None | MAPPED |
| receive | SchedulerAssistant | `schedule_help` | `engine/workers/src/workers/admin.py` | `engine/skills/scheduler.md` | None | MAPPED |
| sell | OutreachDrafter | `outreach_draft` | `engine/workers/src/workers/acquisition.py` | `engine/skills/outreach-drafter.md` | `send` | MAPPED |
| sell | ReplyHandler | `reply_triage` | `engine/workers/src/workers/acquisition.py` | `engine/skills/reply-triager.md` | `send` | MAPPED |
| sell | NegotiationCoach | `negotiation_prep` | `engine/workers/src/workers/acquisition.py` | `engine/skills/negotiation-coach.md` | `ok` | MAPPED |
| sell | ObjectionSimulator | `objection_sim` | `engine/workers/src/workers/marketing.py` | `engine/skills/objection-simulator.md` | `ok` | MAPPED |
| sell | SalesCloser | `sales_close` | `sections/sell/agents/sales_closer.py` | `sections/sell/skills/sales-closer.md` | `ok` | NEW |
| sell | FollowUpAgent | `followup_draft` | `sections/sell/agents/followup_agent.py` | `sections/sell/skills/followup-agent.md` | `send` | NEW |
| delivery | RetellBuilder | `receptionist_build` | `engine/workers/src/workers/delivery.py` | `engine/skills/receptionist-builder.md` | `ok` | MAPPED |
| delivery | QAEngineer | `receptionist_qa` | `engine/workers/src/workers/delivery.py` | `engine/skills/qa-engineer.md` | None | MAPPED |
| delivery | OnboardingAgent | `onboarding_draft` | `engine/workers/src/workers/delivery.py` | `engine/skills/onboarding-agent.md` | `ok` | MAPPED |
| delivery | ServiceDeliveryManager | `delivery_manage` | `sections/delivery/agents/service_delivery_manager.py` | `sections/delivery/skills/service-delivery-manager.md` | `ok` | NEW |
| delivery | ClientSuccessAgent | `client_success` | `sections/delivery/agents/client_success_agent.py` | `sections/delivery/skills/client-success-agent.md` | `send` | NEW |
| marketing | ContentPlanner | `content_plan` | `engine/workers/src/workers/marketing.py` | `engine/skills/content-planner.md` | `ok` | MAPPED |
| marketing | VideoProducer | `video_produce` | `engine/workers/src/workers/marketing.py` | `engine/skills/video-producer.md` | `ok` | MAPPED |
| marketing | CaptionWriter | `caption_write` | `engine/workers/src/workers/marketing.py` | `engine/skills/caption-writer.md` | None | MAPPED |
| marketing | PublishPrep | `publish_prep` | `engine/workers/src/workers/marketing.py` | `engine/skills/publish-prep.md` | `post it` | MAPPED |
| ops | ReportCompiler | `report_compile` | `engine/workers/src/workers/admin.py` | `engine/skills/report-compiler.md` | None | MAPPED |
| ops | BillingInvoiceAgent | `billing_invoice` | `sections/ops/agents/billing_invoice_agent.py` | `sections/ops/skills/billing-invoice-agent.md` | `ok` | NEW |

**True status (2026-11-17, Phase 7):** Email PAUSED (since 2026-11-14) —
the draft is the final word. Paying client 0. First mail 163 — no state is at 100,
no follow-up is due (100-mail rule). LOCKED pricing only for the invoice
(Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build;
Scale $1,672/mo + $1,997 build) — never quote a price to a prospect.
