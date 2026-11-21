# Agency — sub_agents

This folder will hold the Agency's workers. The real workers were already built in `~/workspace/boss-ceo/` — in Phase 6 their copies were brought into this repo's `01-Agency-Department/engine/workers/`. **Since Phase 1, `chief_of_staff_agency.py` really calls them** (mock brain, $0) — routing by task type below.

## Real workers — WIRED (Phase 1, REUSED engine)

Task type → worker → gate. Gate = the word Boss needs to send/use the output.
Even when a worker runs, the result is only a DRAFT — sending/publishing
is not done by this Chief.

### ACQ — Client Acquisition
| Task type | Worker | Job | Gate | Status |
|---|---|---|---|---|
| `prospect_research` | ProspectResearcher | Finding US home-service SMBs, looking for missed-call signals | None | mock-tested |
| `outreach_draft` | OutreachDrafter | Cold email / IG DM draft (5 each) | `send` | **1 live run (2026-11-06, 5 real drafts, DRAFT ONLY)** |
| `reply_triage` | ReplyHandler | Prospect reply triage, locked reply rule | `send` | mock-tested |
| `negotiation_prep` | NegotiationCoach | Sales call prep | `ok` | mock-tested |

### DEL — Receptionist Delivery
| Task type | Worker | Job | Gate | Status |
|---|---|---|---|---|
| `receptionist_build` | RetellBuilder | Receptionist build plan (DRAFT only) | `ok` | mock-tested — **live stack Vapi/Sophia, not Retell; output is only a plan** |
| `receptionist_qa` | QAEngineer | Running the QA checklist | None | mock-tested |
| `onboarding_draft` | OnboardingAgent | Client onboarding pack draft | `ok` | mock-tested |

### MKT — Marketing & Content
| Task type | Worker | Job | Gate | Status |
|---|---|---|---|---|
| `content_plan` | ContentPlanner | Sunday 5-post weekly plan | `ok` | mock-tested |
| `video_produce` | VideoProducer | Video package: script, shot list, voiceover | `ok` | mock-tested |
| `caption_write` | CaptionWriter | Caption + hashtag | None | mock-tested |
| `publish_prep` | PublishPrep | Preparing a post for publishing (never publishes) | `post it` | mock-tested |
| `objection_sim` | ObjectionSimulator | Simulating prospect objections + answers | `ok` | mock-tested |

### OPS — Operations & Admin
| Task type | Worker | Job | Gate | Status |
|---|---|---|---|---|
| `inbox_triage` | InboxTriager | Inbox triage, reply draft | None | mock-tested |
| `report_compile` | ReportCompiler | Sunday report — only metrics that can be seen | None | mock-tested |
| `schedule_help` | SchedulerAssistant | Scheduling help | None | mock-tested |

Total: 15 workers — all mock-tested, 1 live run happened (OutreachDrafter,
5 real drafts, DRAFT ONLY). Boss has not approved a full live day yet.

Source: `01-Agency-Department/engine/workers/src/workers/` (vendored copy; upstream `~/workspace/boss-ceo/src/workers/`) (acquisition.py, delivery.py,
marketing.py, admin.py) + `~/workspace/ceo-os-summary/CEO-OS-A-to-Z-summary.md` §3.
Routing code: `chief_of_staff_agency.py` — `ROUTING` table.
