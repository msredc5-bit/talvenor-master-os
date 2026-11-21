"""Performance Tracker Agent — analyze section (Phase 7).

Role: make the performance report's template/setup — which metric
to take from where, best/worst comparison, one change for next week.
Vendored worker: PerformanceTracker (Chief task performance_track, gate ok).
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers.
Pipeline stage: 8-report (yt-retention — reads a retention CSV to find the hook leak) — MOCK.
Status: DRAFT ONLY — mock brain ($0), all output [MOCK DRAFT].
Gate: "ok" — the report template may not be used without Boss's "ok".

Honest truth: no video has been published yet — metrics 0 (subs 0, hours 0,
videos 0). Numbers are never estimated — only Boss's real
platform numbers are used. Different from Performance Analyst:
the Tracker makes the setup/template, the Analyst analyzes the real numbers.

Never does: does not publish, upload, send, spend, or
delete. Does not invent/estimate numbers.
Upload OFF — this agent never uploads.
"""

import os
import sys
import uuid

# Only stdlib at import time. Brain / gateway — all lazy, inside run().
# (both departments' vendored trees give a top-level `src` — importing
# src.creator_workers at module level causes a package collision).


class PerformanceTrackerAgent:
    """Performance Tracker — report template agent for the analyze section."""

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
        """Report template DRAFT — delegates to the vendored PerformanceTracker.

        task = {"type": "performance_track", "title": "...",
                "payload": {"topic": ..., "metrics": ... (Boss's real numbers, if any)},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        Metrics 0 (no video published) — numbers are not estimated.
        It writes no file, touches no network, and publishes/uploads nothing.
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
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY. To send/use the output, "
            "Boss's gate word is needed: 'ok'.\n"
            "Metrics 0 — no video published (subs 0, hours 0, videos 0). "
            "Numbers are not estimated — only Boss's real platform "
            "numbers are used.")
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
