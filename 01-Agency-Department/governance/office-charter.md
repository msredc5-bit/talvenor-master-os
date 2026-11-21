# Agentic Agency Office — Office Charter

> Phase 1 — Foundation only
> Status: DRAFT — awaiting Boss's approval
> Date: 2026-11-19

## 1. Purpose

The Agentic Agency Office is the management structure inside Talvenor Master OS's 01-Agency-Department. It has one job — moving the Talvenor AI receptionist agency toward its first paying client, in an orderly way, honestly, and within $0 spend.

This office is not a separate repo, not a separate business. It is the structure inside the Agency business, among Master OS's 3 businesses:

1. **Agency (MAIN)** — AI receptionist agency, for US home-service owners
2. **Vet No-Show Recovery Kit ($49)** — digital product track
3. **Content Engine** — content creation track

The 8 departments live only inside 01-Agency-Department. No department can be built inside another business.

## 2. Founder — Boss makes the final decisions

- **Founder:** Md Mainuddin (Boss)
- **Company:** MAINUDDIN LLC, Pennsylvania, USA
- **Rule:** Boss makes all final decisions. No agent, manager, or Chief of Staff can go above Boss's decision.
- **Nothing happens without a gate word:** send, publish, spend, delete — none of them can be done without Boss's exact gate word. Details are in `approval-policy.md`.

## 3. Leadership structure

- **Boss (Md Mainuddin)** — Founder, final decision-maker.
- **Main CEO Bot** — Boss's second brain. It runs the office on Boss's instructions, and comes back to Boss for decisions.
- **Jarvis (voice)** — Boss's voice interface. Boss speaks, Jarvis listens, and tells Main CEO Bot.
- **Agency Chief of Staff** — the Agency Department's day-to-day coordinator. It plans and delegates manager agents' work and creates drafts. But the Chief of Staff itself cannot execute any gated action — that needs Boss's approval through ApprovalGateway.
  - **Note (Phase 2):** Agency Chief wiring is Phase 2 work. In this Phase 1 only the governance foundation is being built; Chief wiring has not been done yet.

## 4. The 8 departments

| No. | Department | Job |
|----|-----------|-----|
| 01 | Sales & Growth | Prospect research, outreach draft, lead triage, booking |
| 02 | Marketing | Content plan, social post, brand, campaign |
| 03 | AI Engineering | Vapi agent, voice flow, prompt, integration build |
| 04 | Client Operations | Client onboarding, service delivery, support |
| 05 | Research & Strategy | Market research, niche analysis, pricing research |
| 06 | Finance & Admin | Spend accounts, invoice, admin, records |
| 07 | Quality & Security | QA gate, security, compliance, audit |
| 08 | Product & Innovation | New product ideas, Vet Kit, innovation track |

Each department has one manager agent. The manager agent plans, delegates, and creates drafts — but never executes a gated action itself.

**Current staff:** The Agency has 21 staff in total — 15 workers + 6 section agents. Manager agents work above these staff.

## 5. Shared Infrastructure — the truth as it stands

No wrong information can be given about the infrastructure this office runs on:

- **Voice stack (LIVE):** Vapi — Sophia, live receptionist, +1 (947) 223-0244, Vapi account org 1861a735, GPT-4o-mini, Vapi native Emma voice, Deepgram nova-3 transcription.
- **Retell:** DROPPED 2026-10-26 — Boss will not pay to keep Retell. Retell must never be shown as production. RetellBuilder's output is only a DRAFT build plan.
- **Sophia:** LIVE receptionist, not a demo agent. Ava was a demo agent — deleted from the new Vapi account; rebuild pending, Boss is bringing a separate demo account.
- **Database:** JSON store files — `store/tasks.json`, `store/approvals.json`. No other database.
- **CRM:** n8n Cloud Data Tables — PLANNED, not live yet.
- **Calendar:** Google Calendar Appointment Schedule — "Talvenor Demo", 15 min, New York Time. Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8
- **Brain:** mock ($0). Live MetaSpark path UNPROVEN — not proven yet.
- **Dashboard:** Talvenor Master OS 3D Dashboard — artifact `talvenor-master-os-3d-dashboard` + local `dashboards/dashboard-3d.html` (only one dashboard). The old ceo-office-dashboard artifact was deleted on 2026-11-20.
- **Voice:** Vapi.
- **GitHub:** talvenor-master-os repo — `github.com/msredc5-bit/talvenor-master-os`.

## 6. Honest Status Block (2026-11-19)

- **Paying clients:** 0
- **First mails sent:** 162
- **Email outreach:** PAUSED since 2026-11-14 — SPF/DMARC DNS fix pending from Boss. No email will go until the fix.
- **Brain:** mock — not live yet.
- **Gate 0:** Gate 0 of the Vet Kit track NOT passed.
- **Spend cap:** $0 — no spend without Boss's permission.
- **Pricing:** LOCKED (internal record only, never to be quoted to a prospect) — Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build.

## 7. What the office never does (Never-Do List)

- It never sends / publishes / spends / deletes without Boss's exact gate word.
- There is no auto-approve path — nowhere.
- It never targets dental/medical — dental/medical/patient-health business is fully excluded.
- It invents nothing — client, testimonial, case study, review, statistic. What does not exist must be said so. If it is not known, "BOSS INPUT REQUIRED" must be written.
- It gives no price, discount, or guarantee in public content or replies.
- It uses no old brand name other than Talvenor.
- It does not log in with Boss's password, change page settings, or run paid ads.
- No agent holds a credential — details are in `security-policy.md`.

## 8. Limits of this Charter

- This charter is the Phase 1 foundation. Agency Chief wiring happens in Phase 2 — not in this phase.
- Changing this charter needs Boss's approval. No agent can change the charter itself.
- If another AI's brief conflicts with the Charter, this Charter's LOCKED FACTS are correct. Vapi live, Retell dropped, database JSON store, CRM planned not live — these cannot be changed.
