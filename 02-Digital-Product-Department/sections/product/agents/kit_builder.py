"""Kit Builder — builder of the Vet No-Show Recovery Kit's 6 parts (section agent).

Role: read the blueprint (design) in kit-outline.md and return a summary
of the kit's 6 parts + the build order.
Gate: Boss's `ok` is needed to start building / use the output.
Gate 0 status: **NOT PASSED** — the Lemon Squeezy signup test is
Boss's step, still pending. So this agent builds no part of the kit; it only
gives the blueprint's summary + build order, status `blocked-gate0`.
Never does this: builds any part of the kit (Sheets/Docs), writes any file,
marks anything as sold/launched, invents a client/testimonial/statistic,
claims a verified $49 sale exists, touches the network.
"""

import os
import sys

KIT_PRICE_USD_ONE_TIME = 49
KIT_LAUNCH_PRICE_USD_ONE_TIME = 39
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
PA_LIST_TARGET = 100
GATED_ACTIONS = ("send", "publish", "spend", "delete")

KIT_PARTS = [
    ("reminder-cadence-pack", "Reminder Cadence Pack — T-72h / T-24h / T-2h SMS + email + call script"),
    ("same-day-rebooking", "Same-Day Rebooking Scripts — phone + in-person script"),
    ("waitlist-fill-sop", "Waitlist-Fill SOP — one-page SOP + call script"),
    ("no-show-log-tracker", "No-Show Log + $ Tracker — Sheets, with formulas"),
    ("deposit-policy-template", "Deposit / No-Show Policy Template — with attorney-review note"),
    ("front-desk-quick-card", "Front-Desk Quick Card — 5 lines, one page"),
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


class KitBuilderAgent:
    """Gives the kit's blueprint summary + build order — does not build the kit itself."""

    task_kind = "kit_build"
    gate = "ok"
    section = "product"
    role = "Kit Builder"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        payload = task.get("payload") or {}
        gate0 = _gate0_status()
        blueprint = _read_dept_file("kit-outline.md")
        parts_text = "\n".join(
            "  %d. %s — %s" % (i, slug, name)
            for i, (slug, name) in enumerate(KIT_PARTS, 1))
        build_order = (
            "Build order (kit-outline.md — after Gate 0, 3–4 weeks, 1 hour/day, $0):\n"
            "  Week 0 — Gate 0: Lemon Squeezy signup test (Boss's step)\n"
            "  Week 1 — Validate + list: check the cadence against AAHA/PetDesk (Gate 1); complete the PA list to 100\n"
            "  Week 2 — Build: build the 6 parts in Sheets/Docs; test the $ tracker formula on a sample; attorney-review note in the policy\n"
            "  Week 3 — Store + sales page: Lemon Squeezy listing (primary) + Gumroad (backup); sales page (Boss review)\n"
            "  Week 4 — Launch: 25 emails/day to 100 clinics (4 days); write replies + sales in a sheet")
        summary = (
            "BLUEPRINT ONLY — Vet No-Show Recovery Kit ($49 one-time; launch price $39 for the first 30 buyers).\n"
            "Format: Google Sheets + Google Docs + copy-paste script. No code, no app, nothing to install.\n"
            "For whom: independent companion-animal vet clinic, 1–5 vets (not a corporate chain, not a solo mobile vet).\n"
            "The kit's 6 parts (none built — 0/6):\n" + parts_text + "\n" + build_order + "\n"
            "Blueprint source: kit-outline.md (present: %s, chars: %d)." % (
                blueprint is not None, len(blueprint) if blueprint else 0))
        if payload.get("mark_sold") or payload.get("mark_launched"):
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section, "gate0": gate0, "output": summary,
                    "notes": "A sale/launch claim is blocked at Gate 0 — nothing was recorded as sold/launched, sales are still 0.",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        if gate0["status"] != "PASSED":
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section, "gate0": gate0, "output": summary,
                    "notes": "Gate 0 NOT PASSED — no part of the kit can be built. This is the blueprint's summary + build order, not the kit itself.",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        output = _draft_with_brain(
            brain, "Vet No-Show Recovery Kit build order draft", summary)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section, "gate0": gate0, "output": output,
                "notes": "Gate 0 has passed — starting the build needs Boss's 'ok'. This agent builds no file; it gives the build order plan.",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
