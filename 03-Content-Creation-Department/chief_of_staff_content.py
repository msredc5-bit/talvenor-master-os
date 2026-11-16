"""Chief of Staff — Content Creation Department (REAL, Phase 3).

Content Creation Engine = Creator OS — faceless YouTube channel-এর
পুরো ১৩-stage pipeline: niche -> viral concept -> script -> video
build + edit -> upload -> analyze -> improve।

কাজ: Main CEO Bot থেকে আসা task-টা পড়ে ~/workspace/
creator-os-combined/-এর আসল ৬ worker-এর দিকে পাঠানো (MockLLM,
mock brain, $0), ফলাফল DRAFT হিসেবে ফেরত দেওয়া, আর gated কাজ
(send / publish / upload / spend / delete) হলে ApprovalGateway
দিয়ে আটকে রাখা।

নিয়ম (কোডে লেখা):
  - এই Chief কখনো publish করে না, upload করে না, মেইল পাঠায় না,
    খরচ করে না, delete করে না। Publish/Upload শুধু Boss-এর gate
    word ("post it" / "upload it")-এ হয়, আর সেটাও Boss নিজে করেন
    (এই সিস্টেম শুধু DRAFT বানায়)।
  - Upload stage 9 সবসময় OFF by default — `upload_youtube.py`
    চালাতে `--auto-upload` + `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর
    নিজের YouTube credential, তিনটাই লাগে। এই Chief upload script
    কখনো চালায় না।
  - video_produce কখনো video file বানায় না — VisualProducer-এর
    visual plan + ঠিক কী কী input বাকি (footage / voiceover line /
    GPU নাম) সেই list দেয়। `video_file` সবসময় None।
  - Worker-রা MockLLM (mock brain, $0) দিয়ে চলে — ফলাফল
    "[MOCK DRAFT]" লেবেল করা থাকে। Live brain (Muse Spark)
    শুধু Boss-এর আলাদা অনুমোদনে, এখানে নয়। Live-LLM path
    creator-os-এ deliberate ভাবে unwired — এই Chief-ও তা ছোঁয় না।
  - VOICE.md DRAFT — Boss ঠিক না করা পর্যন্ত কোনো script-ই
    "final" নয়। script_write-এর প্রতিটা output-এ এই সতর্কতা থাকে।
  - Captions line-level — word-level karaoke নয় (Creator OS-এর
    সীমা, লুকানো হয় না)।

Routing table: TASK_TYPE -> (worker class, gate word)
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone

# --- paths (REUSED systems — duplicate নয়, শুধু import) ------------------
MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(MASTER_OS_DIR, "00-CEO-Core")
CREATOR_OS_DIR = os.path.expanduser("~/workspace/creator-os-combined")

sys.path.insert(0, CEO_CORE_DIR)
sys.path.insert(0, CREATOR_OS_DIR)

from human_approval_gateway import ApprovalGateway  # noqa: E402
from src.creator_workers import (  # noqa: E402
    CaptionWriter,
    PerformanceTracker,
    PublishPrep,
    ScriptWriter,
    TopicResearcher,
    VisualProducer,
)
from src.workers.base import MockLLM, Task as CreatorTask  # noqa: E402

DEPARTMENT = "content"
BUSINESS = "Content Creation Engine (Creator OS)"
CHANNEL = "ToolPilot @ToolPilotai69"
CREATOR_OS_PATH = "~/workspace/creator-os-combined/"
VOICE_MD = "~/workspace/creator-os-combined/youtube-skills/VOICE.md"
VOICE_STATUS = "DRAFT — Boss must correct before any real script ships"
UPLOAD_STAGE = "OFF by default — needs --auto-upload + YOUTUBE_UPLOAD_ENABLED=1 + owner's own credentials"

# ১৩-stage pipeline (Creator OS README থেকে — 0a..10)
PIPELINE_STAGES = [
    "0a-niche",        # yt-niche niche_score.py — topic না থাকলে চলে, নইলে skip
    "0b-plan",         # yt-plan — weekly plan (loop-এর next-brief.json পড়ে)
    "1-research",      # TopicResearcher — niche + viral concept
    "2a-concept",      # concept_score.py — ৩–৫ concept, ১–১০ score
    "2b-script",       # ScriptWriter + hookscore.py
    "3-visual-pack",   # VisualProducer + title.py (title + thumbnail)
    "4-video",         # Reel Factory — real footage / stills+Ken Burns / GPU / paid API
    "5-edit",          # yt-edit — transcript লাগে, না থাকলে skip
    "6-caption-seo",   # CaptionWriter + yt-seo
    "7-publish-prep",  # PublishPrep ONLY — gate: "post it" / "upload it"
    "8-report",        # PerformanceTracker + yt-retention (post-publish only)
    "9-upload",        # upload_youtube.py — DEFAULT OFF
    "10-next-plan",    # loop_next.py — পরের run-এর brief লেখে
]

# task type -> (worker class, gate word for the OUTPUT's onward use)
# gate word = output পাঠাতে/ব্যবহার করতে Boss-এর যে শব্দ লাগবে।
ROUTING = {
    "content_plan": (TopicResearcher, "ok"),
    "script_write": (ScriptWriter, "ok"),
    "video_produce": (VisualProducer, "ok"),
    "caption_write": (CaptionWriter, "ok"),
    "publish_prep": (PublishPrep, "post it"),
    "performance_track": (PerformanceTracker, "ok"),
}

STORE_DIR = os.path.join(MASTER_OS_DIR, "store")
DEFAULT_TASKS_PATH = os.path.join(STORE_DIR, "tasks.json")
DEFAULT_APPROVALS_PATH = os.path.join(STORE_DIR, "approvals.json")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _log_task(record, tasks_path=None):
    """প্রতিটা routed task store/tasks.json-এ append করে। অন্য
    department-এর entry কখনো মুছে না — read-modify-write।"""
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
    """video_produce-এর জন্য ঠিক কী কী input বাকি — বানানো উত্তর নয়,
    checklist। video file কখনো এখানে বানানো হয় না।"""
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
            "paid video API key — $0 cap-এ এই Chief key চায় না, Boss "
            "নিজে দিলে তবেই।")
    return missing


def handle_task(task, tasks_path=None, approvals_path=None):
    """Main CEO Bot থেকে আসা একটা content task চালানো।

    task = {
      "type": "content_plan" | "script_write" | "video_produce" |
              "caption_write" | "publish_prep" | "performance_track",
      "title": "...",
      "payload": {...},           # worker-কে দেওয়া input
      "gated_action": "send" | "publish" | "upload" | "spend" | "delete" (optional),
      "approval_id": "..." (optional — আগে নেওয়া approval),
      "requested_by": "Main CEO Bot" (optional),
    }

    Returns: {"status": "draft-ready" | "pending-approval" |
              "approved-not-executed" | "blocked-upload-off" |
              "route-only" | "error", ...}
    - gated_action থাকলে worker একদম চালানো হয় না — gateway-এ PENDING
      approval request লেখা হয়, আর এখানেই থেমে যায়।
    - worker চালালেও ফলাফল শুধু DRAFT — publish/upload এই Chief করে না।
    - video_produce-তে video_file সবসময় None + missing_inputs list।
    """
    title = task.get("title", "")
    task_type = task.get("type")
    requested_by = task.get("requested_by", "Main CEO Bot")
    gated_action = task.get("gated_action")
    payload = dict(task.get("payload") or {})

    # 1. Upload চাওয়া হয়েছে — stage 9 OFF, কখনো চালানো হয় না।
    if gated_action == "upload":
        result = {
            "status": "blocked-upload-off",
            "department": DEPARTMENT,
            "task": title,
            "gated_action": gated_action,
            "upload_stage": UPLOAD_STAGE,
            "note": "Upload stage 9 is OFF by default. This Chief never "
                    "runs upload_youtube.py. Boss-এর 'upload it' + "
                    "YOUTUBE_UPLOAD_ENABLED=1 + Boss-এর নিজের YouTube "
                    "credential — তিনটাই লাগে, আর upload Boss নিজে করেন।",
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

    # 2. অন্য gated action — worker চালানো যাবে না, approval-এ আটকাতে হবে।
    if gated_action:
        gateway = ApprovalGateway(approvals_path=approvals_path) if approvals_path else ApprovalGateway()
        approval_id = task.get("approval_id")
        if approval_id and gateway.is_approved(approval_id):
            # অনুমোদন থাকলেও এই Chief send/publish/spend/delete করে না —
            # শুধু জানায় যে Boss অনুমোদন দিয়েছেন, কাজটা Boss নিজে করবেন।
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

    # 3. Type ছাড়া task — শুধু routing probe, worker চলে না।
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

    # 4. অচেনা type — ভুল স্বীকার করে থামা, বানানো worker নয়।
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

    # 5. আসল routing — real Creator OS worker, mock brain ($0)।
    worker_cls, gate_word = ROUTING[task_type]
    llm = MockLLM(seed="master-os-phase3")
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

    note = "DRAFT ONLY — mock brain ($0), [MOCK DRAFT] scaffold। "
    if gate_word:
        note += f"Output পাঠাতে/ব্যবহার করতে Boss-এর gate word লাগবে: '{gate_word}'।"
    else:
        note += "এই draft-এ কোনো gate নেই।"
    if task_type == "script_write":
        note += f" VOICE.md {VOICE_STATUS} — এই script final নয়।"
    if task_type == "video_produce":
        note += " Video file বানানো হয়নি — এই Chief video render করে না।"
    if task_type == "publish_prep":
        note += " ready_to_publish=False — upload stage 9 OFF।"

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
        "mock_revenue_usd": worker_result.mock_revenue_usd,  # MOCK ledger only — real money নয় (সবসময় 0.0)
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
    print("Creator OS:", CREATOR_OS_PATH, "| Channel:", CHANNEL)
    print("Upload stage 9:", UPLOAD_STAGE)
    print("VOICE.md:", VOICE_STATUS)
