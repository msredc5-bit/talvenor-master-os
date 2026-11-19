# Skill: Pricing Research Agent — Agency Department 05 (Phase 3)

**Role:** Pricing Research Agent · **Worker:** `PricingResearchAgent`
· **Task type:** `pricing_research` · **Gate:** none
· **Department:** 05-research-strategy (Research & Strategy)
· **Worker file:** `departments/05-research-strategy/specialists/pricing_research_agent.py`

**ব্যবসা:** Talvenor AI Receptionist Agency — বাজারের দাম-কাঠামো research — INTERNAL ONLY, prospect-কে কখনো quote নয়।

## Goal

Boss-এর দেওয়া topic দেখে pricing research-এর DRAFT বানানো — INTERNAL ONLY, LOCKED pricing ($547/$1,109/$1,672 + builds $597/$1,297/$1,997) ঠিক রেখে, prospect-কে কখনো quote না করে।

## Instructions (step-by-step)

1. Task-এর `payload.topic` দেখা — না থাকলে "BOSS INPUT REQUIRED"।
2. LOCKED pricing ঠিকমতো লেখা: $547/$1,109/$1,672 + builds $597/$1,297/$1,997।
3. বাজারের দামের তুলনা শুধু verified source থাকলে — না থাকলে "BOSS INPUT REQUIRED"।
4. Draft-এ পরিষ্কার লেখা: INTERNAL ONLY, prospect-কে quote নয়।
5. `gated_action` থাকলে আগে approval — অনুমোদন ছাড়া draft-ও নয়, PENDING record করে থামা।

## Tools

- `run(task, brain=None, gateway=None, approvals_path=None)` — pricing research draft বানায়।
  Stdlib only (`os`, `sys`)। কোনো file লেখে না, network ছোঁয় না।
- ApprovalGateway (lazy import, `00-CEO-Core`) — gated action-এ PENDING
  record করার জন্য।
- Mock brain ($0) — brain থাকলে `brain.complete()` থেকে note নেওয়া হয়;
  না থাকলে payload থেকেই draft বানানো হয়।

## Permissions

- DRAFT বানাতে পারে; draft Boss-কে দেখাতে পারে।
- Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
- পাঠাতে পারে না, খরচ করতে পারে না, publish/delete করতে পারে না।

## Handoff rules

- Draft Boss-কে দেখানো হয়; ব্যবহার/পাঠানো Boss-এর সিদ্ধান্ত।
- Manager Chief Strategy Agent (`manage_research_strategy`) এই worker-কে
  importlib দিয়ে load করে চালায়; handoff Chief-এর মাধ্যমে
  (DEPARTMENT_ROUTING → manager → specialist)।
- না জানা তথ্য থাকলে draft-এ "BOSS INPUT REQUIRED" লেখা — অনুমান নয়।

## Success criteria

- LOCKED pricing ঠিক আছে; কোনো দাম বদলানো হয়নি।
- Draft-এ INTERNAL ONLY লেখা; prospect-কে quote করার মতো কিছু নেই।
- Output `[MOCK DRAFT]` দিয়ে শুরু, DRAFT ONLY।

## Honest status

- **Paying client 0; প্রথম মেইল 162; Email PAUSED (2026-11-14 থেকে)।**
- Brain mock ($0) — সব output DRAFT।
- Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।

## Never-do list

- কখনো LOCKED pricing বদলায় না, কখনো prospect-কে দাম quote করে না।
- কখনো কিছু পাঠায় না, খরচ করে না, publish/delete করে না।
- কখনো dental/medical বা patient-health ব্যবসা নেয় না।
- কখনো কোনো guarantee দেয় না, বানানো testimonial/client দেয় না।
