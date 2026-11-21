"""Performance Analyst Agent — analyze section (Phase 7, Chief-level role).

Role: analyze the real performance of published content —
read Boss's real metrics (views, retention, CTR, subs) and write where
viewers drop off, why they drop off, and exactly what to change in the next video.
Worker: none — Chief-level role, standalone draft logic (brain.complete).
Method source: youtube-skills/yt-retention/SKILL.md (retention graph —
hook leak, below 25% in the first 30 seconds is healthy) + youtube-skills/yt-audit/
+ PerformanceTracker's template + pipeline.md stage 8-report.
Channel: ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers.
Pipeline stage: 8-report (analysis) — MOCK.
Status: DRAFT ONLY — mock brain ($0), all output [MOCK DRAFT].
Gate: "ok" — the analysis is shown to Boss, Boss decides.

Honest truth: no video has been published yet, so there is no real
metric to analyze — if Boss does not send metrics, this agent just says "no metrics yet — Boss's
numbers needed" and stops. No analysis is written without numbers.
Different from Performance Tracker: the Tracker makes the tracking setup/template,
the Analyst draws decisions from the real numbers.

Never does: does not publish, upload, send, spend, or
delete. Does not invent/estimate numbers.
Upload OFF — this agent never uploads.
"""

import csv
import json
import os
import sys

# Deterministic metrics parser (sweep 2026-11-21, stage 8-report).
# Stdlib only — reads Boss-pasted numbers from a CSV/JSON file (or a
# list of dicts) and computes best/worst + ONE concrete change with plain
# arithmetic. Numbers are NEVER estimated or invented: a missing column
# is reported as missing, not filled in.
#
# CSV columns (case-insensitive, any subset): video/title, views,
# retention_30s (%), retention_avg (%), retention_end (%), ctr (%),
# subs_gained. JSON: a list of such dicts, or {"videos": [...]}.
# Hook leak rule (yt-retention skill): retention in the first 30 seconds
# under 25% is healthy-or-not — under 25% = hook leak, fix the first 15
# seconds first, never the edit.

HOOK_LEAK_THRESHOLD_PCT = 25.0

_METRIC_ALIASES = {
    "video": ("video", "title", "name"),
    "views": ("views", "view_count"),
    "retention_30s": ("retention_30s", "retention_30", "retention_first_30s"),
    "retention_avg": ("retention_avg", "avg_retention", "retention"),
    "retention_end": ("retention_end", "retention_last"),
    "ctr": ("ctr", "click_through_rate", "click-through-rate"),
    "subs": ("subs", "subs_gained", "subscribers_gained", "subscribers"),
}


def _to_float(value):
    """'1,234' / '12.5%' / 12.5 -> float; anything else -> None (never 0)."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").rstrip("%").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _normalize_row(raw):
    """One raw row -> normalized dict with only the metrics the row
    actually carried (missing stays missing)."""
    lowered = {(str(k).strip().lower()): v for k, v in dict(raw).items()}
    row = {}
    for field, aliases in _METRIC_ALIASES.items():
        for alias in aliases:
            if alias in lowered:
                row[field] = lowered[alias]
                break
    out = {"video": str(row.get("video") or "").strip() or "(unnamed video)"}
    for field in ("views", "retention_30s", "retention_avg",
                  "retention_end", "ctr", "subs"):
        value = _to_float(row.get(field))
        if value is not None:
            out[field] = value
    return out


def parse_metrics_file(path):
    """Read a metrics file (CSV or JSON) -> list of normalized rows.
    Raises ValueError on unreadable/empty input — never returns fake rows."""
    if not os.path.isfile(path):
        raise ValueError(f"metrics file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    if not raw.strip():
        raise ValueError(f"metrics file is empty: {path}")
    rows = None
    if path.lower().endswith(".json"):
        data = json.loads(raw)
        if isinstance(data, dict):
            data = data.get("videos", data.get("rows", []))
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected a JSON list of video rows")
        rows = [_normalize_row(r) for r in data if isinstance(r, dict)]
    else:
        import io
        reader = csv.DictReader(io.StringIO(raw))
        if reader.fieldnames is None:
            raise ValueError(f"{path}: no header row found (CSV expected)")
        rows = [_normalize_row(r) for r in reader]
    rows = [r for r in rows if r.get("views") is not None or len(r) > 1]
    if not rows:
        raise ValueError(f"{path}: no usable video rows found")
    return rows


def analyze_metrics(rows):
    """Deterministic analysis of parsed rows -> dict with best/worst +
    ONE concrete change. Only arithmetic on the supplied numbers."""
    rows = [dict(r) for r in rows]
    result = {"videos": len(rows), "source": "boss-supplied numbers only"}
    for field in ("views", "retention_avg", "ctr", "subs"):
        scored = [r for r in rows if r.get(field) is not None]
        if not scored:
            result[f"best_{field}"] = None
            result[f"worst_{field}"] = None
            continue
        best = max(scored, key=lambda r: r[field])
        worst = min(scored, key=lambda r: r[field])
        result[f"best_{field}"] = {"video": best["video"], field: best[field]}
        result[f"worst_{field}"] = {"video": worst["video"], field: worst[field]}
    hook_leaks = [r for r in rows
                  if r.get("retention_30s") is not None
                  and r["retention_30s"] < HOOK_LEAK_THRESHOLD_PCT]
    result["hook_leaks"] = [
        {"video": r["video"], "retention_30s": r["retention_30s"]}
        for r in hook_leaks]
    # ONE concrete change — fixed precedence, no guessing:
    if hook_leaks:
        worst_leak = min(hook_leaks, key=lambda r: r["retention_30s"])
        result["one_change"] = (
            f"Hook leak — '{worst_leak['video']}' keeps only "
            f"{worst_leak['retention_30s']}% at 30s (under 25% is the leak "
            "line). Fix the first 15 seconds only: confirm the title's "
            "promise in the first sentence + open one question the viewer "
            "cannot close. Do not re-edit the middle first.")
    elif result.get("worst_ctr") and result.get("best_ctr") \
            and result["worst_ctr"]["ctr"] < 2.0 \
            and result["best_ctr"]["ctr"] > result["worst_ctr"]["ctr"] * 1.5:
        result["one_change"] = (
            f"Packaging, not the video — '{result['worst_ctr']['video']}' "
            f"CTR is {result['worst_ctr']['ctr']}% vs best "
            f"{result['best_ctr']['ctr']}%. Re-title + re-thumbnail that "
            "one video (title.py lint + thumbnail must not repeat the "
            "title); do not re-shoot it.")
    else:
        slides = [r for r in rows
                  if r.get("retention_30s") is not None
                  and r.get("retention_end") is not None
                  and r["retention_end"] < r["retention_30s"] - 15]
        if slides:
            worst_slide = min(
                slides,
                key=lambda r: r["retention_end"] - r["retention_30s"])
            result["one_change"] = (
                f"Steady slide — '{worst_slide['video']}' falls from "
                f"{worst_slide['retention_30s']}% (30s) to "
                f"{worst_slide['retention_end']}% (end). The fix is "
                "cutting, not rewriting: cut the middle dead air + filler "
                "(cut_list.py) and re-check retention.")
        else:
            result["one_change"] = (
                "No single leak stands out in the supplied numbers — the "
                "video is fine on retention, so the problem is packaging: "
                "send the worst-CTR video to the yt-package skill "
                "(title + thumbnail) before changing the script.")
    return result


def format_report(analysis):
    """Analysis dict -> human-readable report text (numbers quoted, none invented)."""
    lines = ["Performance report — from Boss's real numbers (nothing estimated):",
             f"  Videos: {analysis['videos']}"]
    for field, label in (("views", "Views"), ("retention_avg", "Avg retention %"),
                         ("ctr", "CTR %"), ("subs", "Subs gained")):
        best = analysis.get(f"best_{field}")
        worst = analysis.get(f"worst_{field}")
        if best and worst:
            lines.append(f"  Best {label}: {best['video']} ({best[field]})")
            lines.append(f"  Worst {label}: {worst['video']} ({worst[field]})")
        else:
            lines.append(f"  {label}: (column not in the supplied file — not estimated)")
    if analysis.get("hook_leaks"):
        lines.append("  Hook leaks (<25% at 30s): " + ", ".join(
            f"{h['video']} ({h['retention_30s']}%)" for h in analysis["hook_leaks"]))
    lines.append("")
    lines.append("  ONE concrete change for next week:")
    lines.append("  " + analysis["one_change"])
    return "\n".join(lines)

# Only stdlib at import time. Brain / gateway — all lazy, inside run().


class PerformanceAnalystAgent:
    """Performance Analyst — real-numbers analysis agent (standalone, no worker)."""

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
        """Draft via brain.complete(prompt) — scaffold if there is no brain."""
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
        """Analysis DRAFT from the real numbers — only with Boss's metrics.

        task = {"type": "performance_analyze", "title": "...",
                "payload": {"metrics": {...} | "platform_numbers": {...} |
                            "retention_csv": ... (Boss's real numbers)},
                "gated_action": ... (optional), "approval_id": ... (optional)}
        Without metrics it stops with "no metrics yet — Boss's numbers needed" —
        no analysis is invented. It writes no file, touches no network,
        and publishes/uploads nothing.
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
                "notes": (message + " — no video has been published yet "
                          "(subs 0, hours 0, videos 0), so there is no real "
                          "metric to analyze. Only when Boss sends a YouTube Studio export / "
                          "retention CSV / platform numbers will an analysis "
                          "be written. No analysis is written without numbers."),
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        # Deterministic path (sweep 2026-11-21): when Boss's numbers arrive as a file or
        # list, a parser derives best/worst + one concrete change
        # — no estimate, only arithmetic.
        metrics_file = None
        metrics_rows = None
        if isinstance(metrics, str) and os.path.isfile(metrics):
            metrics_file = metrics
        elif isinstance(metrics, dict):
            metrics_file = (metrics.get("metrics_file")
                            or metrics.get("file") or metrics.get("path"))
            if isinstance(metrics.get("videos"), list):
                metrics_rows = metrics["videos"]
            elif isinstance(metrics.get("rows"), list):
                metrics_rows = metrics["rows"]
        elif isinstance(metrics, list):
            metrics_rows = metrics
        if metrics_file or metrics_rows is not None:
            try:
                rows = (parse_metrics_file(metrics_file) if metrics_file
                        else [_normalize_row(r) for r in metrics_rows
                              if isinstance(r, dict)])
                if not rows:
                    raise ValueError("no usable video rows in the supplied metrics")
                analysis = analyze_metrics(rows)
                text = format_report(analysis)
                return {
                    "status": "draft-ready",
                    "type": self.task_kind,
                    "task": task.get("title", ""),
                    "worker": None,
                    "worker_status": "deterministic-parser",
                    "output": text,
                    "notes": (text + "\n[MOCK DRAFT] — deterministic parser "
                               "(stdlib CSV/JSON, $0). Only Boss's sent "
                               "real numbers were used — nothing was estimated. "
                               "The analysis is shown to Boss, "
                               "Boss decides (gate 'ok')."),
                    "analysis": analysis,
                    "draft_only": True,
                    "mock_brain": True,
                    "gate": self.gate,
                }
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                return {
                    "status": "error",
                    "type": self.task_kind,
                    "task": task.get("title", ""),
                    "worker": None,
                    "worker_status": "error",
                    "output": "",
                    "notes": ("Metrics file could not be read — no analysis "
                               f"was written: {exc}"),
                    "error": str(exc),
                    "draft_only": True,
                    "mock_brain": True,
                    "gate": self.gate,
                }

        prompt = (
            "[PerformanceAnalyst] Analyze ONLY these real platform numbers sent by Boss: "
            f"{metrics}. No other numbers exist — ToolPilot videos published: 0, subs 0, "
            "watch hours 0. Find where viewers drop off (retention graph — hook leak, "
             "below 25% in the first 30 seconds is healthy), why, and one concrete change for "
            "next week. Never invent or estimate numbers. "
            "Never invent clients, stats, testimonials, prices."
        )
        text = self._draft(prompt, brain)
        notes = text + (
             "\n[MOCK DRAFT] — mock brain ($0), DRAFT ONLY. The analysis is shown to Boss, "
             "Boss decides (gate 'ok'). Only Boss's sent "
             "real numbers were used — nothing was estimated.")
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


if __name__ == "__main__":
    # Self-test — deterministic parser only, TEMP files, no live data.
    import tempfile

    sample_rows = [
        {"video": "Nano Banana 2 test", "views": 1200,
         "retention_30s": 18, "retention_avg": 42, "retention_end": 30,
         "ctr": 4.1, "subs": 12},
        {"video": "AI news roundup", "views": 300,
         "retention_30s": 31, "retention_avg": 38, "retention_end": 22,
         "ctr": 1.4, "subs": 1},
    ]
    analysis = analyze_metrics(sample_rows)
    assert analysis["best_views"]["video"] == "Nano Banana 2 test", analysis
    assert analysis["worst_views"]["video"] == "AI news roundup", analysis
    assert len(analysis["hook_leaks"]) == 1, analysis
    assert "Hook leak" in analysis["one_change"], analysis
    print("in-memory rows: best/worst + hook leak + one change OK")

    tmp = tempfile.mkdtemp()
    csv_path = os.path.join(tmp, "metrics.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["video", "views", "retention_30s",
                           "retention_avg", "retention_end", "ctr", "subs"])
        writer.writeheader()
        writer.writerows(sample_rows)
    parsed = parse_metrics_file(csv_path)
    assert len(parsed) == 2 and parsed[0]["views"] == 1200.0, parsed
    print("CSV parse: 2 rows OK")

    agent = PerformanceAnalystAgent()
    result = agent.run(
        {"type": "performance_analyze", "title": "self-test",
         "payload": {"metrics": csv_path}})
    assert result["status"] == "draft-ready", result
    assert result["worker_status"] == "deterministic-parser", result
    assert "Hook leak" in result["output"], result
    print("agent.run(metrics file): draft-ready, deterministic-parser OK")
    empty = agent.run({"type": "performance_analyze", "title": "self-test",
                       "payload": {}})
    assert empty["status"] == "waiting-for-metrics", empty
    print("agent.run(no metrics): waiting-for-metrics OK")
    print("performance_analyst: OK")
