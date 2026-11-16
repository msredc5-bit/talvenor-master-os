# Agency — sub_agents

এই folder-এ Agency-র worker-রা থাকবে। আসল worker-রা আগেই বানানো ছিল `~/workspace/boss-ceo/`-তে — Phase 6-এ ওদের copy এই repo-র `01-Agency-Department/engine/workers/`-এ আনা হয়েছে। **Phase 1 থেকে `chief_of_staff_agency.py` ওদের সত্যিই ডাকে** (mock brain, $0) — task type অনুযায়ী routing নিচে।

## আসল worker — WIRED (Phase 1, REUSED engine)

Task type → worker → gate। Gate = output পাঠাতে/ব্যবহার করতে Boss-এর
যে শব্দ লাগবে। Worker চালালেও ফলাফল শুধু DRAFT — পাঠানো/পাবলিশ
এই Chief করে না।

### ACQ — Client Acquisition
| Task type | Worker | কাজ | Gate | অবস্থা |
|---|---|---|---|---|
| `prospect_research` | ProspectResearcher | US home-service SMB খোঁজা, missed-call signal দেখা | নেই | mock-tested |
| `outreach_draft` | OutreachDrafter | Cold email / IG DM draft (৫টা করে) | `send` | **১টা live run (2026-11-06, ৫টা real draft, DRAFT ONLY)** |
| `reply_triage` | ReplyHandler | Prospect reply triage, locked reply rule | `send` | mock-tested |
| `negotiation_prep` | NegotiationCoach | Sales call-এর প্রস্তুতি | `ok` | mock-tested |

### DEL — Receptionist Delivery
| Task type | Worker | কাজ | Gate | অবস্থা |
|---|---|---|---|---|
| `receptionist_build` | RetellBuilder | Receptionist build plan (DRAFT only) | `ok` | mock-tested — **live stack Vapi/Sophia, Retell নয়; output শুধু plan** |
| `receptionist_qa` | QAEngineer | QA checklist চালানো | নেই | mock-tested |
| `onboarding_draft` | OnboardingAgent | Client onboarding pack draft | `ok` | mock-tested |

### MKT — Marketing & Content
| Task type | Worker | কাজ | Gate | অবস্থা |
|---|---|---|---|---|
| `content_plan` | ContentPlanner | রবিবার ৫-পোস্ট weekly plan | `ok` | mock-tested |
| `video_produce` | VideoProducer | Video package: script, shot list, voiceover | `ok` | mock-tested |
| `caption_write` | CaptionWriter | Caption + hashtag | নেই | mock-tested |
| `publish_prep` | PublishPrep | Post publish-এর জন্য তৈরি (কখনো publish করে না) | `post it` | mock-tested |
| `objection_sim` | ObjectionSimulator | Prospect objection + উত্তর simulate | `ok` | mock-tested |

### OPS — Operations & Admin
| Task type | Worker | কাজ | Gate | অবস্থা |
|---|---|---|---|---|
| `inbox_triage` | InboxTriager | Inbox triage, reply draft | নেই | mock-tested |
| `report_compile` | ReportCompiler | রবিবার report — শুধু দেখা যায় এমন metric | নেই | mock-tested |
| `schedule_help` | SchedulerAssistant | Scheduling সাহায্য | নেই | mock-tested |

মোট: ১৫ worker — সব mock-tested, ১টা live run হয়েছে (OutreachDrafter,
৫টা real draft, DRAFT ONLY)। Full live day এখনো Boss approve করেননি।

সূত্র: `01-Agency-Department/engine/workers/src/workers/` (vendored copy; upstream `~/workspace/boss-ceo/src/workers/`) (acquisition.py, delivery.py,
marketing.py, admin.py) + `~/workspace/ceo-os-summary/CEO-OS-A-to-Z-summary.md` §3।
Routing কোড: `chief_of_staff_agency.py` — `ROUTING` table।
