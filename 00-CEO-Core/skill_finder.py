"""Skill-finder — the Main CEO Bot's skill-finding ability (REAL, 2026-11-21).

Adapted from two upstream skill-finders (read-only reference, no code
copied — their text was read, their scripts/commands were NOT reproduced):
  - cubicyyy/auto-research-skills — skill-finder (MIT, per SKILL.md
    frontmatter): search -> shortlist top 3-5 by stars -> confirm ->
    vendor verbatim -> surface chosen skills. Mechanism (git submodules
    + symlinks + uv CLI) does NOT fit Talvenor (Windows symlink pain,
    no Claude Code here) — method kept, mechanism replaced.
  - vercel-labs/skills — find-skills (MIT): leaderboard first
    (skills.sh), then keyword search; verify install count (1K+
    preferred, <100 wary), source reputation, GitHub stars; present
    options; install only on approval.

Talvenor rules layered on top:
  - Local first: the repo's own skills/ are searched first.
  - $0 cap: no paid skill/account; brain mock — no live call.
  - Draft-only: a proposal can be written (store/skill-proposals.json),
    a skill file cannot be written / installed — Boss's "ok" is needed.
  - Never verbatim: no copying an outside skill — adapt it for Talvenor.
  - Windows: no symlink — the adapted file is copied.

Progressive-disclosure loader (2026-11-24, Agent Skills format —
agentskills.io: a skill carries `name` + one-line `description` as
metadata, full instructions load only on match):
  - Discovery: build_index() reads ONLY the frontmatter of each skill
    file (name + description), never the full text.
  - Activation: find_skills() ranks the index by task keywords;
    load_skill() reads the FULL file, but only for a match.
  - The index covers ALL 28 skills dirs in the repo (Agency engine +
    departments + sections, Products engine + sections, Content engine
    + sections, root skills/). Before 2026-11-24 only the 15 Agency
    roots were indexed — the 34 Products/Content skills were invisible.
  - Phase-1 pointer files and the SKILL_INDEX.md manifest are NOT
    skills and are never indexed (a pointer resolves to its canonical
    engine copy instead).

Phase 2 hardening (2026-11-25):
  - Validation: validate_skill_frontmatter() / validate_index() check
    name (present, non-empty, equal to the file stem), description
    (present, non-empty, single-line), and version (when present,
    N.N or N.N.N). doctor() reports validation failures.
  - Version: an optional `version:` frontmatter key; absent -> "1.0"
    (default in code — the 114 skill files were NOT rewritten).
    Index entries carry an additive "version" key.
  - Execution tracking: every load_skill / load_skill_for_task call is
    appended to logs/skill_executions.jsonl (skill name, query, UTC
    timestamp, result path or error type — never skill content or
    keys). LOG_PATH is module-level and monkeypatchable for tests.
  - Bare-name collision: several names exist in 2-3 copies (e.g.
    kit-builder). load_skill() warns + logs an ambiguous_bare_name
    event, then loads the FIRST match (unchanged behavior). Callers
    should prefer an explicit repo path (load_skill("path/to/x.md"))
    or a qualified lookup instead of a bare name.

Stdlib only. No network — a human (Mira) does the online search; this module
only does local registry search + writes DRAFT proposals.
"""

import json
import os
import re
import warnings
from datetime import datetime, timezone

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROPOSALS_PATH = os.path.join(_MASTER_OS_DIR, "store",
                                      "skill-proposals.json")

# Local skill roots — ALL skill folders in the repo (28 dirs).
SKILL_ROOTS = (
    "skills",
    "01-Agency-Department/engine/skills",
    "01-Agency-Department/sections/receive/skills",
    "01-Agency-Department/sections/sell/skills",
    "01-Agency-Department/sections/delivery/skills",
    "01-Agency-Department/sections/ops/skills",
    "01-Agency-Department/sections/marketing/skills",
    "01-Agency-Department/departments/01-sales-growth/skills",
    "01-Agency-Department/departments/02-marketing/skills",
    "01-Agency-Department/departments/03-ai-engineering/skills",
    "01-Agency-Department/departments/04-client-operations/skills",
    "01-Agency-Department/departments/05-research-strategy/skills",
    "01-Agency-Department/departments/06-finance-admin/skills",
    "01-Agency-Department/departments/07-quality-security/skills",
    "01-Agency-Department/departments/08-product-innovation/skills",
    "02-Digital-Product-Department/engine/skills",
    "02-Digital-Product-Department/sections/finance/skills",
    "02-Digital-Product-Department/sections/launch/skills",
    "02-Digital-Product-Department/sections/product/skills",
    "02-Digital-Product-Department/sections/research/skills",
    "02-Digital-Product-Department/sections/sales/skills",
    "02-Digital-Product-Department/sections/support/skills",
    "03-Content-Creation-Department/engine/skills",
    "03-Content-Creation-Department/sections/analyze/skills",
    "03-Content-Creation-Department/sections/growth/skills",
    "03-Content-Creation-Department/sections/plan/skills",
    "03-Content-Creation-Department/sections/produce/skills",
    "03-Content-Creation-Department/sections/publish/skills",
)

# Files that look like skills but are not: Phase-1 pointer files (their
# first line starts with this marker) and the dedup manifest.
POINTER_MARKER = "Moved — canonical copy:"
NON_SKILL_FILES = ("SKILL_INDEX.md",)

# Remote directories the finder searches (names + licenses only).
REMOTE_SOURCES = (
    {"name": "skills.sh", "license": "per-skill",
     "what": "leaderboard + keyword search"},
    {"name": "anthropics/skills", "license": "Apache-2.0",
     "what": "docs / design / build skills"},
    {"name": "anthropics/knowledge-work-plugins", "license": "Apache-2.0",
     "what": "sales / finance / marketing role skills"},
    {"name": "vercel-labs/skills", "license": "MIT",
     "what": "find-skills + web skills"},
    {"name": "adkit/ads-skills", "license": "MIT",
     "what": "Meta / Google ads strategy"},
    {"name": "superamped/ai-marketing-skills", "license": "MIT",
     "what": "ad analyzer, angles, creative"},
    {"name": "makash/godmode", "license": "MIT",
     "what": "backup + 126 engineering skills"},
    {"name": "poorangryman/ai-agent-pro-kit", "license": "MIT",
     "what": "agent-memory"},
    {"name": "frankxai/skills", "license": "MIT",
     "what": "tool-allowlist"},
    {"name": "braydos-h/BreachPilot", "license": "Apache-2.0",
     "what": "tool-invocation security"},
    {"name": "openclaw/skills", "license": "MIT",
     "what": "expense-tracker, memory"},
    {"name": "cubicyyy/auto-research-skills", "license": "MIT",
     "what": "skill-finder (exact name)"},
)

# find-skills quality gate (vercel): installs / reputation thresholds.
MIN_INSTALLS_PREFERRED = 1000
MIN_INSTALLS_WARY = 100
TRUSTED_PUBLISHERS = ("vercel-labs", "anthropics", "microsoft", "openclaw")

# Phase 2: skill version. Optional `version:` frontmatter key; absent -> "1.0".
# The 114 skill files were NOT rewritten to add versions — the default lives
# in code (see _read_frontmatter / build_index / _parse_skill_file).
DEFAULT_VERSION = "1.0"
VERSION_RE = re.compile(r"^\d+\.\d+(\.\d+)?$")

# Phase 2: execution log. Module-level so tests can monkeypatch it to a
# temp file; _log_execution reads this global at call time. The file lives
# under logs/, which is gitignored (Phase 1) — runtime state, never pushed.
LOG_PATH = os.path.join(_MASTER_OS_DIR, "logs", "skill_executions.jsonl")


def _is_pointer_or_manifest(path, head=""):
    """True for Phase-1 pointer files and the SKILL_INDEX.md manifest."""
    if os.path.basename(path) in NON_SKILL_FILES:
        return True
    if head.startswith(POINTER_MARKER):
        return True
    return False


def _read_frontmatter(path):
    """Read ONLY the head of a skill file: the YAML frontmatter block.

    Returns {"name": ..., "description": ..., "version": ...} (keys
    missing when absent; "version" is optional, default "1.0" is applied
    by the callers, not here). Reads at most the first 4 KiB — the
    discovery step never loads a full skill file. Returns {} for files
    without frontmatter.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            head = f.read(4096)
    except OSError:
        return {}
    lines = head.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    meta = {}
    for line in lines[1:]:
        s = line.strip()
        if s == "---":
            break
        m = re.match(r"^(name|description|version):\s*(.*)$", s)
        if not m:
            continue
        value = m.group(2).strip()
        if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        meta[m.group(1)] = value
    return meta


def _strip_frontmatter(text):
    """Remove a leading YAML frontmatter block (--- ... ---) if present."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1:])
    return text


def _fallback_description(text):
    """One-line description from the body (pre-frontmatter heuristic)."""
    for line in _strip_frontmatter(text).splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">") or s.startswith("**"):
            continue
        return s
    return ""


def _parse_skill_file(path):
    """Name + title + one-line description + version from a .md skill file.

    Frontmatter wins when present; otherwise the old heuristic applies.
    Version is the frontmatter `version:` key when present, else
    DEFAULT_VERSION ("1.0") — no skill file is rewritten to add one.
    Returns None for pointer files and the manifest (not skills).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    first_line = text.splitlines()[0] if text.splitlines() else ""
    if _is_pointer_or_manifest(path, first_line):
        return None
    meta = _read_frontmatter(path)
    title = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            break
    description = meta.get("description") or _fallback_description(text)
    return {
        "name": meta.get("name")
        or os.path.splitext(os.path.basename(path))[0],
        "title": title,
        "description": description,
        "version": meta.get("version") or DEFAULT_VERSION,
        "path": os.path.relpath(path, _MASTER_OS_DIR),
    }


def _iter_skill_files(repo_dir=None):
    """All candidate skill .md files under every SKILL_ROOT."""
    root = repo_dir or _MASTER_OS_DIR
    for rel in SKILL_ROOTS:
        d = os.path.join(root, rel)
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            if fname.endswith(".md"):
                yield os.path.join(d, fname)


def build_index(repo_dir=None):
    """Discovery index: name + one-line description + version for every skill.

    Reads frontmatter only (cheap); full skill text is never loaded here.
    Pointer files and the manifest are excluded. "version" is the
    frontmatter `version:` key when present, else DEFAULT_VERSION ("1.0").
    A malformed version is carried as-is so validate_index() can flag it.
    """
    index = []
    for path in _iter_skill_files(repo_dir):
        try:
            with open(path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
        except OSError:
            continue
        if _is_pointer_or_manifest(path, first_line):
            continue
        meta = _read_frontmatter(path)
        if meta.get("name") and meta.get("description"):
            index.append({
                "name": meta["name"],
                "description": meta["description"],
                "version": meta.get("version") or DEFAULT_VERSION,
                "path": os.path.relpath(path, repo_dir or _MASTER_OS_DIR),
            })
            continue
        # No frontmatter: fall back to a full parse for this file only.
        parsed = _parse_skill_file(path)
        if parsed is not None:
            index.append({
                "name": parsed["name"],
                "description": parsed["description"],
                "version": parsed["version"],
                "path": parsed["path"],
            })
    return index


def _log_execution(event, skill=None, query=None, result=None, error=None,
                   candidates=None):
    """Append one skill-execution record to LOG_PATH (JSONL, one line).

    Record: event, skill name, task/query, UTC ISO timestamp, result
    (loaded repo-relative path, or None) or error type. An
    "ambiguous_bare_name" event also carries "candidates" (all matching
    repo-relative paths). Only names/paths/timestamps are logged — never
    skill content, keys, or credentials. Never raises: logging must not
    break a load (a failed write is silently dropped).
    """
    record = {
        "event": event,
        "skill": skill,
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "error": error,
    }
    if candidates is not None:
        record["candidates"] = list(candidates)
    try:
        parent = os.path.dirname(LOG_PATH)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def validate_skill_frontmatter(path):
    """Validate one skill file's effective metadata.

    Checks: name present, non-empty, and equal to the file stem;
    description present, non-empty, single-line; version, when present
    in frontmatter, matches N.N or N.N.N (VERSION_RE). Name/description
    fall back to the same resolution _parse_skill_file uses (file stem /
    first body line), so a file whose frontmatter omits a key still
    validates when the fallback resolves it — only a genuinely missing,
    empty, or mismatched value is a problem. Pointer files and the manifest are not skills: [].
    Returns a list of problem strings (empty = valid).
    """
    try:
        rel = os.path.relpath(path, _MASTER_OS_DIR)
    except ValueError:
        rel = path
    try:
        with open(path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
    except OSError:
        return [f"unreadable: {rel}"]
    if _is_pointer_or_manifest(path, first_line):
        return []
    meta = _read_frontmatter(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    problems = []
    name = meta.get("name") or stem
    if not name:
        problems.append(f"no name: {rel}")
    elif meta.get("name") and meta["name"] != stem:
        problems.append(f"name mismatch: {rel} (name {meta['name']!r} "
                        f"!= file stem {stem!r})")
    description = meta.get("description")
    if not description:
        parsed = _parse_skill_file(path)
        description = parsed["description"] if parsed else ""
    if not description:
        problems.append(f"no description: {rel}")
    elif "\n" in description:
        problems.append(f"multi-line description: {rel}")
    version = meta.get("version")
    if version is not None and not VERSION_RE.match(version):
        problems.append(f"bad version: {rel} (version {version!r} must "
                        "match N.N or N.N.N)")
    return problems


def validate_index(index, repo_dir=None):
    """Validate a discovery index (as built by build_index).

    Per entry: name present/non-empty, description present/non-empty/
    single-line, version (when present) matches N.N or N.N.N. Also
    checks the index count equals len(list_local_skills(repo_dir)) —
    pass repo_dir when the index was built from a non-default repo.
    Returns a list of problem strings (empty = valid).
    """
    problems = []
    for entry in index:
        label = entry.get("name") or entry.get("path") or "?"
        if not entry.get("name"):
            problems.append(
                f"index entry missing name: {entry.get('path', '?')}")
        if not entry.get("description"):
            problems.append(f"index entry missing description: {label}")
        elif "\n" in entry["description"]:
            problems.append(f"index entry multi-line description: {label}")
        version = entry.get("version")
        if version is not None and not VERSION_RE.match(version):
            problems.append(f"index entry bad version: {label} "
                            f"(version {version!r} must match N.N or N.N.N)")
    expected = len(list_local_skills(repo_dir))
    if len(index) != expected:
        problems.append(f"index count {len(index)} != "
                        f"local skills {expected}")
    return problems


def find_candidates(name, repo_dir=None):
    """All index matches for a bare skill name, as repo-relative paths.

    Returns [] when nothing matches, one path for a unique skill, and
    more than one path when the same bare name exists in several copies
    (14 such names exist in the repo today). Order is index order — the
    first entry is the copy load_skill() loads.
    """
    return [entry["path"] for entry in build_index(repo_dir)
            if entry["name"] == name]


def _score(query, name, description):
    """Keyword hits of the query in a skill's name + description."""
    words = [w.lower() for w in re.findall(r"[a-z0-9][a-z0-9_-]*",
                                           (query or "").lower())]
    if not words:
        return 0
    hay = (name + " " + description).lower()
    return sum(1 for w in words if w in hay)


def find_skills(query, repo_dir=None, top_n=5):
    """Rank the discovery index by task keywords — names only, no content."""
    scored = []
    for entry in build_index(repo_dir):
        hits = _score(query, entry["name"], entry["description"])
        if hits:
            scored.append((hits, entry))
    scored.sort(key=lambda item: (-item[0], item[1]["name"]))
    return [entry for _, entry in scored[:top_n]]


def list_local_skills(repo_dir=None):
    """Registry of all local skill files in the repo."""
    found = []
    for path in _iter_skill_files(repo_dir):
        parsed = _parse_skill_file(path)
        if parsed is not None:
            found.append(parsed)
    return found


def find_skill_local(query, repo_dir=None):
    """Keyword search in the local registry — match in name + description."""
    scored = []
    for skill in list_local_skills(repo_dir):
        hits = _score(query, skill["name"], skill["description"])
        if hits:
            scored.append((hits, skill))
    scored.sort(key=lambda item: (-item[0], item[1]["name"]))
    return [skill for _, skill in scored]


def load_skill(name_or_path, repo_dir=None):
    """Activation: read the FULL text of one skill, by name or repo path.

    Pointers never resolve — a pointer's stem resolves to its canonical
    engine copy, because pointers are excluded from the index.
    Returns {"name", "description", "path", "version", "content"}.
    Raises ValueError when no skill matches.
    Bare-name collision: when a bare name matches more than one index
    entry, a UserWarning is emitted and an "ambiguous_bare_name" event
    (with all candidate paths) is appended to the execution log — then
    the FIRST match is returned, unchanged. Prefer an explicit repo
    path (load_skill("path/to/skill.md")) over a bare name. Every call
    (success or failure) is recorded in the execution log.
    """
    root = repo_dir or _MASTER_OS_DIR
    target = (name_or_path or "").strip()
    if not target:
        _log_execution("load_skill", skill=None, result=None,
                       error="ValueError")
        raise ValueError("load_skill: empty name or path")
    candidates = []
    if os.path.sep in target or target.endswith(".md"):
        path = target if os.path.isabs(target) else os.path.join(root, target)
        if os.path.isfile(path):
            candidates.append(path)
    else:
        # Bare name: may match more than one copy (dedup is Worker B's
        # scope; this loader must stay correct over whatever files exist).
        rel_paths = find_candidates(target, repo_dir=root)
        if len(rel_paths) > 1:
            warnings.warn(
                f"load_skill: ambiguous bare name {target!r} matches "
                f"{len(rel_paths)} skills {rel_paths} — loading the "
                "first; prefer an explicit repo path",
                UserWarning, stacklevel=2)
            _log_execution("ambiguous_bare_name", skill=target, result=None,
                           candidates=rel_paths)
        candidates = [os.path.join(root, p) for p in rel_paths]
    for path in candidates:
        parsed = _parse_skill_file(path)
        if parsed is None:
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        result = {
            "name": parsed["name"],
            "description": parsed["description"],
            "path": parsed["path"],
            "version": parsed.get("version", DEFAULT_VERSION),
            "content": content,
        }
        _log_execution("load_skill", skill=parsed["name"],
                       result=parsed["path"])
        return result
    _log_execution("load_skill", skill=target, result=None,
                   error="ValueError")
    raise ValueError(f"load_skill: no skill named or at {target!r}")


def load_skill_for_task(query, repo_dir=None, top_n=1):
    """Find matching skills for a task, then load the FULL text of the top one.

    Returns {"matches": [...index entries...], "loaded": {...} or None,
    "ambiguous": bool, "candidates": [...repo-relative paths...]}.
    Only the top match's full text is loaded — the rest stay index-only.
    "ambiguous" is True when the top match's bare name exists in more
    than one copy; "candidates" lists every copy's path. Every call is
    recorded in the execution log (see _log_execution).
    """
    matches = find_skills(query, repo_dir=repo_dir, top_n=top_n)
    loaded = None
    ambiguous = False
    candidates = []
    if matches:
        candidates = find_candidates(matches[0]["name"], repo_dir=repo_dir)
        ambiguous = len(candidates) > 1
        try:
            loaded = load_skill(matches[0]["name"], repo_dir=repo_dir)
        except ValueError:
            _log_execution("load_skill_for_task", skill=matches[0]["name"],
                           query=query, result=None, error="ValueError")
            raise
    _log_execution("load_skill_for_task",
                   skill=loaded["name"] if loaded else None,
                   query=query,
                   result=loaded["path"] if loaded else None)
    return {"matches": matches, "loaded": loaded,
            "ambiguous": ambiguous, "candidates": candidates}


def quality_gate(installs=None, stars=None, publisher="", license_id=""):
    """find-skills verification: installs + reputation + license.

    Returns (ok, reason). Not ok without an MIT/Apache-2.0 license.
    """
    if license_id not in ("MIT", "Apache-2.0"):
        return False, f"license {license_id!r} not allowed (MIT/Apache-2.0 only)"
    if installs is not None and installs < MIN_INSTALLS_WARY:
        return False, f"only {installs} installs (< {MIN_INSTALLS_WARY}) — too weak"
    if stars is not None and stars < 5:
        return False, f"only {stars} stars (< 5) — too weak"
    if publisher and publisher not in TRUSTED_PUBLISHERS:
        return True, (f"unknown publisher {publisher!r} — usable, "
                      "but rank below trusted publishers")
    return True, "pass"


def propose_skill(query, agent, candidate_repo, candidate_skill,
                  source_url, license_id, fit_note, why="",
                  proposals_path=None):
    """Write a DRAFT proposal — not an install, not writing a skill file.

    Without Boss's "ok", nothing comes of a proposal.
    """
    ok, reason = quality_gate(license_id=license_id)
    if not ok:
        raise ValueError(f"Proposal refused by quality gate: {reason}")
    path = proposals_path or DEFAULT_PROPOSALS_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        proposals = data.get("proposals", []) if isinstance(data, dict) else []
    except (FileNotFoundError, json.JSONDecodeError):
        proposals = []
    # Dedup (2026-11-21): the same repo + same skill is never proposed twice —
    # the earlier proposal is returned, no new record is written.
    for existing in proposals:
        if (existing.get("candidate_repo") == candidate_repo
                and existing.get("candidate_skill") == candidate_skill):
            duplicate = dict(existing)
            duplicate["duplicate"] = True
            return duplicate
    proposal = {
        "status": "proposed",
        "query": query,
        "agent": agent,
        "why": why,
        "candidate_repo": candidate_repo,
        "candidate_skill": candidate_skill,
        "source_url": source_url,
        "license": license_id,
        "fit_note": fit_note,
        "quality_gate": reason,
    }
    proposals.append(proposal)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"proposals": proposals}, f, indent=2, ensure_ascii=False)
    return dict(proposal)


def doctor(repo_dir=None):
    """Check the local skill registry: can files be read, do they have a heading.

    Problems also include frontmatter validation failures
    (validate_skill_frontmatter per file) and index validation failures
    (validate_index: per-entry checks + index count vs local skills).
    """
    problems = []
    skills = list_local_skills(repo_dir)
    for skill in skills:
        if not skill["title"]:
            problems.append(f"no heading: {skill['path']}")
        if not skill["description"]:
            problems.append(f"no description: {skill['path']}")
    for path in _iter_skill_files(repo_dir):
        try:
            with open(path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
        except OSError:
            continue
        if _is_pointer_or_manifest(path, first_line):
            continue
        problems.extend(validate_skill_frontmatter(path))
    problems.extend(validate_index(build_index(repo_dir), repo_dir))
    return {"skills_found": len(skills), "problems": problems}


if __name__ == "__main__":
    # Manual check: TEMP paths are used — the real store is never touched.
    import tempfile

    _tmp = tempfile.mkdtemp()
    _tmp_props = os.path.join(_tmp, "skill-proposals.json")
    # Phase 2: point the execution log at a temp file for the whole
    # self-test — the real logs/skill_executions.jsonl is never touched.
    _tmp_log = os.path.join(_tmp, "skill_executions.jsonl")
    _real_log = LOG_PATH
    LOG_PATH = _tmp_log
    _local = find_skill_local("backup")
    assert any(s["name"] == "backup-recovery-agent" for s in _local), _local
    assert find_skill_local("xyznoskill") == []
    ok, _reason = quality_gate(installs=5000, stars=1000,
                               publisher="anthropics", license_id="Apache-2.0")
    assert ok is True
    ok, _reason = quality_gate(license_id="Proprietary")
    assert ok is False
    ok, _reason = quality_gate(installs=50, license_id="MIT")
    assert ok is False
    _p = propose_skill("backup", "Backup & Recovery Agent",
                       "makash/godmode", "backup",
                       "https://github.com/makash/godmode",
                       "MIT", "RPO/RTO + restore-test pattern fits Talvenor",
                       proposals_path=_tmp_props)
    assert _p["status"] == "proposed"
    # Dedup: proposing the same repo + skill again writes no new record,
    # the earlier one is returned ("duplicate": True).
    _p2 = propose_skill("backup", "Backup & Recovery Agent",
                        "makash/godmode", "backup",
                        "https://github.com/makash/godmode",
                        "MIT", "RPO/RTO + restore-test pattern fits Talvenor",
                        proposals_path=_tmp_props)
    assert _p2.get("duplicate") is True
    with open(_tmp_props, encoding="utf-8") as f:
        assert len(json.load(f)["proposals"]) == 1
    _d = doctor()
    assert _d["skills_found"] >= 110, _d
    assert _d["problems"] == [], _d
    # Progressive-disclosure loader (2026-11-24): the index carries
    # name + description only — no full skill text is loaded at discovery.
    _idx = build_index()
    assert len(_idx) == _d["skills_found"], (_idx, _d)
    assert all(set(e) == {"name", "description", "path", "version"}
               for e in _idx), _idx[:1]
    assert all(e["name"] and e["description"] for e in _idx), _idx[:1]
    # Products + Content skills are indexed now (invisible before 2026-11-24).
    _names = {e["name"] for e in _idx}
    assert "kit-builder" in _names and "script-writer" in _names, _names
    assert "SKILL_INDEX" not in _names, _names
    _found = find_skills("backup", top_n=3)
    assert _found and _found[0]["name"] == "backup-recovery-agent", _found
    assert find_skills("xyznoskill") == []
    _loaded = load_skill("backup-recovery-agent")
    assert _loaded["name"] == "backup-recovery-agent", _loaded
    assert _loaded["content"].startswith("---\nname: backup-recovery-agent"), \
        _loaded["content"][:120]
    assert "# " in _loaded["content"], _loaded["content"][:200]
    # A pointer stem resolves to the canonical engine copy, never the pointer.
    _g = load_skill("growth-agent")
    assert _g["path"].startswith(
        "03-Content-Creation-Department/engine/skills/"), _g["path"]
    try:
        load_skill("xyznoskill")
        raise SystemExit("FAIL: load_skill accepted an unknown skill")
    except ValueError:
        pass
    _task = load_skill_for_task("backup")
    assert _task["loaded"] is not None, _task
    assert _task["loaded"]["name"] == "backup-recovery-agent", _task
    assert load_skill_for_task("xyznoskill")["loaded"] is None
    # Phase 2 hardening (2026-11-25): validation, version, execution
    # log, bare-name collision. All loads above already went to the
    # temp log (LOG_PATH was redirected at the top of this self-test).
    try:
        assert validate_index(_idx) == [], validate_index(_idx)
        for _p in _iter_skill_files():
            with open(_p, "r", encoding="utf-8") as _f:
                _head = _f.readline().strip()
            if _is_pointer_or_manifest(_p, _head):
                continue
            assert validate_skill_frontmatter(_p) == [], _p
        # Version: defaults to "1.0" (no skill file carries one yet) and
        # parses when present; a malformed version is flagged.
        assert all(e["version"] == "1.0" for e in _idx), _idx[:1]
        _vfile = os.path.join(_tmp, "versioned-skill.md")
        with open(_vfile, "w", encoding="utf-8") as _f:
            _f.write("---\nname: versioned-skill\n"
                     "description: A temp skill for the version check.\n"
                     "version: 2.3.1\n---\n\n# Versioned Skill\n\nBody.\n")
        assert _read_frontmatter(_vfile)["version"] == "2.3.1"
        assert validate_skill_frontmatter(_vfile) == [], _vfile
        _vbad = os.path.join(_tmp, "bad-version-skill.md")
        with open(_vbad, "w", encoding="utf-8") as _f:
            _f.write("---\nname: bad-version-skill\n"
                     "description: Bad version format.\n"
                     "version: v1\n---\n\n# Bad Version Skill\n\nBody.\n")
        assert validate_skill_frontmatter(_vbad) != [], _vbad
        # Execution log: a load is recorded (temp log path only).
        _loaded2 = load_skill("backup-recovery-agent")
        assert _loaded2["name"] == "backup-recovery-agent"
        assert _loaded2["version"] == "1.0", _loaded2
        with open(_tmp_log, encoding="utf-8") as _f:
            _recs = [json.loads(line) for line in _f if line.strip()]
        assert any(r["event"] == "load_skill"
                   and r.get("skill") == "backup-recovery-agent"
                   and r.get("result") == _loaded2["path"]
                   and r.get("timestamp") for r in _recs), _recs
        # Ambiguous bare name: warns, logs all candidates, loads first.
        with warnings.catch_warnings(record=True) as _w:
            warnings.simplefilter("always")
            _amb = load_skill("kit-builder")
        assert any(issubclass(w.category, UserWarning)
                   and "ambiguous" in str(w.message) for w in _w), _w
        with open(_tmp_log, encoding="utf-8") as _f:
            _recs = [json.loads(line) for line in _f if line.strip()]
        _amb_recs = [r for r in _recs
                     if r["event"] == "ambiguous_bare_name"
                     and r.get("skill") == "kit-builder"]
        assert _amb_recs and len(_amb_recs[0]["candidates"]) == 2, _recs
        assert _amb["path"] == _amb_recs[0]["candidates"][0], _amb
        _task2 = load_skill_for_task("kit-builder")
        assert _task2["loaded"]["name"] == "kit-builder", _task2
        assert _task2["ambiguous"] is True, _task2
        assert _task2["candidates"] == _amb_recs[0]["candidates"], _task2
    finally:
        LOG_PATH = _real_log
    print(f"skill_finder: OK (local={len(_local)} for 'backup', "
          f"registry={_d['skills_found']} skills, gate + proposal draft work, "
          f"index={len(_idx)} entries, loader loads full text on match only)")
