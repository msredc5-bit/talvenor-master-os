"""Payment-Rails Checker — Gate 0 test steps + record of Boss's result (section agent).

Role: write the Gate 0 test steps and record Boss's result —
Lemon Squeezy signup (as a BD individual), and if it fails, the fallback order:
Polar → Gumroad (as an individual, not an LLC).
Gate: no gate — this is only checking + recording.
Gate 0 status: **NOT PASSED** — this role watches Gate 0,
but never writes "PASSED" itself. Boss's result is recorded only when Boss
reports it (as a verbatim quote); this agent does not change the Status line
of gate0-status.md — it writes no file at all.
Never does this: signs up on Lemon Squeezy / Polar / Gumroad itself;
says Gate 0 PASSED on its own; brings Etsy into the plan (closed for
Bangladesh — hard no); writes any file; touches the network.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
GATED_ACTIONS = ("send", "publish", "spend", "delete")

GATE0_STEPS = [
    "1. Go to lemonsqueezy.com — sign up as an individual (not MAINUDDIN LLC — the LLC is US-registered with no US bank, so individual is the right path).",
    "2. Look at the payout method — check whether BD bank payout is available.",
    "3. Tell Boss the result: pass / fail / what it said (a screenshot helps). Boss's step, ~15 min, $0.",
    "4. If Lemon Squeezy fails (triage/blocked), test the backup rail — Polar (BD is on the seller/payout list, Stripe Connect Express).",
    "5. If Polar also fails, Gumroad — BD bank payout exists, must register as an individual (not an LLC).",
    "6. If all rails are closed, the product track is fully KILLed — the kit will not be built, Boss will be told.",
]

RAIL_FEES = [
    "Lemon Squeezy: 5% + $0.50, $50 min payout (research report §2, 2026-11-12).",
    "Polar: 5% + $0.50.",
    "Gumroad: ~12.9% + $0.80 effective, $100 min payout.",
    "Etsy: hard no — closed for Bangladesh, never in the plan.",
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


class PaymentRailsCheckerAgent:
    """Writes Gate 0 test steps + records Boss's result — does not sign up."""

    task_kind = "gate0_check"
    gate = None
    section = "finance"
    role = "Payment-Rails Checker"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        payload = task.get("payload") or {}
        gate0 = _gate0_status()
        lines = [
            "Gate 0 — Lemon Squeezy Signup Test (test steps + record).",
            "Current status (read from gate0-status.md): %s." % gate0["status"],
            "",
            "Test steps (Boss's step, ~15 min, $0 — this agent never signs up itself):",
        ]
        lines.extend("  " + step for step in GATE0_STEPS)
        lines.append("")
        lines.append("Rail fees (research report §2, 2026-11-12):")
        lines.extend("  - " + fee for fee in RAIL_FEES)
        boss_result = (payload.get("boss_result") or "").strip()
        if boss_result:
            lines.append("")
            lines.append("Result reported by Boss (record only — verbatim quote, not this agent's verdict):")
            lines.append("  \"%s\"" % boss_result)
            lines.append("This agent never writes Gate 0 PASSED itself. Changing the Status line of gate0-status.md is a manual step on Boss's word — this agent writes no file.")
        else:
            lines.append("")
            lines.append("Boss's result has not arrived yet — it will be recorded only when Boss tests and reports it. This agent never writes PASSED/FAILED on its own.")
        static_text = "\n".join(lines)
        output = _draft_with_brain(
            brain, "Gate 0 payment rails test steps draft", static_text)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section, "gate0": gate0,
                "boss_result_recorded": bool(boss_result),
                "output": output,
                "notes": "Gate 0's true status, read from gate0-status.md. No verdict without Boss's result.",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
