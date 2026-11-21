"""Chief of Staff — Content Creation Department (REAL, Phase 3).

Content Creation Engine = Creator OS — a faceless YouTube channel's
full 13-stage pipeline: niche -> viral concept -> script -> video
build + edit -> upload -> analyze -> improve.

Job: read the task coming from the Main CEO Bot and send it to the
vendored real 6 Creator OS workers inside this office (MockLLM,
mock brain, $0), return the result as a DRAFT, and hold back gated work
(send / publish / upload / spend / delete) — hold it back with
the ApprovalGateway.

Rules (written in code):
  - This Chief never publishes, never uploads, never sends mail,
    never spends, never deletes. Publish/Upload happen only on Boss's gate
    word ("post it" / "upload it"), and even then Boss does it himself
    (this system only makes DRAFTs).
  - Upload stage 9 is always OFF by default — to run `upload_youtube.py`
    you need `--auto-upload` + `YOUTUBE_UPLOAD_ENABLED=1` + Boss's
    own YouTube credential — all three are needed. This Chief never runs
    the upload script.
  - video_produce never makes a video file — it gives VisualProducer's
    visual plan + the list of exactly which inputs are still missing (footage / voiceover line /
    GPU name). `video_file` is always None.
  - Workers run on BrainFactory's brain — if the "brain" flag in config.json is
    "mock" (DEFAULT, $0), the vendored MockLLM,
    labelled "[MOCK DRAFT]"; if "live", the vendored
    MetaSparkProvider. A live brain (Muse Spark) only with Boss's separate
    approval, not here; Phase 6 makes no live calls (see
    00-CEO-Core/brain.py). Content's own LiveLLMProvider is
    deliberately unwired — this Chief does not touch it either.
  - VOICE.md is DRAFT — no script is
    "final" until Boss fixes it. Every script_write output carries this warning.
  - Captions are line-level — not word-level karaoke (a Creator OS
    limit, not hidden).

Routing table: TASK_TYPE -> (worker class, gate word)
"""

import importlib.util
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# --- paths (VENDORED workers — inside the office, no outside dependency) --
MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(MASTER_OS_DIR, "00-CEO-Core")
ENGINE_WORKERS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "engine", "workers")

sys.path.insert(0, CEO_CORE_DIR)
sys.path.insert(0, ENGINE_WORKERS_DIR)

from human_approval_gateway import ApprovalGateway  # noqa: E402
from brain import BrainFactory  # noqa: E402
from src.creator_workers import (  # noqa: E402
    CaptionWriter,
    PerformanceTracker,
    PublishPrep,
    ScriptWriter,
    TopicResearcher,
    VisualProducer,
)
from src.workers.base import Task as CreatorTask  # noqa: E402

DEPARTMENT = "content"
BUSINESS = "Content Creation Engine (Creator OS)"
CHANNEL = "ToolPilot @ToolPilotai69"
VOICE_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VOICE.md")
VOICE_STATUS = "DRAFT — Boss must correct before any real script ships"
UPLOAD_STAGE = "OFF by default — needs --auto-upload + YOUTUBE_UPLOAD_ENABLED=1 + owner's own credentials"

# 13-stage pipeline (from the Creator OS README — 0a..10)
PIPELINE_STAGES = [
    "0a-niche",        # yt-niche niche_score.py — runs when there is no topic, skipped otherwise
    "0b-plan",         # yt-plan — weekly plan (reads the loop's next-brief.json)
    "1-research",      # TopicResearcher — niche + viral concept
    "2a-concept",      # concept_score.py — 3–5 concepts, 1–10 score
    "2b-script",       # ScriptWriter + hookscore.py
    "3-visual-pack",   # VisualProducer + title.py (title + thumbnail)
    "4-video",         # Reel Factory — real footage / stills+Ken Burns / GPU / paid API
    "5-edit",          # yt-edit — needs a transcript, skipped without one
    "6-caption-seo",   # CaptionWriter + yt-seo
    "7-publish-prep",  # PublishPrep ONLY — gate: "post it" / "upload it"
    "8-report",        # PerformanceTracker + yt-retention (post-publish only)
    "9-upload",        # upload_youtube.py — DEFAULT OFF
    "10-next-plan",    # loop_next.py — writes the next run's brief
]

# task type -> (worker class, gate word for the OUTPUT's onward use)
# gate word = the word Boss must give to send/use the output.
ROUTING = {
    "content_plan": (TopicResearcher, "ok"),
    "script_write": (ScriptWriter, "ok"),
    "video_produce": (VisualProducer, "ok"),
    "caption_write": (CaptionWriter, "ok"),
    "publish_prep": (PublishPrep, "post it"),
    "performance_track": (PerformanceTracker, "ok"),
}

# Phase 7 section agents — task type -> (agent file rel. to this dept dir,
# agent class name). Chief-level + NEW roles go here (the ROUTING 6
# have not been changed). Agents are loaded by file path with importlib.
SECTION_ROUTING = {
    "plan_weekly": ("sections/plan/agents/content_planner.py", "ContentPlannerAgent"),
    "performance_analyze": ("sections/analyze/agents/performance_analyst.py", "PerformanceAnalystAgent"),
    "growth_research": ("sections/growth/agents/growth_agent.py", "GrowthAgent"),
    "repurpose_plan": ("sections/growth/agents/repurpose_agent.py", "RepurposeAgent"),
    # Sweep 2026-11-21 — 6 WRAPPED section agents: the ROUTING 6 task types
    # now go through a section agent instead of calling the vendored worker directly.
    # Agents wrap the same vendored worker, so the Chief's
    # outward contract (status / worker / gate / voice_status /
    # video_file / ready_to_publish / note) stay as before —
    # check_phase3.py asserts that.
    "content_plan": ("sections/plan/agents/topic_researcher.py", "TopicResearcherAgent"),
    "script_write": ("sections/produce/agents/script_writer.py", "ScriptWriterAgent"),
    "video_produce": ("sections/produce/agents/visual_producer.py", "VisualProducerAgent"),
    "caption_write": ("sections/publish/agents/caption_writer.py", "CaptionWriterAgent"),
    "publish_prep": ("sections/publish/agents/publish_prep.py", "PublishPrepAgent"),
    "performance_track": ("sections/analyze/agents/performance_tracker.py", "PerformanceTrackerAgent"),
}

STORE_DIR = os.path.join(MASTER_OS_DIR, "store")
DEFAULT_TASKS_PATH = os.path.join(STORE_DIR, "tasks.json")
DEFAULT_APPROVALS_PATH = os.path.join(STORE_DIR, "approvals.json")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _log_task(record, tasks_path=None):
    """Every routed task is appended to store/tasks.json. It never deletes another
    department's entry — read-modify-write."""
    path = tasks_path or DEFAULT_TASKS_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("records", []) if isinstance(data, dict) else []
    except (FileNotFoundError, json.JSONDecodeError):
        records = []
    records.append(record)
    payload = {"schema": "tasks-v1", "records": records}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return record


def missing_video_inputs(payload):
    """Exactly which inputs are still missing for video_produce — not a made-up answer,
    a checklist. A video file is never made here."""
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
            "paid video API key — under the $0 cap this Chief does not ask for a key; only if Boss " 
            "gives it himself.")
    return missing


def handle_task(task, tasks_path=None, approvals_path=None):
    """Run one content task coming from the Main CEO Bot.

    task = {
      "type": "content_plan" | "script_write" | "video_produce" |
              "caption_write" | "publish_prep" | "performance_track",
      "title": "...",
      "payload": {...},           # input given to the worker
      "gated_action": "send" | "publish" | "upload" | "spend" | "delete" (optional),
      "approval_id": "..." (optional — approval taken earlier),
      "requested_by": "Main CEO Bot" (optional),
    }

    Returns: {"status": "draft-ready" | "pending-approval" |
              "approved-not-executed" | "blocked-upload-off" |
              "route-only" | "error", ...}
    - If a gated_action is present, the worker is not run at all — the approval request is
      written to the gateway as PENDING, and it stops here.
    - Even when a worker runs, the result is only a DRAFT — this Chief does not publish/upload.
    - In video_produce, video_file is always None + a missing_inputs list.
    """
    title = task.get("title", "")
    task_type = task.get("type")
    requested_by = task.get("requested_by", "Main CEO Bot")
    gated_action = task.get("gated_action")
    payload = dict(task.get("payload") or {})

    # 1. Upload requested — stage 9 OFF, never run.
    if gated_action == "upload":
        result = {
            "status": "blocked-upload-off",
            "department": DEPARTMENT,
            "task": title,
            "gated_action": gated_action,
            "upload_stage": UPLOAD_STAGE,
            "note": "Upload stage 9 is OFF by default. This Chief never "
                    "runs upload_youtube.py. Boss's 'upload it' + " 
                    "YOUTUBE_UPLOAD_ENABLED=1 + Boss's own YouTube " 
                    "credential — all three are needed, and Boss does the upload himself.",
            "draft_only": True,
        }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": None,
            "status": "blocked-upload-off",
            "gated_action": gated_action,
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 2. Another gated action — the worker may not run, it must be held at approval.
    if gated_action:
        gateway = ApprovalGateway(approvals_path=approvals_path) if approvals_path else ApprovalGateway()
        approval_id = task.get("approval_id")
        if approval_id and gateway.is_approved(approval_id):
            # Even with approval, this Chief does not send/publish/spend/delete —
            # it only says that Boss has approved, and Boss will do the work himself.
            result = {
                "status": "approved-not-executed",
                "department": DEPARTMENT,
                "task": title,
                "gated_action": gated_action,
                "approval_id": approval_id,
                "note": "Boss approved, but this Chief never sends/publishes/uploads/spends/deletes. Boss executes it himself.",
                "draft_only": True,
            }
        else:
            approval = gateway.request(gated_action, title or task_type or "content task", requested_by)
            result = {
                "status": "pending-approval",
                "department": DEPARTMENT,
                "task": title,
                "gated_action": gated_action,
                "approval": approval,
                "note": "Gated action refused — PENDING approval recorded. Nothing was sent/published/uploaded/spent/deleted.",
                "draft_only": True,
            }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": None,
            "status": result["status"],
            "gated_action": gated_action,
            "approval_id": result.get("approval", {}).get("id") or approval_id,
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 3. Task without a type — just a routing probe, no worker runs.
    if not task_type:
        result = {
            "status": "route-only",
            "department": DEPARTMENT,
            "business": BUSINESS,
            "channel": CHANNEL,
            "task": title,
            "note": "No task type given — routing probe only, no worker ran.",
            "routing_keys": sorted(ROUTING),
        }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": None,
            "worker": None,
            "status": "route-only",
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 3b. Phase 7 section agents — plan_weekly / performance_analyze /
    #     growth_research / repurpose_plan — run by loading the agent file from
    #     sections/<section>/agents/ (importlib, by file path). If a gated
    #     action was present it was already held in the block above, so here only drafts.
    if task_type in SECTION_ROUTING:
        agent_rel_path, agent_cls_name = SECTION_ROUTING[task_type]
        agent_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), agent_rel_path)
        spec = importlib.util.spec_from_file_location(
            f"content_section_{task_type}", agent_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        agent = getattr(module, agent_cls_name)()
        llm = BrainFactory.get_brain("content")
        agent_result = agent.run(task, brain=llm, approvals_path=approvals_path)
        result = {
            **agent_result,
            "department": DEPARTMENT,
            "business": BUSINESS,
            "channel": CHANNEL,
            "task": title,
            "type": task_type,
            "agent": agent_cls_name,
        }
        if task_type in ROUTING:
            # WRAPPED agent — keeping the Chief's legacy outward contract:
            # worker = the vendored worker's name, output = the worker's output,
            # note = the agent's notes (with the VOICE.md warning), and by type
            # extra field (voice_status / video_file / ready_to_publish).
            _worker_cls, gate_word = ROUTING[task_type]
            result["worker"] = agent_result.get("worker", _worker_cls.__name__)
            result["worker_status"] = agent_result.get("worker_status")
            result["output"] = agent_result.get(
                "worker_output", agent_result.get("output"))
            result["notes"] = agent_result.get("notes", "")
            result["note"] = agent_result.get("notes", "")
            result["mock_brain"] = agent_result.get("mock_brain", True)
            result["draft_only"] = True
            result["gate"] = gate_word
            if task_type == "script_write":
                result["voice_status"] = agent_result.get(
                    "voice_status", VOICE_STATUS)
            if task_type == "video_produce":
                result["video_file"] = agent_result.get("video_file")
                result["video_built"] = agent_result.get("video_built", False)
                result["missing_inputs"] = agent_result.get(
                    "missing_inputs", missing_video_inputs(payload))
            if task_type == "publish_prep":
                result["ready_to_publish"] = agent_result.get(
                    "ready_to_publish", False)
                result["upload_stage"] = agent_result.get(
                    "upload_stage", UPLOAD_STAGE)
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": agent_cls_name,
            "status": agent_result.get("status"),
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 4. Unknown type — admit the mistake and stop, no made-up worker.
    if task_type not in ROUTING:
        result = {
            "status": "error",
            "department": DEPARTMENT,
            "task": title,
            "type": task_type,
            "error": f"Unknown task type {task_type!r}. Known: {sorted(ROUTING)}",
        }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": None,
            "status": "error",
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 5. Real routing — real Creator OS worker, BrainFactory's brain ($0 mock default).
    worker_cls, gate_word = ROUTING[task_type]
    llm = BrainFactory.get_brain("content")
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

    note = "DRAFT ONLY — mock brain ($0), [MOCK DRAFT] scaffold. "
    if gate_word:
        note += f"To send/use this output you need Boss's gate word: '{gate_word}'." 
    else:
        note += "This draft has no gate."
    if task_type == "script_write":
        note += f" VOICE.md {VOICE_STATUS} — this script is not final."
    if task_type == "video_produce":
        note += "No video file was made — this Chief does not render video."
    if task_type == "publish_prep":
        note += " ready_to_publish=False — upload stage 9 OFF."

    result = {
        "status": "draft-ready",
        "department": DEPARTMENT,
        "business": BUSINESS,
        "channel": CHANNEL,
        "task": title,
        "type": task_type,
        "worker": worker_cls.__name__,
        "worker_status": worker_result.status,
        "output": worker_result.output,
        "notes": worker_result.notes,
        "mock_revenue_usd": worker_result.mock_revenue_usd,  # MOCK ledger only — not real money (always 0.0)
        "mock_brain": True,
        "draft_only": True,
        "gate": gate_word,
        "note": note,
    }
    if task_type == "script_write":
        result["voice_status"] = VOICE_STATUS
    if task_type == "video_produce":
        result["video_file"] = None
        result["video_built"] = False
        result["missing_inputs"] = missing_video_inputs(payload)
    if task_type == "publish_prep":
        result["ready_to_publish"] = False
        result["upload_stage"] = UPLOAD_STAGE
    _log_task({
        "id": uuid.uuid4().hex[:12],
        "department": DEPARTMENT,
        "title": title,
        "type": task_type,
        "worker": worker_cls.__name__,
        "status": "draft-ready",
        "logged_at": _now_iso(),
    }, tasks_path=tasks_path)
    return result


if __name__ == "__main__":
    print("Content Chief of Staff — REAL (Phase 3). Pipeline:", " -> ".join(PIPELINE_STAGES))
    print("Routed task types:", ", ".join(sorted(ROUTING)))
    print("Creator OS (vendored):", ENGINE_WORKERS_DIR, "| Channel:", CHANNEL)
    print("Upload stage 9:", UPLOAD_STAGE)
    print("VOICE.md:", VOICE_STATUS)
