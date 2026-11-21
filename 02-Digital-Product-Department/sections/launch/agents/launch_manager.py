"""Launch Manager — Vet Kit launch checklist DRAFT (section agent).

Role: build the launch checklist DRAFT — Gate 0, the kit's 6 parts,
Gate 1 check, store listing, sales page, emailing 100 clinics, writing
replies + sales in a sheet.
Gate: Boss's `go` is needed to move the launch forward.
Gate 0 status: **NOT PASSED** — no launch can happen. This
agent only gives a DRAFT checklist, status `blocked-gate0`; it marks
nothing as launched, records no sale.
Never does this: launches; honors mark_launched / mark_sold; writes any
file; sends mail; invents a client/testimonial/statistic;
touches the network.
"""

import os
import sys

KIT_PRICE_USD_ONE_TIME = 49
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
GATED_ACTIONS = ("send", "publish", "spend", "delete")

LAUNCH_CHECKLIST = [
    "Gate 0 passed (does the Lemon Squeezy store open?) — still NOT PASSED",
    "The kit's 6 parts built (Sheets + Docs + script) — not done yet (0/6)",
    "Cadence checked against AAHA/PetDesk guidance (Gate 1) — not done yet",
    "Lemon Squeezy listing + Gumroad backup listing — not done yet",
    "Sales page — Boss will review before launch",
    "Email 100 clinics, 25 a day (4 days) — email channel is now PAUSED (since 2026-11-14)",
    "Write every reply + sale in a sheet — sales are still 0",
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


def _gate0_status():
    """Reads the Status line of gate0-status.md — NOT PASSED unless PASSED is written (fail-closed)."""
    text = _read_dept_file("gate0-status.md")
    if text is None:
        return {"status": "NOT PASSED",
                "note": "gate0-status.md could not be read — fail-closed: treated as NOT PASSED."}
    for line in text.splitlines():
        stripped = line.strip().lstrip("*").strip()
        if stripped.startswith("Status:"):
            value = stripped[len("Status:"):].strip().lstrip("*").strip()
            if value.startswith("PASSED"):
                return {"status": "PASSED",
                        "note": "gate0-status.md says Status: PASSED."}
            return {"status": "NOT PASSED",
                    "note": "Gate 0 has not passed — the Lemon Squeezy signup test is Boss's step, still pending."}
    return {"status": "NOT PASSED",
            "note": "No Status line found in gate0-status.md — fail-closed: treated as NOT PASSED."}


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


class LaunchManagerAgent:
    """Gives a launch checklist DRAFT — does not launch itself."""

    task_kind = "launch_prep"
    gate = "go"
    section = "launch"
    role = "Launch Manager"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        payload = task.get("payload") or {}
        gate0 = _gate0_status()
        checklist_text = "\n".join(
            "  %d. %s" % (i, item)
            for i, item in enumerate(LAUNCH_CHECKLIST, 1))
        summary = (
            "Launch checklist DRAFT — Vet No-Show Recovery Kit ($49 one-time).\n"
            + checklist_text + "\n"
            "Gate 0: %s. Kit built: 0/6. PA list: 39/100. Sale: 0." % gate0["status"])
        if payload.get("mark_sold") or payload.get("mark_launched"):
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section, "gate0": gate0, "output": summary,
                    "notes": "A launch/sale claim is blocked at Gate 0 — nothing was recorded as launched/sold, sales are still 0.",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        if gate0["status"] != "PASSED":
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section, "gate0": gate0, "output": summary,
                    "notes": "DRAFT checklist only — no launch has happened, and it cannot happen. Launch is blocked until Gate 0 passes.",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        output = _draft_with_brain(
            brain, "Vet No-Show Recovery Kit launch checklist draft", summary)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section, "gate0": gate0, "output": output,
                "notes": "Gate 0 has passed — moving the launch forward needs Boss's 'go'. Checklist DRAFT only; this agent does not launch.",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
