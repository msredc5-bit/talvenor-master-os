"""Content Planner Agent — plan section (Phase 7, Chief-level role).

Role: make a weekly / monthly content plan — what gets posted, when,
in which order, per Boss's real capacity. The Talvenor weekly social plan
(5 posts) and ToolPilot's rhythm (1 long/week + 2 Shorts/week) — both are
this role's work.
Worker: none — Chief-level role, standalone draft logic (brain.complete).
Method source: youtube-skills/yt-plan/SKILL.md + scripts/loop_next.py
(stage 10-next-plan) + pipeline.md.
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers.
Pipeline stage: 0b-plan + 10-next-plan — MOCK.
Status: DRAFT ONLY — mock brain ($0), all output [MOCK DRAFT].
Gate: "ok" — no plan runs without Boss's "ok" or edits.

Honest truth: the Nov 16–22 Talvenor weekly plan (5 posts: Mon Reel, Tue Carousel,
Wed Image, Thu Carousel, Fri LinkedIn) was given 2026-11-15 18:00 —
Boss's "ok" is still pending. No plan is claimed to be approved.

Never does: does not publish, upload, send, spend, or
delete. Does not invent any metric/claim inside a plan.
Upload OFF — this agent never uploads.
"""

import os
import sys

# Only stdlib at import time. Brain / gateway — all lazy, inside run().


class ContentPlannerAgent:
    """Content Planner — weekly plan draft agent (standalone, no worker)."""

    task_kind = "plan_weekly"
    gate = "ok"
    section = "plan"
    role = "Content Planner"

    # -- paths (stdlib only) ---------------------------------------------
    @staticmethod
    def _dept_dir():
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    @staticmethod
    def _ceo_core_dir():
        return os.path.join(
            os.path.dirname(ContentPlannerAgent._dept_dir()), "00-CEO-Core")

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
                    "it will not go ahead.",
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
        """Make a weekly plan DRAFT — standalone, via brain.complete.

        task = {"type": "plan_weekly", "title": "...",
                "payload": {"hours": ..., "niche": ..., ...},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        It writes no file, touches no network, and publishes/uploads nothing.
        """
        task = dict(task or {})
        payload = dict(task.get("payload") or {})
        blocked = self._gate_check(task, gateway, approvals_path)
        if blocked is not None:
            return blocked

        prompt = (
            "[ContentPlanner] Weekly content plan DRAFT for ToolPilot @ToolPilotai69 "
            "(AI Tools & Tutorials, faceless, US viewers) and Talvenor weekly social (5 posts). "
            "Rhythm: 1 long video/week (Sat 10 AM ET = Sat 9 PM Dhaka) + 2 Shorts/week "
            "(Wed + Fri 9 AM ET = 8 PM Dhaka). "
            "Week 1 long video: \"Google's Nano Banana 2 Is Free - But Is It Good?\" — "
            "READY TO RECORD, verdict [FILL AFTER TEST]. "
            "Table columns: pillar + format + platform + posting time. "
            "Rules: never invent clients, stats, testimonials, prices. "
            f"Boss's input: {payload}."
        )
        text = self._draft(prompt, brain)
        notes = text + (
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY. To send/use the output, "
            "Boss's gate word is needed: 'ok'.\n"
            "Honest note: the Nov 16–22 Talvenor weekly plan (5 posts: Mon Reel, Tue Carousel, "
            "Wed Image, Thu Carousel, Fri LinkedIn) was given 2026-11-15 18:00 — "
            "Boss's \"ok\" is still pending. This draft is not approved either.")
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
