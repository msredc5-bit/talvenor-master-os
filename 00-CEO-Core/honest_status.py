"""Honest-status reader — read-only access to the live business numbers
(Phase 2, Unified Business OS).

Single source of truth: ``00-CEO-Core/config.json`` -> ``"honest_status"``
(first_mails_sent, paying_clients, email_outreach). The same file is
already read by scripts/sync_status.py, 00-CEO-Core/goals.py and
scripts/sync_engines.py — this module is the one small reader the
department agents use, so no agent keeps its own hardcoded copy of a
number that changes (first mails 163, paying clients 0, ...).

Rules:
  - READ ONLY. This module never writes, never creates a file, never
    invents a number.
  - A missing file, corrupt JSON, or missing key returns the string
    "UNKNOWN" — callers must surface that marker, never substitute a
    hardcoded number of their own.
  - No number lives in this file. The values come only from config.json.

Stdlib only. No network, no send, no publish, no spend.
"""

import json
import os

UNKNOWN = "UNKNOWN"


def _config_path(config_path=None):
    """config.json next to this module, unless a path is given (tests)."""
    if config_path:
        return config_path
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "config.json")


def read_honest_status(config_path=None):
    """The honest_status dict from config.json, or {} when unreadable."""
    try:
        with open(_config_path(config_path), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    honest = data.get("honest_status")
    return honest if isinstance(honest, dict) else {}


def first_mails_sent(config_path=None):
    """Total first mails sent (int), or "UNKNOWN" when no source has it."""
    value = read_honest_status(config_path).get("first_mails_sent")
    return value if isinstance(value, int) else UNKNOWN


def paying_clients(config_path=None):
    """Paying clients (int), or "UNKNOWN" when no source has it."""
    value = read_honest_status(config_path).get("paying_clients")
    return value if isinstance(value, int) else UNKNOWN


def email_outreach(config_path=None):
    """Email outreach state text, or "UNKNOWN" when no source has it."""
    value = read_honest_status(config_path).get("email_outreach")
    return value if isinstance(value, str) and value else UNKNOWN


if __name__ == "__main__":
    # Self-test — TEMP files only, the real config is only read, never written.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_config = os.path.join(tmp_dir, "config.json")
    with open(tmp_config, "w", encoding="utf-8") as f:
        json.dump({"honest_status": {
            "first_mails_sent": 162,
            "paying_clients": 0,
            "email_outreach": "PAUSED since 2026-11-14",
        }}, f)
    assert first_mails_sent(tmp_config) == 162
    assert paying_clients(tmp_config) == 0
    assert email_outreach(tmp_config) == "PAUSED since 2026-11-14"
    # Missing keys / missing file / corrupt file -> UNKNOWN, never a guess.
    with open(tmp_config, "w", encoding="utf-8") as f:
        json.dump({"honest_status": {}}, f)
    assert first_mails_sent(tmp_config) == UNKNOWN
    assert paying_clients(tmp_config) == UNKNOWN
    assert email_outreach(tmp_config) == UNKNOWN
    assert first_mails_sent(os.path.join(tmp_dir, "no-such.json")) == UNKNOWN
    with open(tmp_config, "w", encoding="utf-8") as f:
        f.write("{not json")
    assert read_honest_status(tmp_config) == {}
    # The real config reads cleanly and matches the known state.
    assert first_mails_sent() == 163
    assert paying_clients() == 0
    print("honest_status: OK (reads config.json honest_status; "
          "missing/corrupt -> UNKNOWN)")
