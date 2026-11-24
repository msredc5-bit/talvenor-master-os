"""CRM dry-run wrapper — Talvenor Master OS, local-first Phase 6.

Wraps the existing ``00-CEO-Core/crm_adapter.py`` (already dry-run
only: ``health()`` is NOT CONNECTED, write methods validate and
return the exact would-be payload, write nothing anywhere, no
network). This module does NOT reimplement payload building — it
calls the adapter's real dry-run methods.

``dry_run_upsert(prospect)`` returns::

  {"status": "ok", "dry_run": True,
   "payload": {<would-be upsert payload>}, "live": False}

On a bad prospect the adapter raises ValueError; that becomes::

  {"status": "error", "dry_run": True, "payload": None,
   "live": False, "error": <message>}

It writes nothing to any live system, Sheet, or n8n. The adapter
is imported lazily by path (same pattern the department managers
use for 00-CEO-Core).

Stdlib only. No network, no keys, no spend.
"""

from __future__ import annotations

import importlib.util
import os

__all__ = ["dry_run_upsert", "health"]


def _load_crm_adapter():
    """Lazy path import of 00-CEO-Core/crm_adapter.py."""
    here = os.path.dirname(os.path.abspath(__file__))
    ceo_core = os.path.dirname(here)
    path = os.path.join(ceo_core, "crm_adapter.py")
    spec = importlib.util.spec_from_file_location(
        "lead_chain_crm_adapter", path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load crm_adapter.py from %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def health():
    """CRM health, straight from the adapter: NOT CONNECTED."""
    return _load_crm_adapter().health()


def dry_run_upsert(prospect):
    """Dry-run upsert of one prospect via the real CRM adapter.

    Returns {"status": "ok", "dry_run": True, "payload": {...},
    "live": False}. Writes nothing anywhere.
    """
    try:
        adapter = _load_crm_adapter()
        payload = adapter.lead_upsert_payload(prospect)
        return {"status": "ok", "dry_run": True,
                "payload": payload, "live": False}
    except Exception as exc:  # noqa: BLE001 — validation failure is data
        return {"status": "error", "dry_run": True, "payload": None,
                "live": False,
                "error": "%s: %s" % (type(exc).__name__, exc)}


if __name__ == "__main__":
    # Self-test — TEST data only, no I/O, no live calls.
    import json

    h = health()
    assert h["status"] == "NOT CONNECTED" and h["live"] is False

    prospect = {"business_name": "TEST Plumbing LLC",
                "city": "Drexel Hill", "state": "PA",
                "website": "https://test-plumbing.example",
                "domain": "test-plumbing.example",
                "email": "office@test-plumbing.example",
                "phone": "+1-555-010-0001",
                "score": 85, "tier": "Tier 1",
                "source": "TEST fixture"}
    result = dry_run_upsert(prospect)
    assert result["status"] == "ok", result
    assert result["dry_run"] is True
    assert result["live"] is False
    payload = result["payload"]
    assert payload["dry_run"] is True
    assert payload["table"] == "leads"
    assert payload["action"] == "upsert"
    assert payload["key"] == {"domain": "test-plumbing.example"}
    assert payload["fields"]["business_name"] == "TEST Plumbing LLC"
    assert payload["fields"]["state"] == "PA"
    assert json.dumps(payload)  # serializable — it IS the would-be body

    bad = dry_run_upsert({"business_name": "No State"})
    assert bad["status"] == "error" and bad["payload"] is None
    assert bad["live"] is False
    keyless = dry_run_upsert({"business_name": "X", "state": "PA"})
    assert keyless["status"] == "error"
    print("crm_dryrun: OK (adapter health NOT CONNECTED; dry-run "
          "payload via real adapter, serializable, live=False; "
          "bad prospects fail cleanly; nothing written)")
