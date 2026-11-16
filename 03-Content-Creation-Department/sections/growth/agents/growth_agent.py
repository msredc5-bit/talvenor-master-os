"""Growth Agent — growth section (Phase 7, NEW role).

ভূমিকা (role): Trend-research draft + collab-outreach draft বানানো —
ToolPilot channel-এর growth-এর জন্য কোন trend/topic দেখতে হবে, আর কোন
creator/channel-এর সাথে collab-এর জন্য কী লিখতে হবে, তার DRAFT।
Worker: নেই — NEW standalone role, draft logic (brain.complete)।
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers।
Pipeline stage: 1-research-এর growth-ধারা (trend research) — MOCK।
Status: DRAFT ONLY — mock brain ($0), সব output [MOCK DRAFT]।
Gate: "send" — collab-outreach পাঠাতে Boss-এর gate word "send" লাগে;
outreach draft শুধু DRAFT, পাঠানো এই agent-এর কাজ নয়।

সৎ সত্য: কোনো trend invent করা হয় না — mock brain output [MOCK DRAFT]
scaffold; আসল trend data-র জন্য Boss-এর input লাগে। কোনো collab এখনো
হয়নি, কোনো outreach পাঠানো হয়নি।

কখনো করে না: message/email পাঠায় না, publish করে না, upload করে না,
খরচ করে না, delete করে না। Trend / collab / stat invent করে না।
কোনো invented client / testimonial / case study / price লেখে না।
Upload OFF — this agent never uploads।
"""

import os
import sys

# Import time-এ শুধু stdlib। Brain / gateway — সব lazy, run()-এর ভিতরে।

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"


class GrowthAgent:
    """Growth Agent — trend research + collab-outreach draft agent (NEW, standalone)।"""

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
                    "'send' ছাড়া কোনো outreach পাঠানো হয় না।",
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
        """Trend-research + collab-outreach DRAFT — standalone, brain.complete দিয়ে।

        task = {"type": "growth_research", "title": "...",
                "payload": {"niche": ..., "trend": ... (Boss-এর দেওয়া, থাকলে)},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        DRAFT ONLY — কিছু পাঠানো হয় না। কোনো file লেখে না, network ছোঁয় না,
        কিছু publish/upload করে না।
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
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY। কোনো trend invent "
            "করা হয়নি — আসল trend data-র জন্য Boss-এর input লাগে।\n"
            "Collab-outreach draft শুধু DRAFT — পাঠাতে Boss-এর gate word "
            "'send' লাগে, আর পাঠানো Boss নিজে করেন। কোনো outreach এখনো "
            "পাঠানো হয়নি।")
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
