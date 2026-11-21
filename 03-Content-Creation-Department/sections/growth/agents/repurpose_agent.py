"""Repurpose Agent — growth section (Phase 7, NEW role).

Role: make a long-video-to-shorts plan DRAFT — which moments of a long video
become Shorts (hook moment, best reveal, funniest fail), each with its
hook + length + caption note.
Worker: none — NEW standalone role, draft logic (brain.complete).
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers.
Pipeline stage: shorts track of 5-edit (yt-edit — shorts) — BLOCKED
(needs a transcript, there is no transcript yet).
Status: DRAFT ONLY — mock brain ($0), all output [MOCK DRAFT].
Gate: "ok" — the plan may not be used without Boss's "ok".

Honest truth: there is no long video yet — Week 1 long video ("Google's Nano
Banana 2 Is Free - But Is It Good?", ~9.5 min, 5 tests) READY TO RECORD,
Boss's OBS recording is pending. So this agent only makes a PLAN — it does not claim any short
was made. Missing-inputs list: source video file/link
+ transcript.

Never does: does not render shorts, edit video, publish,
upload, send, spend, or delete. Does not claim any short was made.
Does not write any invented client / stat / testimonial /
price.
Upload OFF — this agent never uploads.
"""

import os
import sys

# Only stdlib at import time. Brain / gateway — all lazy, inside run().


def missing_repurpose_inputs(payload):
    """Exactly which inputs are still missing for the repurpose plan — not a made-up answer, a checklist."""
    missing = []
    if not payload.get("source_video") and not payload.get("source_link"):
        missing.append(
            "source video file/link — no long video has been recorded yet "
            "(Week 1 long video READY TO RECORD, Boss's OBS recording pending).")
    if not payload.get("transcript"):
        missing.append(
            "transcript — needed for stage 5-edit; without a video there is no transcript.")
    return missing


class RepurposeAgent:
    """Repurpose Agent — long-video-to-shorts plan agent (NEW, standalone)."""

    task_kind = "repurpose_plan"
    gate = "ok"
    section = "growth"
    role = "Repurpose Agent"

    # -- paths (stdlib only) ---------------------------------------------
    @staticmethod
    def _dept_dir():
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    @staticmethod
    def _ceo_core_dir():
        return os.path.join(
            os.path.dirname(RepurposeAgent._dept_dir()), "00-CEO-Core")

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
        """Long-video-to-shorts plan DRAFT — standalone, via brain.complete.

        task = {"type": "repurpose_plan", "title": "...",
                "payload": {"source_video": ..., "source_link": ...,
                            "transcript": ... (if any)},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        PLAN ONLY — no short was made, there is no video_file. It writes no file,
        touches no network, and publishes/uploads nothing.
        """
        task = dict(task or {})
        payload = dict(task.get("payload") or {})
        blocked = self._gate_check(task, gateway, approvals_path)
        if blocked is not None:
            return blocked

        missing = missing_repurpose_inputs(payload)
        prompt = (
            "[RepurposeAgent] Long-video-to-shorts plan DRAFT for ToolPilot @ToolPilotai69. "
            "Source long video: Week 1 \"Google's Nano Banana 2 Is Free - But Is It Good?\" "
            "(~9.5 min, 5 tests). "
            "Honest fact: no long video exists yet — no OBS recording, no transcript — "
            "so this is a PLAN ONLY, no short was made. "
            "Plan: which moments become Shorts (hook moment, best reveal, funniest fail), "
            "each with hook + length + caption note. Never claim a short was made. "
            "Never invent clients, stats, testimonials, prices. "
            f"Boss's input: {payload}."
        )
        text = self._draft(prompt, brain)
        notes = text + (
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY. To send/use the output, "
            "Boss's gate word is needed: 'ok'.\n"
            "PLAN ONLY — no short was made. Missing inputs: "
            + ("; ".join(missing) if missing else "none — source video given."))
        return {
            "status": "draft-ready",
            "type": self.task_kind,
            "task": task.get("title", ""),
            "worker": None,
            "worker_status": "standalone-draft",
            "output": text,
            "notes": notes,
            "missing_inputs": missing,
            "shorts_made": 0,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
