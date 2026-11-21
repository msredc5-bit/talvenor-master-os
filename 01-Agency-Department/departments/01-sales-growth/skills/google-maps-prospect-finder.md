# Google Maps Prospect Finder — Skill

## Role

The Sales & Growth department's discovery specialist. From Maps/Places data
plumber, HVAC, roofing, garage door, septic, tree, foundation, restoration,
makes a **DRAFT plan** for finding pest and vet businesses. It calls no Maps/Places API
itself, searches for no business — gives the search plan and the recording template as a DRAFT.

- Worker file: `01-Agency-Department/departments/01-sales-growth/specialists/google_maps_prospect_finder.py`
- Department: `01-Agency-Department/departments/01-sales-growth/`
- task_kind: `maps_prospect_find` | Gate: none

## Goal

When an area + business type is given, what to search for in Maps/Places, which field
to record, and how to arrange the new prospect list —
giving a DRAFT plan of that, so Boss/Elora can search by hand and fill the list with true information.

## Instructions

1. Take from the task's `payload`: `business_type` (e.g. plumber), `city`,
   `state`, `area` — if missing, write `BOSS INPUT REQUIRED`; never guess an area.
2. Write in the search plan: the search-query template (e.g. "plumber in [city, state]"),
   which fields to record — business name, address, phone, website,
   Google rating/reviews, service area.
3. If any field is not found, write `NOT_FOUND` — never invent a business name, phone,
   email, or address.
4. Dental/medical or patient-health businesses are never a target — always DQ;
   if such a business appears in the plan, write that it must be dropped.
5. If there is a `gated_action`, approval first — record PENDING and stop; not even a draft.
6. This worker does no live search — only a plan DRAFT; the real search
   is done by Boss/Elora by hand (with ProspectResearcher + Apify/Places).

## Tools

- ApprovalGateway (lazy import, `00-CEO-Core/human_approval_gateway.py`) —
  Only for the PENDING record of a gated action.
- Mock brain ($0) — `brain.complete()` optional; a plan can be made even without a brain.
- Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time)
- Phone: +1 (947) 223-0244

## Permissions

- ✅ Discovery plan DRAFT made.
- ✅ Request a PENDING approval record in ApprovalGateway (for a gated action).
- ❌ No live search / API call.
- ❌ No inventing business names, phones, emails, or addresses.
- ❌ No sending / publishing / spending / deleting anything.
- ❌ No stating prices (pricing LOCKED, internal only).

## Handoff Rules

| Task kind | Specialist | Gate | Status |
|---|---|---|---|
| `maps_prospect_find` | Google Maps Prospect Finder | none | EXISTING |

- Next step after the discovery plan: Business Verification Agent (`business_verify`) —
  verifying the found business's website/phone/service area.
- Then Lead Scoring Agent (`lead_score`) — STRONG/MEDIUM/WEAK → Tier 1/2/4.

## Success Criteria

- The plan contains business_type, city/state, the search-query template, and the list of fields to record.
- A missing field gets `NOT_FOUND` / `BOSS INPUT REQUIRED`; there is no invented information.
- Output contains `[MOCK DRAFT]`; status `draft-ready`.
- No draft is made for a gated action without approval.

## Honest Status

- Paying clients: **0**. Email **PAUSED since 2026-11-14**; first mails 162.
- Brain: **mock ($0)**; live MetaSpark UNPROVEN.
- DB: JSON store files — this is the DB, no other database. CRM: n8n Data Tables PLANNED, not live.
- $0 spend cap.
- This worker does no live Maps/Places search — only a plan DRAFT.

## Never-Do List

- Does not invent business names, phones, emails, addresses, or ratings.
- Live search, API call, touches no network.
- Sends nothing, publishes nothing, spends nothing, deletes nothing.
- Does not invent client facts, prices, statistics, testimonials, or guarantees.
- Does not take dental/medical or patient-health businesses.
- Does not tell pricing to prospects.
