"""Publish Prep Agent — publish section (Phase 7).

Role: prepare a post for publishing — final checklist draft:
hook, readable text, no invented claim, platform, best posting time.
It does not publish — it only gives a checklist draft.
Vendored worker: PublishPrep (Chief task publish_prep, gate "post it").
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers.
Pipeline stage: 7-publish-prep — MOCK.
Status: DRAFT ONLY — mock brain ($0), all output [MOCK DRAFT].
Gate: "post it" (for video upload, "upload it") — without Boss's exact word
nothing is published/uploaded, and Boss does that himself.

Honest truth: ready_to_publish is always False. Upload stage 9 is DEFAULT OFF —
all three are needed: Boss's "upload it" + YOUTUBE_UPLOAD_ENABLED=1 + Boss's
own YouTube credential (OAuth). This agent never runs upload_youtube.py.
LinkedIn = Boss posts himself (personal profile).

Never does: does not publish, upload, send, spend, or
delete. Does not write any invented client / stat / testimonial / price.
Upload OFF — this agent never uploads.
"""

import os
import sys
import uuid

# Only stdlib at import time. Brain / gateway — all lazy, inside run().
# (both departments' vendored trees give a top-level `src` — importing
# src.creator_workers at module level causes a package collision).

UPLOAD_STAGE = ("OFF by default — needs Boss's 'upload it' + "
                "YOUTUBE_UPLOAD_ENABLED=1 + Boss's own YouTube credential")


class PublishPrepAgent:
    """Publish Prep — checklist draft agent for the publish section."""

    task_kind = "publish_prep"
    gate = "post it"
    section = "publish"
    role = "Publish Prep"

    _WORKER_CLASS_NAME = "PublishPrep"

    # -- paths (stdlib only) ---------------------------------------------
    @staticmethod
    def _dept_dir():
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    @staticmethod
    def _workers_dir():
        return os.path.join(PublishPrepAgent._dept_dir(), "engine", "workers")

    @staticmethod
    def _ceo_core_dir():
        return os.path.join(
            os.path.dirname(PublishPrepAgent._dept_dir()), "00-CEO-Core")

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
        from src.creator_workers import PublishPrep
        from src.workers.base import Task as CreatorTask
        return PublishPrep, CreatorTask

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
                "upload_stage": UPLOAD_STAGE,
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
        """Publish-prep checklist DRAFT — delegates to the vendored PublishPrep.

        task = {"type": "publish_prep", "title": "...",
                "payload": {"topic": ..., "platform": ...},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        ready_to_publish is always False. It writes no file, touches no network,
        and publishes/uploads nothing.
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
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY. To publish, Boss's "
            "gate word is needed: 'post it' (for video upload, 'upload it').\n"
            "ready_to_publish=False — upload stage 9 OFF. This agent never "
            "runs upload_youtube.py.")
        return {
            "status": "draft-ready",
            "type": self.task_kind,
            "task": task.get("title", ""),
            "worker": worker_cls.__name__,
            "worker_status": worker_result.status,
            "output": worker_result.notes or "",
            "worker_output": worker_result.output,
            "notes": notes,
            "ready_to_publish": False,
            "upload_stage": UPLOAD_STAGE,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
