"""Performance Tracker Agent — analyze section (Phase 7).

ভূমিকা (role): Performance report-এর template/setup বানানো — কোন metric
কোথা থেকে নিতে হবে, best/worst comparison, পরের সপ্তাহে একটা change।
Vendored worker: PerformanceTracker (Chief task performance_track, gate ok)।
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers।
Pipeline stage: 8-report (yt-retention — retention CSV পড়ে hook leak খোঁজা) — MOCK।
Status: DRAFT ONLY — mock brain ($0), সব output [MOCK DRAFT]।
Gate: "ok" — Boss-এর "ok" ছাড়া report template ব্যবহার করা যাবে না।

সৎ সত্য: কোনো video এখনো publish হয়নি — metric 0 (subs 0, hours 0,
videos 0)। সংখ্যা কখনো estimate করা হয় না — শুধু Boss-এর পাঠানো আসল
platform সংখ্যা ব্যবহার করা হয়। Performance Analyst-এর থেকে আলাদা:
Tracker setup/template বানায়, Analyst আসল সংখ্যা বিশ্লেষণ করে।

কখনো করে না: publish করে না, upload করে না, send করে না, খরচ করে না,
delete করে না। সংখ্যা invent/estimate করে না।
Upload OFF — this agent never uploads।
"""

import os
import sys
import uuid

# Import time-এ শুধু stdlib। Worker / brain / gateway — সব lazy, run()-এর ভিতরে
# (দুই department-এর vendored tree-ই top-level `src` দেয় — module level-এ
# src.creator_workers import করলে package collision হয়)।


class PerformanceTrackerAgent:
    """Performance Tracker — analyze section-এর report template agent।"""

    task_kind = "performance_track"
    gate = "ok"
    section = "analyze"
    role = "Performance Tracker"

    _WORKER_CLASS_NAME = "PerformanceTracker"

    # -- paths (stdlib only) ---------------------------------------------
    @staticmethod
    def _dept_dir():
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    @staticmethod
    def _workers_dir():
        return os.path.join(PerformanceTrackerAgent._dept_dir(), "engine", "workers")

    @staticmethod
    def _ceo_core_dir():
        return os.path.join(
            os.path.dirname(PerformanceTrackerAgent._dept_dir()), "00-CEO-Core")

    # -- lazy loaders ------------------------------------------------------
    def _load_gateway(self, approvals_path):
        ceo_core = self._ceo_core_dir()
        if ceo_core not in sys.path:
            sys.path.insert(0, ceo_core)
        from human_approval_gateway import ApprovalGateway
        if approvals_path:
            return ApprovalGateway(approvals_path=approvals_path)
        return ApprovalGateway()

    def _load_worker(self):
        workers_dir = self._workers_dir()
        src_pkg = sys.modules.get("src")
        if src_pkg is not None:
            loaded = [os.path.normpath(p)
                      for p in (getattr(src_pkg, "__path__", []) or [])]
            wanted = os.path.normpath(os.path.join(workers_dir, "src"))
            if wanted not in loaded:
                for name in [n for n in list(sys.modules)
                            if n == "src" or n.startswith("src.")]:
                    del sys.modules[name]
        if workers_dir in sys.path:
            sys.path.remove(workers_dir)
        sys.path.insert(0, workers_dir)
        from src.creator_workers import PerformanceTracker
        from src.workers.base import Task as CreatorTask
        return PerformanceTracker, CreatorTask

    def _get_brain(self, brain):
        if brain is not None:
            return brain
        ceo_core = self._ceo_core_dir()
        if ceo_core not in sys.path:
            sys.path.insert(0, ceo_core)
        from brain import BrainFactory
        return BrainFactory.get_brain("content")

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
        """Gated action থাকলে worker চালানো যাবে না — PENDING-এ আটকাও।"""
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
        """Report template DRAFT — vendored PerformanceTracker-কে delegate করে।

        task = {"type": "performance_track", "title": "...",
                "payload": {"topic": ..., "metrics": ... (Boss-এর আসল সংখ্যা, থাকলে)},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        Metrics 0 (কোনো video publish হয়নি) — সংখ্যা estimate করা হয় না।
        কোনো file লেখে না, network ছোঁয় না, কিছু publish/upload করে না।
        """
        task = dict(task or {})
        payload = dict(task.get("payload") or {})
        blocked = self._gate_check(task, gateway, approvals_path)
        if blocked is not None:
            return blocked

        worker_cls, CreatorTask = self._load_worker()
        llm = self._get_brain(brain)
        worker = worker_cls(
            f"content-{worker_cls.__name__}",
            "toolpilot-content",
            "content",
            worker_cls.__name__,
            llm,
        )
        creator_task = CreatorTask(
            task_id=f"content-{uuid.uuid4().hex[:12]}",
            business_id="toolpilot-content",
            division_id="content",
            kind=worker_cls.task_kind,
            payload=dict(getattr(worker_cls, "default_payload", {}) or {}, **payload),
        )
        worker_result = worker.execute(creator_task)

        notes = (worker_result.notes or "") + (
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY। Output পাঠাতে/ব্যবহার "
            "করতে Boss-এর gate word লাগবে: 'ok'।\n"
            "Metrics 0 — কোনো video publish হয়নি (subs 0, hours 0, videos 0)। "
            "সংখ্যা estimate করা হয় না — শুধু Boss-এর পাঠানো আসল platform "
            "সংখ্যা ব্যবহার করা হয়।")
        return {
            "status": "draft-ready",
            "type": self.task_kind,
            "task": task.get("title", ""),
            "worker": worker_cls.__name__,
            "worker_status": worker_result.status,
            "output": worker_result.notes or "",
            "worker_output": worker_result.output,
            "notes": notes,
            "metrics": 0,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
