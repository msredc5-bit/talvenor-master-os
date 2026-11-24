"""§21 items 1–3 (Skill discovery, progressive disclosure, skill loading)
— Talvenor Master OS, Phase 8, Worker A.

Real code under test: 00-CEO-Core/skill_finder.py, against the REAL
112-skill index, read-only. No skill file is written, no proposal is
filed, no network, no live LLM call. The skill-execution log is
redirected to a per-test tmp file (the real logs/skill_executions.jsonl
is never touched), and any store write aimed at the real store/ is
refused by the autouse guard fixture below.
"""
import json
import os
import warnings

import pytest

import skill_finder
from skill_finder import (
    build_index,
    doctor,
    find_candidates,
    find_skill_local,
    find_skills,
    list_local_skills,
    load_skill,
    load_skill_for_task,
    validate_index,
    validate_skill_frontmatter,
)

REPO_ROOT = skill_finder._MASTER_OS_DIR


# --------------------------------------------------------------------------
# Isolation guards (local to this file — the shared conftest belongs to
# Worker C and is left untouched).
# --------------------------------------------------------------------------


def _is_real_store_path(path):
    real = os.path.realpath(os.path.join(REPO_ROOT, "store"))
    return os.path.realpath(str(path)).startswith(real + os.sep)


@pytest.fixture(autouse=True)
def _redirect_skill_log(tmp_path, monkeypatch):
    """Point the skill-execution log at a per-test tmp file."""
    monkeypatch.setattr(
        skill_finder, "LOG_PATH", str(tmp_path / "skill_executions.jsonl"))


@pytest.fixture(autouse=True)
def _guard_real_store(monkeypatch):
    """Refuse any store_io write aimed at the real store/.

    A test that touches the real store fails here instead of writing.
    """
    import store_io

    orig_write = store_io.write_json_atomic
    orig_update = store_io.update_json
    orig_append = store_io.append_json_line

    def _checked_write(path, payload):
        assert not _is_real_store_path(path), \
            f"test tried to write the REAL store: {path}"
        return orig_write(path, payload)

    def _checked_update(path, fn, default=None):
        assert not _is_real_store_path(path), \
            f"test tried to update the REAL store: {path}"
        return orig_update(path, fn, default=default)

    def _checked_append(path, record):
        assert not _is_real_store_path(path), \
            f"test tried to append to the REAL store: {path}"
        return orig_append(path, record)

    monkeypatch.setattr(store_io, "write_json_atomic", _checked_write)
    monkeypatch.setattr(store_io, "update_json", _checked_update)
    monkeypatch.setattr(store_io, "append_json_line", _checked_append)


@pytest.fixture
def temp_log(tmp_path):
    return tmp_path / "skill_executions.jsonl"


def _read_log(path):
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------- item 1 — discovery
class TestSkillDiscovery:
    def test_build_index_covers_registry(self):
        """Index count == local registry count; every entry has a name."""
        index = build_index()
        local = list_local_skills()
        assert len(index) == len(local)
        assert len(index) >= 100, f"only {len(index)} skills indexed"
        assert all(e["name"] for e in index)

    def test_find_skills_locates_backup_skill(self):
        """'backup' -> backup-recovery-agent is the top match."""
        found = find_skills("backup", top_n=3)
        assert found, "no match for 'backup'"
        assert found[0]["name"] == "backup-recovery-agent"
        assert found[0]["description"]

    def test_find_skill_local_agrees(self):
        local = find_skill_local("backup")
        assert local and local[0]["name"] == "backup-recovery-agent"

    def test_find_skills_no_match_returns_empty(self):
        assert find_skills("xyznoskill") == []
        assert find_skill_local("xyznoskill") == []

    def test_find_skills_ranks_by_keyword(self):
        found = find_skills("kit builder", top_n=5)
        names = [e["name"] for e in found]
        assert "kit-builder" in names, names

    def test_doctor_finds_skills_with_no_problems(self):
        report = doctor()
        assert report["skills_found"] == len(build_index())
        assert report["problems"] == [], report["problems"][:5]

    def test_validate_index_clean(self):
        assert validate_index(build_index()) == []

    def test_every_index_path_resolves_to_a_file(self):
        for entry in build_index():
            assert os.path.isfile(os.path.join(REPO_ROOT, entry["path"])), \
                entry["path"]


# ------------------------------------------------- item 2 — progressive disclosure
class TestProgressiveDisclosure:
    def test_index_entries_carry_metadata_only(self):
        """Discovery loads frontmatter only: exactly name/description/
        path/version — never full skill text ('content' key absent)."""
        index = build_index()
        assert index, "empty index"
        for entry in index:
            assert set(entry) == {"name", "description", "path", "version"}, \
                entry
            assert entry["description"] and "\n" not in entry["description"]
            assert entry["version"]

    def test_find_skills_returns_index_only_entries(self):
        found = find_skills("backup", top_n=3)
        assert found and all(
            set(e) == {"name", "description", "path", "version"}
            for e in found)

    def test_load_for_task_loads_only_top_match(self, tmp_path):
        """Only the top match's full text is loaded; the rest stay
        index-only (matches carry no 'content')."""
        result = load_skill_for_task("backup")
        assert result["matches"], "no matches for 'backup'"
        assert all("content" not in m for m in result["matches"])
        assert result["loaded"] is not None
        assert result["loaded"]["name"] == "backup-recovery-agent"
        assert "content" in result["loaded"]
        assert result["ambiguous"] is False

    def test_load_for_task_no_match_loads_nothing(self):
        result = load_skill_for_task("xyznoskill")
        assert result["matches"] == []
        assert result["loaded"] is None
        assert result["ambiguous"] is False
        assert result["candidates"] == []


# ------------------------------------------------------------ item 3 — loading
class TestSkillLoading:
    def test_load_skill_returns_full_text(self):
        loaded = load_skill("backup-recovery-agent")
        assert loaded["name"] == "backup-recovery-agent"
        assert loaded["description"]
        assert loaded["path"].endswith("backup-recovery-agent.md")
        assert loaded["version"] == "1.0"
        assert loaded["content"].startswith("---\nname: backup-recovery-agent")
        assert "# " in loaded["content"]

    def test_load_skill_by_explicit_path(self):
        entry = next(e for e in build_index()
                     if e["name"] == "backup-recovery-agent")
        loaded = load_skill(entry["path"])
        assert loaded["name"] == "backup-recovery-agent"
        assert loaded["path"] == entry["path"]

    def test_load_skill_unknown_raises_valueerror(self):
        with pytest.raises(ValueError):
            load_skill("xyznoskill")

    def test_load_skill_empty_name_raises_valueerror(self):
        with pytest.raises(ValueError):
            load_skill("")

    def test_pointer_stem_resolves_to_canonical_copy(self):
        """A pointer file's stem resolves to the engine copy, never
        the pointer itself."""
        loaded = load_skill("growth-agent")
        assert loaded["path"].startswith(
            "03-Content-Creation-Department/engine/skills/"), loaded["path"]
        assert "SKILL_INDEX" not in loaded["path"]

    def test_manifest_is_not_a_skill(self):
        names = {e["name"] for e in build_index()}
        assert "SKILL_INDEX" not in names

    def test_ambiguous_bare_name_warns_logs_and_loads_first(
            self, tmp_path):
        """Phase 2 behaviour: kit-builder exists in 2 copies — the
        loader warns, logs every candidate, then loads the FIRST."""
        candidates = find_candidates("kit-builder")
        assert len(candidates) == 2, candidates
        log_path = tmp_path / "skill_executions.jsonl"
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            loaded = load_skill("kit-builder")
        assert any(issubclass(w.category, UserWarning)
                   and "ambiguous" in str(w.message) for w in caught), \
            [str(w.message) for w in caught]
        records = _read_log(log_path)
        amb = [r for r in records
               if r["event"] == "ambiguous_bare_name"
               and r.get("skill") == "kit-builder"]
        assert amb, records
        assert amb[0]["candidates"] == candidates
        assert loaded["path"] == candidates[0]
        assert loaded["name"] == "kit-builder"

    def test_load_skill_for_task_reports_ambiguity(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = load_skill_for_task("kit-builder")
        assert result["loaded"]["name"] == "kit-builder"
        assert result["ambiguous"] is True
        assert result["candidates"] == find_candidates("kit-builder")

    def test_load_is_recorded_in_execution_log(self, tmp_path):
        log_path = tmp_path / "skill_executions.jsonl"
        loaded = load_skill("backup-recovery-agent")
        records = _read_log(log_path)
        hits = [r for r in records
                if r["event"] == "load_skill"
                and r.get("skill") == "backup-recovery-agent"
                and r.get("result") == loaded["path"]
                and r.get("timestamp")]
        assert hits, records

    def test_frontmatter_validation_clean_for_known_skill(self):
        path = os.path.join(
            REPO_ROOT,
            next(e["path"] for e in build_index()
                 if e["name"] == "backup-recovery-agent"))
        assert validate_skill_frontmatter(path) == []

    def test_real_store_write_guard_is_active(self, tmp_path):
        """The guard itself: a write aimed at the real store/ must
        raise before anything is written (no real file is touched)."""
        import store_io

        real_target = os.path.join(REPO_ROOT, "store", "must-not-exist.json")
        with pytest.raises(AssertionError):
            store_io.write_json_atomic(real_target, {"x": 1})
        assert not os.path.exists(real_target)
