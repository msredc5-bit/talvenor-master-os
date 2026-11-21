"""Clinic Researcher — verify + grow the PA vet list (section agent).

Role: report the status of the verified list in pa-vet-clinics.csv and
write the rules for verifying new clinics — goal: 100 independent PA vet clinics.
Gate: no gate — building a list is safe work. But emailing anyone from
the list needs Boss's `send`, and the email channel is now PAUSED
(since 2026-11-14).
Gate 0 status: **NOT BLOCKED** — the list can be grown outside Gate 0;
but per the plan the remaining 61 clinics will be completed after Gate 0.
Never does this: invents contact details — writes "Not publicly listed"
if it is not public; brings a chain (Banfield, VCA, Vetco, BluePearl,
Thrive, PetVet365) into the list; emails/calls anyone (no outreach);
overwrites the CSV — this agent writes no file.
"""

import csv
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
PA_LIST_TARGET = 100
GATED_ACTIONS = ("send", "publish", "spend", "delete")

EXCLUDED_CHAINS = ["Banfield", "VCA", "Vetco", "BluePearl", "Thrive",
                   "PetVet365", "PetVet Care Centers"]

NEXT_CITIES_PLAN = [
    "Around Pittsburgh", "Around Harrisburg", "Lehigh Valley",
    "Bucks / Montgomery County", "Pittsburgh suburbs", "Small Central PA towns",
]


def _dept_dir():
    """Finds the department dir by locating kit-outline.md (read-only source)."""
    here = os.path.dirname(os.path.abspath(__file__))
    node = here
    for _ in range(6):
        if os.path.isfile(os.path.join(node, "kit-outline.md")):
            return node
        node = os.path.dirname(node)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))


def _read_pa_list():
    """Reads pa-vet-clinics.csv (read-only) — rows + city breakdown."""
    path = os.path.join(_dept_dir(), "pa-vet-list", "pa-vet-clinics.csv")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except (FileNotFoundError, OSError):
        return []


def _load_gateway(gateway, approvals_path):
    """ApprovalGateway lazy import — only when gated work needs it."""
    if gateway is not None:
        return gateway
    ceo_core = os.path.join(os.path.dirname(_dept_dir()), "00-CEO-Core")
    if ceo_core not in sys.path:
        sys.path.insert(0, ceo_core)
    from human_approval_gateway import ApprovalGateway  # noqa: PLC0415
    if approvals_path:
        return ApprovalGateway(approvals_path=approvals_path)
    return ApprovalGateway()


def _draft_with_brain(brain, prompt, static_text):
    """If a brain exists, uses brain.complete(prompt) to write a [MOCK DRAFT];
    otherwise static DRAFT text. Never a live call / network — the brain is mock."""
    if brain is not None:
        try:
            mock_text = brain.complete(prompt)
        except Exception:  # noqa: BLE001
            mock_text = ""
        if mock_text:
            return "[MOCK DRAFT]\n" + str(mock_text) + "\n\n---\n" + static_text
    return "DRAFT ONLY\n" + static_text


def _gated_check(agent, task, gateway, approvals_path):
    """If a gated_action is present, returns PENDING; if approved, None (only the
    DRAFT can proceed — the agent never executes a gated action)."""
    gated_action = (task or {}).get("gated_action")
    if not gated_action:
        return None
    if gated_action not in GATED_ACTIONS:
        return {"status": "error",
                "error": "Unknown gated action %r." % (gated_action,),
                "draft_only": True, "mock_brain": True, "gate": agent.gate}
    gw = _load_gateway(gateway, approvals_path)
    approval_id = task.get("approval_id")
    if approval_id:
        try:
            if gw.is_approved(approval_id):
                return None
        except Exception:  # noqa: BLE001
            pass
    approval = gw.request(gated_action, task.get("title") or agent.task_kind,
                          "Digital-Product-Section-Agent")
    return {"status": "pending-approval", "approval": approval,
            "draft_only": True, "mock_brain": True, "gate": agent.gate}


class ClinicResearcherAgent:
    """Gives the PA vet list's status + verification rules — does no outreach."""

    task_kind = "clinic_research"
    gate = None
    section = "research"
    role = "Clinic Researcher"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        rows = _read_pa_list()
        cities = {}
        with_email = 0
        for row in rows:
            city = (row.get("city") or "").strip()
            if city:
                cities[city] = cities.get(city, 0) + 1
            email = (row.get("public_email") or "").strip()
            if email and email != "Not publicly listed" and "@" in email:
                with_email += 1
        city_lines = "\n".join(
            "  - %s: %d" % (city, count)
            for city, count in sorted(cities.items()))
        static_text = "\n".join([
            "PA Vet Clinic List — verified status (read-only, from pa-vet-clinics.csv):",
            "  Rows: %d / %d (remaining %d — to be completed after Gate 0)." % (
                len(rows), PA_LIST_TARGET, PA_LIST_TARGET - len(rows)),
            "  Have a public email: %d; 'Not publicly listed': %d." % (
                with_email, len(rows) - with_email),
            "  City breakdown:",
            city_lines or "  (no rows)",
            "",
            "Verification rules (pa-vet-list/README.md):",
            "  1. Each clinic's own official website first (best), otherwise a directory listing (name + city + website/phone visible).",
            "  2. Chains EXCLUDED — cannot be added to the list: %s." % ", ".join(EXCLUDED_CHAINS),
            "  3. If the email/phone is not public, write 'Not publicly listed' — nothing can be invented.",
            "  4. Target: independent companion-animal clinic, 1–5 vets. Not a corporate chain, not a solo mobile vet.",
            "",
            "Next cities (README plan): %s." % "; ".join(NEXT_CITIES_PLAN),
            "No outreach — this agent emails/calls nobody. Emailing from the list needs Boss's 'send', and the email channel is now PAUSED (since 2026-11-14).",
        ])
        output = _draft_with_brain(
            brain, "PA vet clinic list status draft", static_text)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section,
                "pa_rows": len(rows), "pa_target": PA_LIST_TARGET,
                "with_email": with_email,
                "output": output,
                "notes": "Verified public information only — nothing invented. No clinic has been emailed.",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
