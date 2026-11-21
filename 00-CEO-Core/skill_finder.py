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

Stdlib only. No network — a human (Mira) does the online search; this module
only does local registry search + writes DRAFT proposals.
"""

import json
import os
import re

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROPOSALS_PATH = os.path.join(_MASTER_OS_DIR, "store",
                                      "skill-proposals.json")

# Local skill roots — all skill folders in the repo.
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
)

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


def _parse_skill_file(path):
    """Name + one-line description from a .md skill file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    title = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            break
    # Description: the first non-empty, non-heading paragraph line.
    description = ""
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">") or s.startswith("**"):
            continue
        description = s
        break
    return {
        "name": os.path.splitext(os.path.basename(path))[0],
        "title": title,
        "description": description,
        "path": os.path.relpath(path, _MASTER_OS_DIR),
    }


def list_local_skills(repo_dir=None):
    """Registry of all local skill files in the repo."""
    root = repo_dir or _MASTER_OS_DIR
    found = []
    for rel in SKILL_ROOTS:
        d = os.path.join(root, rel)
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".md"):
                continue
            parsed = _parse_skill_file(os.path.join(d, fname))
            if parsed is not None:
                found.append(parsed)
    return found


def find_skill_local(query, repo_dir=None):
    """Keyword search in the local registry — match in name + description."""
    words = [w.lower() for w in re.findall(r"[a-z0-9][a-z0-9_-]*",
                                           (query or "").lower())]
    if not words:
        return []
    scored = []
    for skill in list_local_skills(repo_dir):
        hay = (skill["name"] + " " + skill["title"] + " "
               + skill["description"]).lower()
        hits = sum(1 for w in words if w in hay)
        if hits:
            scored.append((hits, skill))
    scored.sort(key=lambda item: (-item[0], item[1]["name"]))
    return [skill for _, skill in scored]


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
    """Check the local skill registry: can files be read, do they have a heading."""
    problems = []
    skills = list_local_skills(repo_dir)
    for skill in skills:
        if not skill["title"]:
            problems.append(f"no heading: {skill['path']}")
        if not skill["description"]:
            problems.append(f"no description: {skill['path']}")
    return {"skills_found": len(skills), "problems": problems}


if __name__ == "__main__":
    # Manual check: TEMP paths are used — the real store is never touched.
    import tempfile

    _tmp = tempfile.mkdtemp()
    _tmp_props = os.path.join(_tmp, "skill-proposals.json")
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
    assert _d["skills_found"] >= 80, _d
    assert _d["problems"] == [], _d
    print(f"skill_finder: OK (local={len(_local)} for 'backup', "
          f"registry={_d['skills_found']} skills, gate + proposal draft work)")
