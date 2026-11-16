"""Publish Prep Agent — publish section (Phase 7).

ভূমিকা (role): Post-টা publish-এর জন্য তৈরি করা — final checklist draft:
hook, readable text, কোনো invented claim নেই, platform, best posting time।
Publish করে না — শুধু checklist draft দেয়।
Vendored worker: PublishPrep (Chief task publish_prep, gate "post it")।
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers।
Pipeline stage: 7-publish-prep — MOCK।
Status: DRAFT ONLY — mock brain ($0), সব output [MOCK DRAFT]।
Gate: "post it" (video upload-এর জন্য "upload it") — Boss-এর exact word
ছাড়া কিছু publish/upload হয় না, আর সেটাও Boss নিজে করেন।

সৎ সত্য: ready_to_publish সবসময় False। Upload stage 9 DEFAULT OFF —
লাগে তিনটাই: Boss-এর "upload it" + YOUTUBE_UPLOAD_ENABLED=1 + Boss-এর
নিজের YouTube credential (OAuth)। এই agent কখনো upload_youtube.py চালায় না।
LinkedIn = Boss নিজে post করেন (personal profile)।

কখনো করে না: publish করে না, upload করে না, send করে না, খরচ করে না,
delete করে না। কোনো invented client / stat / testimonial / price লেখে না।
Upload OFF — this agent never uploads।
"""

import os
import sys
import uuid

# Import time-এ শুধু stdlib। Worker / brain / gateway — সব lazy, run()-এর ভিতরে
# (দুই department-এর vendored tree-ই top-level `src` দেয় — module level-এ
# src.creator_workers import করলে package collision হয়)।

UPLOAD_STAGE = ("OFF by default — needs Boss-এর 'upload it' + "
                "YOUTUBE_UPLOAD_ENABLED=1 + Boss-এর নিজের YouTube credential")


class PublishPrepAgent:
    """Publish Prep — publish section-এর checklist draft agent।"""

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
                "upload_stage": UPLOAD_STAGE,
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
        """Publish-prep checklist DRAFT — vendored PublishPrep-কে delegate করে।

        task = {"type": "publish_prep", "title": "...",
                "payload": {"topic": ..., "platform": ...},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        ready_to_publish সবসময় False। কোনো file লেখে না, network ছোঁয় না,
        কিছু publish/upload করে না।
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
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY। Publish করতে Boss-এর "
            "gate word লাগবে: 'post it' (video upload-এর জন্য 'upload it')।\n"
            "ready_to_publish=False — upload stage 9 OFF। এই agent কখনো "
            "upload_youtube.py চালায় না।")
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
