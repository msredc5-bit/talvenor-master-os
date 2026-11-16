"""Visual Producer Agent — produce section (Phase 7).

ভূমিকা (role): Visual plan বানানো — shot list, thumbnail idea, on-screen
text (verbatim, ছোট, readable) + stage 4-video-র production plan +
missing-inputs checklist।
Vendored worker: VisualProducer (Chief task video_produce, gate ok)।
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers।
Pipeline stage: 3-visual-pack (+ 4-video plan) — MOCK।
Status: DRAFT ONLY — mock brain ($0), সব output [MOCK DRAFT]।
Gate: "ok" — Boss-এর "ok" ছাড়া visual plan ব্যবহার করা যাবে না।

⚠️ Stage 4 BLOCKED: এই agent video file বানায় না — video_file সবসময়
None + missing-inputs list। Real footage / OBS recording নেই, Boss-এর PC
GPU-র নাম 2026-11-01 থেকে জানা যায়নি, AI video generation এখানে
REGION-BLOCKED (retry করা হয় না)। কোনো shot film করা না গেলে সেটা বলতে
হয়, fake করা যাবে না।

কখনো করে না: video render করে না, publish করে না, upload করে না, send
করে না, খরচ করে না, delete করে না। কোনো invented client / stat /
testimonial / price লেখে না।
Upload OFF — this agent never uploads।
"""

import os
import sys
import uuid

# Import time-এ শুধু stdlib। Worker / brain / gateway — সব lazy, run()-এর ভিতরে
# (দুই department-এর vendored tree-ই top-level `src` দেয় — module level-এ
# src.creator_workers import করলে package collision হয়)।


def missing_video_inputs(payload):
    """video_produce-এর জন্য ঠিক কী কী input বাকি — বানানো উত্তর নয়, checklist।"""
    missing = []
    if not payload.get("footage"):
        missing.append(
            "footage — real footage file (OBS recording / phone clip). "
            "না থাকলে video stage শুধু plan লেখে, video বানায় না।")
    if not payload.get("voice_lines") and not payload.get("script"):
        missing.append(
            "voiceover lines / script — VOICE.md DRAFT, Boss-এর "
            "correction বাকি; script ছাড়া voiceover line লেখা যায় না।")
    if payload.get("provider") == "local" and not payload.get("gpu_name"):
        missing.append(
            "Boss-এর PC GPU নাম — true AI video motion-এর জন্য লাগে "
            "(নাম 2026-11-01 থেকে জানা যায়নি)।")
    if payload.get("provider") == "api" and not payload.get("video_api_key"):
        missing.append(
            "paid video API key — $0 cap-এ এই agent key চায় না, Boss "
            "নিজে দিলে তবেই।")
    return missing


class VisualProducerAgent:
    """Visual Producer — produce section-এর visual plan agent।"""

    task_kind = "video_produce"
    gate = "ok"
    section = "produce"
    role = "Visual Producer"

    _WORKER_CLASS_NAME = "VisualProducer"

    # -- paths (stdlib only) ---------------------------------------------
    @staticmethod
    def _dept_dir():
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    @staticmethod
    def _workers_dir():
        return os.path.join(VisualProducerAgent._dept_dir(), "engine", "workers")

    @staticmethod
    def _ceo_core_dir():
        return os.path.join(
            os.path.dirname(VisualProducerAgent._dept_dir()), "00-CEO-Core")

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
        from src.creator_workers import VisualProducer
        from src.workers.base import Task as CreatorTask
        return VisualProducer, CreatorTask

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
        """Visual plan draft বানানো — vendored VisualProducer worker-কে delegate করে।

        task = {"type": "video_produce", "title": "...",
                "payload": {"topic": ..., "format": ..., "footage": ...,
                            "voice_lines": ..., "script": ...,
                            "provider": ..., "gpu_name": ...},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        video_file সবসময় None — video render করা হয় না। কোনো file লেখে না,
        network ছোঁয় না, কিছু publish/upload করে না।
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

        missing = missing_video_inputs(payload)
        notes = (worker_result.notes or "") + (
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY। Output পাঠাতে/ব্যবহার "
            "করতে Boss-এর gate word লাগবে: 'ok'।\n"
            "Stage 4 BLOCKED — video file বানানো হয়নি, video_file=None। "
            "Default stills + Ken Burns motion = সত্যিকারের motion নয়।")
        return {
            "status": "draft-ready",
            "type": self.task_kind,
            "task": task.get("title", ""),
            "worker": worker_cls.__name__,
            "worker_status": worker_result.status,
            "output": worker_result.notes or "",
            "worker_output": worker_result.output,
            "notes": notes,
            "video_file": None,
            "video_built": False,
            "missing_inputs": missing,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
