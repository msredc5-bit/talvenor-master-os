"""Vault — finished-task results as files (D3, 2026-11-21).

The promise in store/vault/README.md: when a task finishes, its result
lives here as a `<date>-<business>-<short-title>.md` file. Until now
no code wrote to the vault — this helper is the first writer.

Rules (from the README):
  - Text files only — no video file lives here (that
    path is written in the result text).
  - No file is deleted / overwritten — on a name clash, a -2, -3...
    version is written.
  - File name: `<date>-<business>-<short-title>.md`.

Usage (from run_office.py drain):
  from vault import write_result
  path = write_result(store_dir, record)  # record holds result + drained_at

Stdlib only. No network, no send, no spend.
"""

import json
import os
import re
from datetime import datetime, timezone

VAULT_DIRNAME = "vault"


def _slug(text, max_len=40):
    """Title -> filename-safe short slug (lowercase, joined with -)."""
    slug = re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")
    return slug[:max_len].strip("-") or "task"


def vault_path_for(store_dir, record, drained_at=None):
    """The vault file path for this record (nothing is written — only the name is decided)."""
    vault_dir = os.path.join(store_dir, VAULT_DIRNAME)
    when = drained_at or record.get("drained_at") or record.get("queued_at")
    try:
        date = datetime.fromisoformat(
            str(when).replace("Z", "+00:00")).date().isoformat()
    except (TypeError, ValueError):
        date = datetime.now(timezone.utc).date().isoformat()
    business = re.sub(r"[^a-z0-9-]+", "-",
                      str(record.get("business") or "agency").lower())
    name = f"{date}-{business}-{_slug(record.get('title'))}.md"
    return os.path.join(vault_dir, name)


def _render_result(result):
    """result (str / dict / None) -> text fit to write as markdown."""
    if result is None:
        return "(no result recorded)"
    if isinstance(result, str):
        return result
    return json.dumps(result, indent=2, ensure_ascii=False)


def write_result(store_dir, record):
    """Write one done/failed task's result to the vault. Returns: file path.

    If a file with the same name exists, it is not overwritten — a -2, -3... version is written.
    """
    path = vault_path_for(store_dir, record)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        stem, ext = os.path.splitext(path)
        n = 2
        while os.path.exists(f"{stem}-{n}{ext}"):
            n += 1
        path = f"{stem}-{n}{ext}"
    result = record.get("result")
    status = record.get("status", "?")
    lines = [
        f"# {record.get('title', '(untitled)')}",
        "",
        f"- Business: {record.get('business', '?')}",
        f"- Type: {record.get('type', '?')}",
        f"- Status: {status}",
        f"- Task id: {record.get('id', '?')}",
        f"- Queued: {record.get('queued_at', '?')}",
        f"- Drained: {record.get('drained_at', '?')}",
        "",
        "## Result",
        "",
        _render_result(result),
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


if __name__ == "__main__":
    # Manual check: in a TEMP dir, the real store is never touched.
    import tempfile

    tmp = tempfile.mkdtemp()
    record = {
        "id": "abc123",
        "business": "agency",
        "type": "research",
        "title": "Verify the Talvenor booking link is live!",
        "status": "done",
        "queued_at": "2026-11-21T10:00:00+00:00",
        "drained_at": "2026-11-21T10:05:00+00:00",
        "result": "VERIFIED LIVE — booking page loads.",
    }
    p1 = write_result(tmp, record)
    assert p1.endswith("2026-11-21-agency-verify-the-talvenor-booking-link-is-live.md"), p1
    with open(p1, encoding="utf-8") as f:
        assert "VERIFIED LIVE" in f.read()
    p2 = write_result(tmp, record)  # same name -> not overwritten, -2 version
    assert p2.endswith("-2.md"), p2
    assert os.path.exists(p1) and os.path.exists(p2)
    print(f"vault: OK (wrote {os.path.basename(p1)} + versioned {os.path.basename(p2)})")
