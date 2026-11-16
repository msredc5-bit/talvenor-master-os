"""Performance Analyst Agent — analyze section (Phase 7, Chief-level role).

ভূমিকা (role): Publish হওয়া content-এর আসল performance বিশ্লেষণ করা —
Boss-এর পাঠানো আসল metric (views, retention, CTR, subs) পড়ে কোথায়
viewer ছাড়ে, কেন ছাড়ে, আর পরের video-তে ঠিক কী বদলাতে হবে, সেটা লেখা।
Worker: নেই — Chief-level role, standalone draft logic (brain.complete)।
Method-এর source: youtube-skills/yt-retention/SKILL.md (retention graph —
hook leak, প্রথম ৩০ সেকেন্ডে ২৫%-এর নিচে healthy) + youtube-skills/yt-audit/
+ PerformanceTracker-এর template + pipeline.md stage 8-report।
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers।
Pipeline stage: 8-report (analysis) — MOCK।
Status: DRAFT ONLY — mock brain ($0), সব output [MOCK DRAFT]।
Gate: "ok" — analysis Boss-কে দেখানো হয়, Boss সিদ্ধান্ত নেন।

সৎ সত্য: কোনো video এখনো publish হয়নি, তাই বিশ্লেষণ করার মতো আসল
metric 0 — Boss metric না পাঠালে এই agent শুধু "no metrics yet — Boss's
numbers needed" বলে থামে। সংখ্যা ছাড়া analysis লেখা হয় না।
Performance Tracker-এর থেকে আলাদা: Tracker tracking-এর setup/template
বানায়, Analyst আসল সংখ্যা থেকে সিদ্ধান্ত বের করে।

কখনো করে না: publish করে না, upload করে না, send করে না, খরচ করে না,
delete করে না। সংখ্যা invent/estimate করে না।
Upload OFF — this agent never uploads।
"""

import os
import sys

# Import time-এ শুধু stdlib। Brain / gateway — সব lazy, run()-এর ভিতরে।


class PerformanceAnalystAgent:
    """Performance Analyst — আসল সংখ্যার বিশ্লেষণ agent (standalone, no worker)।"""

    task_kind = "performance_analyze"
    gate = "ok"
    section = "analyze"
    role = "Performance Analyst"

    # -- paths (stdlib only) ---------------------------------------------
    @staticmethod
    def _dept_dir():
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    @staticmethod
    def _ceo_core_dir():
        return os.path.join(
            os.path.dirname(PerformanceAnalystAgent._dept_dir()), "00-CEO-Core")

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
        """আসল সংখ্যার analysis DRAFT — শুধু Boss-এর পাঠানো metric দিয়ে।

        task = {"type": "performance_analyze", "title": "...",
                "payload": {"metrics": {...} | "platform_numbers": {...} |
                            "retention_csv": ... (Boss-এর আসল সংখ্যা)},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        Metric না থাকলে "no metrics yet — Boss's numbers needed" বলে থামে —
        analysis invent করা হয় না। কোনো file লেখে না, network ছোঁয় না,
        কিছু publish/upload করে না।
        """
        task = dict(task or {})
        payload = dict(task.get("payload") or {})
        blocked = self._gate_check(task, gateway, approvals_path)
        if blocked is not None:
            return blocked

        metrics = (payload.get("metrics") or payload.get("platform_numbers")
                   or payload.get("numbers") or payload.get("retention_csv"))
        if not metrics:
            message = "no metrics yet — Boss's numbers needed"
            return {
                "status": "waiting-for-metrics",
                "type": self.task_kind,
                "task": task.get("title", ""),
                "worker": None,
                "worker_status": "waiting-for-metrics",
                "output": message,
                "notes": (message + " — কোনো video এখনো publish হয়নি "
                          "(subs 0, hours 0, videos 0), তাই বিশ্লেষণ করার "
                          "মতো আসল metric 0। Boss YouTube Studio export / "
                          "retention CSV / platform সংখ্যা পাঠালে তবেই analysis "
                          "লেখা হবে। সংখ্যা ছাড়া analysis লেখা হয় না।"),
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        prompt = (
            "[PerformanceAnalyst] Analyze ONLY these real platform numbers sent by Boss: "
            f"{metrics}. No other numbers exist — ToolPilot videos published: 0, subs 0, "
            "watch hours 0. Find where viewers drop off (retention graph — hook leak, "
            "প্রথম ৩০ সেকেন্ডে ২৫%-এর নিচে healthy), why, and one concrete change for "
            "next week. Never invent or estimate numbers. "
            "Never invent clients, stats, testimonials, prices."
        )
        text = self._draft(prompt, brain)
        notes = text + (
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY। Analysis Boss-কে "
            "দেখানো হয়, সিদ্ধান্ত Boss নেন (gate 'ok')। শুধু Boss-এর পাঠানো "
            "আসল সংখ্যা ব্যবহার করা হয়েছে — কিছু estimate করা হয়নি।")
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
