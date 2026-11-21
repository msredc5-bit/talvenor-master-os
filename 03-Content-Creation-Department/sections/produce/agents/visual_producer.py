"""Visual Producer Agent — produce section (Phase 7).

Role: make a visual plan — shot list, thumbnail idea, on-screen
text (verbatim, short, readable) + the stage 4-video production plan +
missing-inputs checklist.
Vendored worker: VisualProducer (Chief task video_produce, gate ok).
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers.
Pipeline stage: 3-visual-pack (+ 4-video plan) — MOCK.
Status: DRAFT ONLY — mock brain ($0), all output [MOCK DRAFT].
Gate: "ok" — the visual plan may not be used without Boss's "ok".

⚠️ Stage 4 BLOCKED: this agent does not make a video file — video_file is always
None + a missing-inputs list. No real footage / OBS recording, Boss's PC
GPU name unknown since 2026-11-01, AI video generation is
REGION-BLOCKED here (no retry). If a shot cannot be filmed, that must be said;
it may not be faked.

Never does: does not render video, publish, upload, send,
spend, or delete. Does not write any invented client / stat /
testimonial / price.
Upload OFF — this agent never uploads.
"""

import os
import sys
import uuid

# Only stdlib at import time. Brain / gateway — all lazy, inside run().
# (both departments' vendored trees give a top-level `src` — importing
# src.creator_workers at module level causes a package collision).


def missing_video_inputs(payload):
    """Exactly which inputs are still missing for video_produce — not a made-up answer, a checklist."""
    missing = []
    if not payload.get("footage"):
        missing.append(
            "footage — real footage file (OBS recording / phone clip). "
            "Without it, the video stage only writes a plan, it does not make a video.")
    if not payload.get("voice_lines") and not payload.get("script"):
        missing.append(
            "voiceover lines / script — VOICE.md DRAFT, Boss's " 
            "correction pending; without a script no voiceover line can be written.")
    if payload.get("provider") == "local" and not payload.get("gpu_name"):
        missing.append(
            "Boss's PC GPU name — needed for true AI video motion " 
            "(name unknown since 2026-11-01).")
    if payload.get("provider") == "api" and not payload.get("video_api_key"):
        missing.append(
            "paid video API key — under the $0 cap this agent does not ask for a key; only if Boss " 
            "gives it himself.")
    return missing


class VisualProducerAgent:
    """Visual Producer — visual plan agent for the produce section."""

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
        """Make a visual plan draft — delegates to the vendored VisualProducer worker.

        task = {"type": "video_produce", "title": "...",
                "payload": {"topic": ..., "format": ..., "footage": ...,
                            "voice_lines": ..., "script": ...,
                            "provider": ..., "gpu_name": ...},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        video_file is always None — no video is rendered. It writes no file,
        touches no network, and publishes/uploads nothing.
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
            "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY. To send/use the output, "
            "Boss's gate word is needed: 'ok'.\n"
            "Stage 4 BLOCKED — no video file was made, video_file=None. "
            "Default stills + Ken Burns motion are not real motion.")
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
