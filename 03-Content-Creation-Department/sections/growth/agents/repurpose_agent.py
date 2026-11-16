"""Repurpose Agent — growth section (Phase 7, NEW role).

ভূমিকা (role): Long-video-to-shorts plan DRAFT বানানো — একটা long video-র
কোন moment Shorts হবে (hook moment, best reveal, funniest fail), প্রতিটার
hook + length + caption note সহ।
Worker: নেই — NEW standalone role, draft logic (brain.complete)।
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers।
Pipeline stage: 5-edit-এর shorts-ধারা (yt-edit — shorts) — BLOCKED
(transcript লাগে, এখনো কোনো transcript নেই)।
Status: DRAFT ONLY — mock brain ($0), সব output [MOCK DRAFT]।
Gate: "ok" — Boss-এর "ok" ছাড়া plan ব্যবহার করা যাবে না।

সৎ সত্য: কোনো long video এখনো নেই — Week 1 long video ("Google's Nano
Banana 2 Is Free - But Is It Good?", ~৯.৫ min, ৫ test) READY TO RECORD,
Boss-এর OBS recording বাকি। তাই এই agent শুধু PLAN বানায় — কোনো short
বানানো হয়েছে বলে দাবি করে না। Missing-inputs list: source video file/link
+ transcript।

কখনো করে না: short render করে না, video edit করে না, publish করে না,
upload করে না, send করে না, খরচ করে না, delete করে না। কোনো short বানানো
হয়েছে বলে দাবি করে না। কোনো invented client / stat / testimonial / price
লেখে না।
Upload OFF — this agent never uploads।
"""

import os
import sys

# Import time-এ শুধু stdlib। Brain / gateway — সব lazy, run()-এর ভিতরে।


def missing_repurpose_inputs(payload):
    """Repurpose plan-এর জন্য ঠিক কী কী input বাকি — বানানো উত্তর নয়, checklist।"""
    missing = []
    if not payload.get("source_video") and not payload.get("source_link"):
        missing.append(
            "source video file/link — কোনো long video এখনো record হয়নি "
            "(Week 1 long video READY TO RECORD, Boss-এর OBS recording বাকি)।")
    if not payload.get("transcript"):
        missing.append(
            "transcript — stage 5-edit-এর জন্য লাগে; video না হলে transcript আসে না।")
    return missing


class RepurposeAgent:
    """Repurpose Agent — long-video-to-shorts plan agent (NEW, standalone)।"""

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
        """brain.complete(prompt) দিয়ে draft — brain না থাকলে scaffold।"""
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
                    "sent/published/uploaded/spent/deleted. Boss-এর gate word "
                    "ছাড়া এগোবে না।",
        }

    def _gate_check(self, task, gateway, approvals_path):
        """Gated action থাকলে draft চালানো যাবে না — PENDING-এ আটকাও।"""
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
                "upload_stage": "OFF by default — needs Boss-এর 'upload it' + "
                                "YOUTUBE_UPLOAD_ENABLED=1 + Boss-এর নিজের "
                                "YouTube credential",
                "note": "Upload stage 9 is OFF by default. This agent never uploads.",
            }
        gw = gateway if gateway is not None else self._load_gateway(approvals_path)
        approval_id = task.get("approval_id")
        if approval_id:
            try:
                if gw.is_approved(approval_id):
                    return None  # approved — তবুও শুধু draft, action execute নয়
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
            "note": f"Gate word '{self.gate}' ছাড়া এগোবে না — Boss-এর "
                    f"অনুমোদন বাকি। Gated action {gated_action!r}-এর জন্য "
                    "কোনো approval record বানানো যায়নি।",
        }

    # -- run ---------------------------------------------------------------
    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Long-video-to-shorts plan DRAFT — standalone, brain.complete দিয়ে।

        task = {"type": "repurpose_plan", "title": "...",
                "payload": {"source_video": ..., "source_link": ...,
                            "transcript": ... (থাকলে)},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        PLAN ONLY — কোনো short বানানো হয়নি, video_file নেই। কোনো file লেখে না,
        network ছোঁয় না, কিছু publish/upload করে না।
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
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY। Output পাঠাতে/ব্যবহার "
            "করতে Boss-এর gate word লাগবে: 'ok'।\n"
            "PLAN ONLY — কোনো short বানানো হয়নি। Missing inputs: "
            + ("; ".join(missing) if missing else "none — source video দেওয়া হয়েছে।"))
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
