"""Kit QA — QA checklist for the Vet No-Show Recovery Kit's 6 parts (section agent, NEW).

Role: write a QA checklist DRAFT against the 6 parts in kit-outline.md —
whether any part has been built, and if so, what must be checked.
Gate: Boss's `ok` is needed to use the QA result.
Gate 0 status: **NOT PASSED** — none of the kit's 6 parts
has been built (0/6), so there is nothing to QA. This agent returns:
"NOT BUILT — nothing to QA yet" + a QA checklist DRAFT for each part.
Never does this: claims any part passed (nothing has been built at all);
builds the kit; writes any file; invents a client/testimonial/statistic;
touches the network.
"""

import os
import sys

KIT_PRICE_USD_ONE_TIME = 49
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
GATED_ACTIONS = ("send", "publish", "spend", "delete")

# (slug, QA checklist — from kit-outline.md, to be checked after Gate 0)
KIT_QA_ITEMS = [
    ("reminder-cadence-pack",
     "Whether all three touches T-72h / T-24h / T-2h are present; whether [NAME] / [PET] / [TIME] fields exist; "
     "Gate 1: whether the cadence + script match AAHA/PetDesk's published guidance."),
    ("same-day-rebooking",
     "Whether both the phone + in-person scripts are in plain US English; whether filling the slot the same day is covered."),
    ("waitlist-fill-sop",
     "Whether it is one page; whether it says who to call first + in what order + the exact call script."),
    ("no-show-log-tracker",
     "Whether the formulas auto-total (test with sample numbers); whether it shows all three: the month's misses / estimated $ loss / recovery rate."),
    ("deposit-policy-template",
     "Whether 'have your own attorney review before using' is written; whether it is not presented as legal advice."),
    ("front-desk-quick-card",
     "Whether it is 5 lines; whether it is one page; whether it is fit to keep at the reception desk."),
]

GLOBAL_QA_CHECKS = [
    "Whether 'Talvenor' is spelled correctly everywhere.",
    "Whether there is any invented client / testimonial / statistic.",
    "Whether there is any claim to replace a PIMS (practice-management software) — the kit works alongside a PIMS.",
    "Whether there is any claim of a verified $49 sale (the price is an inference, not observed traction).",
    "Whether there is any plan to email a clinic twice.",
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


def _read_dept_file(name):
    try:
        with open(os.path.join(_dept_dir(), name), "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, OSError):
        return None


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


class KitQAAgent:
    """Gives a QA checklist DRAFT for the kit's 6 parts — never calls any part passed."""

    task_kind = "kit_qa"
    gate = "ok"
    section = "product"
    role = "Kit QA"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        blueprint = _read_dept_file("kit-outline.md")
        lines = [
            "NOT BUILT — nothing to QA yet",
            "Vet No-Show Recovery Kit ($49 one-time) — none of the 6 parts has been built (0/6).",
            "There is nothing to QA. The checklist DRAFT below must be checked against each part after Gate 0 passes + build.",
            "Blueprint source: kit-outline.md (present: %s, chars: %d)." % (
                blueprint is not None, len(blueprint) if blueprint else 0),
            "",
            "Per-part QA checklist (DRAFT):",
        ]
        for i, (slug, checks) in enumerate(KIT_QA_ITEMS, 1):
            lines.append("  %d. %s — status: NOT BUILT" % (i, slug))
            lines.append("     Checks: %s" % checks)
        lines.append("")
        lines.append("Global checks (all parts):")
        for item in GLOBAL_QA_CHECKS:
            lines.append("  - %s" % item)
        lines.append("")
        lines.append("Verdict: no part has passed QA — nothing has been built at all. Checklist DRAFT only.")
        static_text = "\n".join(lines)
        output = _draft_with_brain(
            brain, "Vet No-Show Recovery Kit QA checklist draft", static_text)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section,
                "parts_built": 0, "parts_total": len(KIT_QA_ITEMS),
                "output": output,
                "notes": "No part has passed QA — nothing has been built at all. Checklist DRAFT; QA again after build.",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
