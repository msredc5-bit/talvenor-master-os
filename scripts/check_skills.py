#!/usr/bin/env python3
"""check_skills.py — Phase 2 (local-first) self-check for skills + Chief hook.

What it checks (offline ONLY — no network, no live call, ever; mock
brain only, $0):
  1. Skill counts: 112 real skills (index == local registry == doctor).
  2. Frontmatter format on all 112 (validate_skill_frontmatter /
     validate_index — read-only, no writes needed).
  3. Progressive disclosure: index entries carry ONLY
     name/description/path/version; find_skills returns index-only
     entries; load_skill_for_task loads the full text of the top match
     only.
  4. Finder locates the right skill ("backup" -> backup-recovery-agent;
     "kit builder" -> kit-builder, ambiguous, exactly 2 candidates;
     "xyznoskill" -> no matches, loaded None).
  5. Runtime loads AND executes the correct skill for a Chief-routed
     task end-to-end on the mock path (caption_write -> draft-ready AND
     result["skill"]["name"] == "caption-writer", Agency engine copy).
  6. Gated tasks return BEFORE any skill work (no "skill" key).
  7. A department manager runs with the skill name/path as advisory
     context and ignores the unknown key.
  8. Duplicates resolved: kit-qa and script-writer have 1 index entry
     each (engine copy); the 5 pointer files are excluded from the index.
  9. Broken references: every skill path in the index resolves to an
     existing file; every pointer target exists.
 10. Execution-log recording + temp-skill validation — WRITE-DEPENDENT:
     each first probes writability (tempfile.mkdtemp()); if it raises,
     the check is recorded SKIP with reason "environment write block",
     never failed.
 11. Chief real-path call (real temp tasks path): attempted as well;
     if the write fails it is recorded [BLOCKED] with the exact error.
 12. Real store unchanged by this check run (the execution log is
     redirected to os.devnull for the read-only checks, so the real
     logs/skill_executions.jsonl is never touched).

Stdlib only. Run: python3 scripts/check_skills.py
"""

import json
import os
import sys
import tempfile
import warnings

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)
sys.path.insert(0, os.path.join(BASE, "01-Agency-Department"))

results = []  # (name, status, detail); status in PASS / FAIL / SKIP / BLOCKED


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def skip(name, reason):
    results.append((name, "SKIP", reason))
    print(f"[SKIP] {name} — {reason}")


def blocked(name, reason):
    results.append((name, "BLOCKED", reason))
    print(f"[BLOCKED] {name} — {reason}")


def _snapshot_store():
    """Snapshot of the real store — this check's only job is to prove
    this run did not change it."""
    snap = {}
    for name in ("store/tasks.json", "store/approvals.json"):
        try:
            with open(os.path.join(BASE, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    return snap


def _probe_writable():
    """True when a temp dir can be created; False + the exact error
    when the environment write block is active. Never raises."""
    try:
        d = tempfile.mkdtemp()
    except Exception as e:  # noqa: BLE001 - the probe IS the check
        return False, f"{type(e).__name__}: {e}"
    return True, d


def main():
    store_before = _snapshot_store()

    try:
        import skill_finder as sf  # noqa: PLC0415
    except ImportError as e:  # noqa: BLE001
        check("skill_finder.py imports", False, str(e))
        print("\n0/1 checks passed.")
        return 1

    # Redirect the execution log to os.devnull for the read-only
    # checks: the real logs/skill_executions.jsonl is never touched
    # by this run (the write-dependent check below redirects it to a
    # temp file itself, when the environment allows one).
    real_log_path = sf.LOG_PATH
    sf.LOG_PATH = os.devnull

    # 1. Skill counts: 112 real skills.
    try:
        idx = sf.build_index()
        local = sf.list_local_skills()
        doc = sf.doctor()
        ok = (len(idx) == 112 and len(local) == 112
              and doc["skills_found"] == 112 and doc["problems"] == [])
        check("skill counts: 112 real skills (index == local == doctor)",
              ok, f"index={len(idx)}, local={len(local)}, "
              f"doctor={doc['skills_found']}, "
              f"problems={len(doc['problems'])}")
    except Exception as e:  # noqa: BLE001
        check("skill counts: 112 real skills (index == local == doctor)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 2. Frontmatter format on all 112 (read-only).
    try:
        idx = sf.build_index()
        index_problems = sf.validate_index(idx)
        file_problems = []
        for path in sf._iter_skill_files():
            with open(path, "r", encoding="utf-8") as f:
                head = f.readline().strip()
            if sf._is_pointer_or_manifest(path, head):
                continue
            file_problems.extend(sf.validate_skill_frontmatter(path))
        problems = index_problems + file_problems
        check("frontmatter format: validate_index + all 112 files valid",
              not problems, "; ".join(problems[:3])
              if problems else "112/112 valid")
    except Exception as e:  # noqa: BLE001
        check("frontmatter format: validate_index + all 112 files valid",
              False, f"{type(e).__name__}: {e}"[:160])

    # 3. Progressive disclosure: index entries carry only the four keys.
    try:
        idx = sf.build_index()
        bad = [e for e in idx
               if set(e) != {"name", "description", "path", "version"}]
        check("progressive disclosure: index entries carry only "
              "name/description/path/version",
              not bad, f"{len(idx)} entries, {len(bad)} with extra keys")
    except Exception as e:  # noqa: BLE001
        check("progressive disclosure: index entries carry only "
              "name/description/path/version",
              False, f"{type(e).__name__}: {e}"[:160])

    # 4. find_skills returns index-only entries; load loads the top
    # match's full text only.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            found = sf.find_skills("backup", top_n=3)
            task = sf.load_skill_for_task("backup")
        top = found[0] if found else {}
        loaded = task.get("loaded") or {}
        with open(os.path.join(BASE, loaded.get("path", "")),
                  encoding="utf-8") as f:
            full_text = f.read()
        ok = (top.get("name") == "backup-recovery-agent"
              and "content" not in top
              and all("content" not in e for e in found)
              and loaded.get("name") == "backup-recovery-agent"
              and loaded.get("content") == full_text
              and loaded["content"].startswith("---\nname: backup-recovery-agent"))
        check("find_skills index-only; load_skill_for_task loads full "
              "text of top match only",
              ok, f"top={top.get('name')}, loaded={loaded.get('name')}, "
              f"content_len={len(loaded.get('content', ''))}")
    except Exception as e:  # noqa: BLE001
        check("find_skills index-only; load_skill_for_task loads full "
              "text of top match only",
              False, f"{type(e).__name__}: {e}"[:160])

    # 5. Finder locates "backup" -> backup-recovery-agent.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            found = sf.find_skills("backup")
        ok = bool(found) and found[0]["name"] == "backup-recovery-agent"
        check('finder locates "backup" -> backup-recovery-agent',
              ok, f"top={found[0]['name'] if found else None}")
    except Exception as e:  # noqa: BLE001
        check('finder locates "backup" -> backup-recovery-agent',
              False, f"{type(e).__name__}: {e}"[:160])

    # 6. Finder: "kit builder" -> kit-builder, ambiguous, 2 candidates.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            task = sf.load_skill_for_task("kit builder")
        loaded = task.get("loaded") or {}
        ok = (loaded.get("name") == "kit-builder"
              and task.get("ambiguous") is True
              and task.get("candidates") == [
                  "02-Digital-Product-Department/engine/skills/kit-builder.md",
                  "02-Digital-Product-Department/sections/product/skills/kit-builder.md"])
        check('finder: "kit builder" -> kit-builder, ambiguous, '
              "exactly 2 candidates",
              ok, f"loaded={loaded.get('name')}, "
              f"ambiguous={task.get('ambiguous')}, "
              f"candidates={len(task.get('candidates') or [])}")
    except Exception as e:  # noqa: BLE001
        check('finder: "kit builder" -> kit-builder, ambiguous, '
              "exactly 2 candidates",
              False, f"{type(e).__name__}: {e}"[:160])

    # 7. Finder: unknown skill -> no matches, loaded None.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            found = sf.find_skills("xyznoskill")
            task = sf.load_skill_for_task("xyznoskill")
        ok = (found == [] and task.get("loaded") is None
              and task.get("ambiguous") is False
              and task.get("candidates") == [])
        check('finder: "xyznoskill" -> no matches, loaded None',
              ok, f"found={len(found)}, loaded={task.get('loaded')}")
    except Exception as e:  # noqa: BLE001
        check('finder: "xyznoskill" -> no matches, loaded None',
              False, f"{type(e).__name__}: {e}"[:160])

    # 8-10. Chief-routed tasks on the mock path. _log_task is
    # monkeypatched to an in-memory recorder and OwnerMemory is never
    # touched (_handle_task_inner does not read memory — only the
    # handle_task wrapper does), so no store file is written here.
    try:
        import chief_of_staff_agency as chief  # noqa: PLC0415
    except ImportError as e:  # noqa: BLE001
        chief = None
        check("chief imports (for end-to-end skill-hook tests)",
              False, str(e))

    if chief is not None:
        logged = []
        real_log_task = chief._log_task
        chief._log_task = lambda rec, tasks_path=None: (
            logged.append(rec) or rec)

        # 8. caption_write end-to-end: draft-ready + caption-writer,
        # Agency engine copy; existing keys unchanged.
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = chief._handle_task_inner(
                    {"type": "caption_write",
                     "title": "Write captions for a plumbing Facebook post",
                     "payload": {}},
                    tasks_path=os.path.join("nope", "tasks.json"))
            sk = r.get("skill") or {}
            ok = (r["status"] == "draft-ready"
                  and r.get("worker") == "CaptionWriter"
                  and sk.get("name") == "caption-writer"
                  and sk.get("path") == "01-Agency-Department/engine/skills/caption-writer.md"
                  and sk.get("loaded") is True
                  and r.get("draft_only") is True
                  and r.get("mock_brain") is True
                  and r.get("gate") is None)
            check("chief end-to-end (mock): caption_write -> draft-ready "
                  "+ skill caption-writer (Agency engine copy)",
                  ok, f"status={r['status']}, worker={r.get('worker')}, "
                  f"skill={sk.get('name')}, path={sk.get('path')}")
        except Exception as e:  # noqa: BLE001
            check("chief end-to-end (mock): caption_write -> draft-ready "
                  "+ skill caption-writer (Agency engine copy)",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 9. Gated task returns BEFORE any skill work (stub gateway so
        # no approvals file is written — the gateway itself is
        # check_gate.py's scope, not this script's).
        try:
            class _StubGateway:
                def __init__(self, *a, **k):
                    pass

                def is_approved(self, approval_id):
                    return False

                def request(self, action, detail, requested_by):
                    return {"id": "stub-approval",
                            "status": "pending", "action": action}

            real_gateway = chief.ApprovalGateway
            chief.ApprovalGateway = _StubGateway
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    r = chief._handle_task_inner(
                        {"type": "outreach_draft", "title": "gated send",
                         "payload": {"channel": "email"},
                         "gated_action": "send"},
                        tasks_path=os.path.join("nope", "tasks.json"))
            finally:
                chief.ApprovalGateway = real_gateway
            ok = (r["status"] == "pending-approval"
                  and "skill" not in r
                  and r.get("worker") is None)
            check("chief: gated task returns before any skill work "
                  "(no 'skill' key)",
                  ok, f"status={r['status']}, has_skill={'skill' in r}")
        except Exception as e:  # noqa: BLE001
            check("chief: gated task returns before any skill work "
                  "(no 'skill' key)",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 10. Department manager runs with the skill name/path as
        # advisory context (unknown key ignored, no crash, draft-ready).
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = chief._handle_task_inner(
                    {"type": "dept_sales", "title": "Sales overview check",
                     "payload": {}},
                    tasks_path=os.path.join("nope", "tasks.json"))
            sk = r.get("skill") or {}
            ok = (r["status"] == "draft-ready"
                  and r.get("worker") == "ChiefGrowthAgent"
                  and sk.get("loaded") is True
                  and sk.get("name") and sk.get("path"))
            check("chief: dept manager runs with skill advisory context "
                  "(unknown key ignored)",
                  ok, f"status={r['status']}, worker={r.get('worker')}, "
                  f"skill={sk.get('name')}")
        except Exception as e:  # noqa: BLE001
            check("chief: dept manager runs with skill advisory context "
                  "(unknown key ignored)",
                  False, f"{type(e).__name__}: {e}"[:160])

        chief._log_task = real_log_task

    # 11. Duplicates resolved: kit-qa + script-writer, 1 entry each,
    # engine copy.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            qa = sf.find_candidates("kit-qa")
            sw = sf.find_candidates("script-writer")
            qa_loaded = sf.load_skill("kit-qa")
            sw_loaded = sf.load_skill("script-writer")
        ok = (qa == ["02-Digital-Product-Department/engine/skills/kit-qa.md"]
              and sw == ["03-Content-Creation-Department/engine/skills/script-writer.md"]
              and qa_loaded["path"] == qa[0]
              and sw_loaded["path"] == sw[0])
        check("duplicates resolved: kit-qa + script-writer, 1 index "
              "entry each (engine copy)",
              ok, f"kit-qa={qa}, script-writer={sw}")
    except Exception as e:  # noqa: BLE001
        check("duplicates resolved: kit-qa + script-writer, 1 index "
              "entry each (engine copy)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 12. The 5 pointer files are excluded from the index.
    try:
        pointers = []
        for path in sf._iter_skill_files():
            with open(path, "r", encoding="utf-8") as f:
                head = f.readline().strip()
            if head.startswith(sf.POINTER_MARKER):
                pointers.append(os.path.relpath(path, BASE))
        idx = sf.build_index()
        idx_paths = {e["path"] for e in idx}
        ok = (len(pointers) == 5
              and not (set(pointers) & idx_paths))
        check("pointers excluded: 5 pointer files, none in the index",
              ok, f"pointers={len(pointers)}")
    except Exception as e:  # noqa: BLE001
        check("pointers excluded: 5 pointer files, none in the index",
              False, f"{type(e).__name__}: {e}"[:160])

    # 13. Broken references: every index path resolves; every pointer
    # target exists.
    try:
        idx = sf.build_index()
        missing = [e["path"] for e in idx
                   if not os.path.isfile(os.path.join(BASE, e["path"]))]
        bad_targets = []
        for path in sf._iter_skill_files():
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            head = text.splitlines()[0] if text.splitlines() else ""
            if not head.startswith(sf.POINTER_MARKER):
                continue
            rel = head[len(sf.POINTER_MARKER):].strip()
            target = os.path.normpath(
                os.path.join(os.path.dirname(path), rel))
            if not os.path.isfile(target):
                bad_targets.append(os.path.relpath(path, BASE))
        ok = not missing and not bad_targets
        check("broken references: all index paths exist, all pointer "
              "targets exist",
              ok, f"missing_index={missing[:3]}, "
              f"bad_targets={bad_targets[:3]}"
              if (missing or bad_targets) else f"{len(idx)} paths ok")
    except Exception as e:  # noqa: BLE001
        check("broken references: all index paths exist, all pointer "
              "targets exist",
              False, f"{type(e).__name__}: {e}"[:160])

    # 14. Execution-log recording — WRITE-DEPENDENT: probe first.
    writable, probe = _probe_writable()
    if not writable:
        skip("execution log: load recorded in skill_executions.jsonl",
             f"environment write block ({probe})")
    else:
        tmp_log = os.path.join(probe, "skill_executions.jsonl")
        sf.LOG_PATH = tmp_log
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                loaded = sf.load_skill("backup-recovery-agent")
            with open(tmp_log, encoding="utf-8") as f:
                recs = [json.loads(line) for line in f if line.strip()]
            ok = any(r["event"] == "load_skill"
                     and r.get("skill") == "backup-recovery-agent"
                     and r.get("result") == loaded["path"]
                     and r.get("timestamp") for r in recs)
            check("execution log: load recorded in skill_executions.jsonl",
                  ok, f"records={len(recs)}")
        except Exception as e:  # noqa: BLE001
            check("execution log: load recorded in skill_executions.jsonl",
                  False, f"{type(e).__name__}: {e}"[:160])
        finally:
            sf.LOG_PATH = os.devnull

    # 15. Temp-skill validation (version parse + bad version flagged)
    # — WRITE-DEPENDENT: probe first.
    writable, probe = _probe_writable()
    if not writable:
        skip("temp skill validation: version parses, bad version flagged",
             f"environment write block ({probe})")
    else:
        try:
            vfile = os.path.join(probe, "versioned-skill.md")
            with open(vfile, "w", encoding="utf-8") as f:
                f.write("---\nname: versioned-skill\n"
                        "description: A temp skill for the version check.\n"
                        "version: 2.3.1\n---\n\n# Versioned Skill\n\nBody.\n")
            vbad = os.path.join(probe, "bad-version-skill.md")
            with open(vbad, "w", encoding="utf-8") as f:
                f.write("---\nname: bad-version-skill\n"
                        "description: Bad version format.\n"
                        "version: v1\n---\n\n# Bad Version Skill\n\nBody.\n")
            ok = (sf._read_frontmatter(vfile)["version"] == "2.3.1"
                  and sf.validate_skill_frontmatter(vfile) == []
                  and sf.validate_skill_frontmatter(vbad) != [])
            check("temp skill validation: version parses, bad version "
                  "flagged",
                  ok, "2.3.1 parses, v1 flagged" if ok else "mismatch")
        except Exception as e:  # noqa: BLE001
            check("temp skill validation: version parses, bad version "
                  "flagged",
                  False, f"{type(e).__name__}: {e}"[:160])

    # 16. Chief real-path call (real temp tasks path) — attempted
    # honestly; a write failure is [BLOCKED], not a fail.
    writable, probe = _probe_writable()
    if not writable:
        blocked("chief real-path call (real temp tasks path)",
                f"environment write block ({probe}) — the hook logic "
                "itself is covered by the monkeypatched end-to-end "
                "check above")
    else:
        try:
            import chief_of_staff_agency as chief  # noqa: PLC0415

            tasks_p = os.path.join(probe, "tasks.json")
            appr_p = os.path.join(probe, "approvals.json")
            mem_p = os.path.join(probe, "memory.json")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = chief.handle_task(
                    {"type": "caption_write",
                     "title": "Write captions for a plumbing Facebook post",
                     "payload": {}},
                    tasks_path=tasks_p, approvals_path=appr_p,
                    memory_path=mem_p)
            with open(tasks_p, encoding="utf-8") as f:
                data = json.load(f)
            sk = r.get("skill") or {}
            ok = (r["status"] == "draft-ready"
                  and sk.get("name") == "caption-writer"
                  and len(data.get("records", [])) == 1)
            check("chief real-path call (real temp tasks path)",
                  ok, f"status={r['status']}, skill={sk.get('name')}, "
                  f"records={len(data.get('records', []))}")
        except Exception as e:  # noqa: BLE001
            blocked("chief real-path call (real temp tasks path)",
                    f"{type(e).__name__}: {e}"[:200])

    # 17. Real store unchanged by this check run.
    try:
        sf.LOG_PATH = real_log_path
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    failed = [r for r in results if r[1] == "FAIL"]
    passed = [r for r in results if r[1] == "PASS"]
    skipped = [r for r in results if r[1] == "SKIP"]
    blocked_r = [r for r in results if r[1] == "BLOCKED"]
    decided = len(passed) + len(failed)
    print(f"\n{len(passed)}/{decided} checks passed "
          f"({len(skipped)} skipped, {len(blocked_r)} blocked).")
    if skipped:
        print("SKIPPED:", [r[0] for r in skipped])
    if blocked_r:
        print("BLOCKED:", [r[0] for r in blocked_r])
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_skills: ALL DECIDED CHECKS PASS (offline — no live call made).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
