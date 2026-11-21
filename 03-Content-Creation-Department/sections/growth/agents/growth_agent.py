"""Growth Agent — growth section (Phase 7, NEW role).

Role: make a trend-research draft + collab-outreach draft —
which trend/topic to watch for the ToolPilot channel's growth, and what to write
for a collab with which creator/channel — as a DRAFT.
Worker: none — NEW standalone role, draft logic (brain.complete).
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers.
Pipeline stage: growth track of 1-research (trend research) — MOCK.
Status: DRAFT ONLY — mock brain ($0), all output [MOCK DRAFT].
Gate: "send" — sending collab-outreach needs Boss's gate word "send";
the outreach draft is only a DRAFT, sending is not this agent's job.

Honest truth: no trend is invented — mock brain output is a [MOCK DRAFT]
scaffold; real trend data needs Boss's input. No collab has happened yet,
no outreach has been sent.

Never does: does not send messages/emails, publish, upload,
spend, or delete. Does not invent trends / collabs / stats.
Does not write any invented client / testimonial / case study / price.
Upload OFF — this agent never uploads.
"""

import os
import sys

# Only stdlib at import time. Brain / gateway — all lazy, inside run().

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"


class GrowthAgent:
    """Growth Agent — trend research + collab-outreach draft agent (NEW, standalone)."""

    task_kind = "growth_research"
    gate = "send"
    section = "growth"
    role = "Growth Agent"

    # -- paths (stdlib only) ---------------------------------------------
    @staticmethod
    def _dept_dir():
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    @staticmethod
    def _ceo_core_dir():
        return os.path.join(
            os.path.dirname(GrowthAgent._dept_dir()), "00-CEO-Core")

    # -- lazy loaders ------------------------------------------------------
    def _load_gateway(self, approvals_path):
        ceo_core = self._ceo_core_dir()
        if ceo_core not in sys.path:
            sys.path.insert(0, ceo_core)
        from human_approval_gateway import ApprovalGateway
        if approvals_path:
            return ApprovalGateway(approvals_path=approvals_path)
        return ApprovalGateway()

    def _get_brain(self, brain):
        if brain is not None:
            return brain
        ceo_core = self._ceo_core_dir()
        if ceo_core not in sys.path:
            sys.path.insert(0, ceo_core)
        from brain import BrainFactory
        return BrainFactory.get_brain("content")

    def _draft(self, prompt, brain):
        """Draft via brain.complete(prompt) — scaffold if there is no brain."""
        llm = brain
        if llm is None:
            try:
                llm = self._get_brain(None)
            except Exception:
                llm = None
        if llm is not None:
            try:
                return llm.complete(prompt)
            except Exception:
                pass
        return ("[MOCK DRAFT — no live model was called. Replace this scaffold "
                "with a real draft before shipping.]\nBrief: " + " ".join(prompt.split())[:400] +
                "\nDraft outline (to be written for real):\n"
                "1. Open on the problem in the viewer's own words.\n"
                "2. One clear idea, shown — not claimed.\n"
                "3. Close with one simple ask.\n[END MOCK DRAFT]")

    # -- gate --------------------------------------------------------------
    def _pending(self, task, gated_action, approval):
        return {
            "status": "pending-approval",
            "type": self.task_kind,
            "task": task.get("title", ""),
            "gated_action": gated_action,
            "approval": approval,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
            "note": "Gated action — PENDING approval recorded. Nothing was "
                    "sent/published/uploaded/spent/deleted. Without Boss's gate word " 
                    "'send', no outreach is sent.",
        }

    def _gate_check(self, task, gateway, approvals_path):
        """If there is a gated action, the draft may not run — hold it as PENDING."""
        gated_action = task.get("gated_action")
        if not gated_action:
            return None
        if gated_action == "upload":
            return {
                "status": "blocked-upload-off",
                "type": self.task_kind,
                "task": task.get("title", ""),
                "gated_action": "upload",
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
                "upload_stage": "OFF by default — needs Boss's 'upload it' + " 
                                "YOUTUBE_UPLOAD_ENABLED=1 + Boss's own " 
                                "YouTube credential",
                "note": "Upload stage 9 is OFF by default. This agent never uploads.",
            }
        gw = gateway if gateway is not None else self._load_gateway(approvals_path)
        approval_id = task.get("approval_id")
        if approval_id:
            try:
                if gw.is_approved(approval_id):
                    return None  # approved — still only a draft, no action executed
            except KeyError:
                pass
        if gated_action in ("send", "publish", "spend", "delete"):
            approval = gw.request(
                gated_action, task.get("title") or self.task_kind, self.role)
            return self._pending(task, gated_action, approval)
        return {
            "status": "pending-approval",
            "type": self.task_kind,
            "task": task.get("title", ""),
            "gated_action": gated_action,
            "approval": None,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
            "note": f"Gate word '{self.gate}' is needed to go ahead — Boss's " 
                    f"approval is pending. For gated action {gated_action!r} " 
                    "no approval record could be made.",
        }

    # -- run ---------------------------------------------------------------
    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Trend-research + collab-outreach DRAFT — standalone, via brain.complete.

        task = {"type": "growth_research", "title": "...",
                "payload": {"niche": ..., "trend": ... (Boss's, if given)},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        DRAFT ONLY — nothing is sent. It writes no file, touches no network,
        and publishes/uploads nothing.
        """
        task = dict(task or {})
        payload = dict(task.get("payload") or {})
        blocked = self._gate_check(task, gateway, approvals_path)
        if blocked is not None:
            return blocked

        prompt = (
            "[GrowthAgent] Trend-research DRAFT + collab-outreach DRAFT for ToolPilot "
            "@ToolPilotai69 (AI Tools & Tutorials, faceless, US viewers). "
            "Week 1 topic: \"Google's Nano Banana 2 Is Free - But Is It Good?\". "
            "Rules: no invented trends — only trends Boss supplies or the mock scaffold; "
            "real trend data needs Boss's input. Outreach drafts are DRAFT ONLY — "
            "sending needs Boss's gate word 'send'. "
            "Never invent clients, stats, testimonials, prices. "
            f"Booking link: {BOOKING_LINK}. Boss's input: {payload}."
        )
        text = self._draft(prompt, brain)
        notes = text + (
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY. No trend was invented "
            "— real trend data needs Boss's input.\n"
            "A collab-outreach draft is only a DRAFT — sending needs Boss's gate word "
            "'send', and Boss sends it himself. No outreach has been "
            "sent yet.")
        return {
            "status": "draft-ready",
            "type": self.task_kind,
            "task": task.get("title", ""),
            "worker": None,
            "worker_status": "standalone-draft",
            "output": text,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
