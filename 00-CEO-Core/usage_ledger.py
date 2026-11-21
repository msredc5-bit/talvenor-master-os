"""Usage ledger — every model/tool call receipted, $0 measured
(Improvement Phase 2, modelled on Nod's ledger.ts).

Nod's pattern (~/workspace/nod-reverse/reverse-engineering.md,
ledger.ts):
  - One cost ledger (model_usage): every request / run / sign-in
    grouped by day, with model + tokens + cost + action + its trust
    basis.
  - Spending limits: monthly_usd (Nod default $200), task_usd
    (default $5 — the task stops, shows what it got + what it spent,
    and asks).
  - On reaching a limit, it stops before schedules/tasks/background
    model calls.

Here (per Boss's $0 cap):
  - monthly_cap_usd default 0.0 (read from config.json spend_cap_usd) —
    any live spend at all means the cap is exceeded.
  - task_cap_usd default 0.0 — any live spend on a task at all means
    a check-in is needed (it cannot proceed without asking Boss).
  - A mock call's cost is always $0.00 — a nonzero cost for mock kind is a
    ValueError (a mock never spends money, not even in code).
  - The ledger only measures — it blocks nothing itself; check_in_required() /
    over_monthly_cap() tell the caller, the decision is the caller's (the gate's).
  - tool_calling.call_tool() writes an entry for every call when given a
    ledger_path (kind mock/gate/error, cost 0.0) — without a ledger_path it
    writes nothing (check scripts never touch the real store).

Usage:
  ledger = UsageLedger()  # store/usage_ledger.json
  ledger.record("mock", "mock", "mock", cost_usd=0.0, action="draft_email")
  ledger.monthly_total()  # 0.0
  ledger.check_in_required("job-123")  # False — mock spend is 0
  ledger.spend_report()  # "$0.00 ..." — honest report

Status: REAL (Improvement Phase 2, 2026-11-21) — runs on the mock brain.
"""

import json
import os
from datetime import datetime, timezone

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
CONFIG_PATH = os.path.join(_MASTER_OS_DIR, "00-CEO-Core", "config.json")
DEFAULT_LEDGER_PATH = os.path.join(_STORE_DIR, "usage_ledger.json")

KINDS = ("mock", "live", "draft", "gate", "error")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _month_of(iso_ts):
    return (iso_ts or "")[:7]  # "YYYY-MM"


def _load_spend_cap_usd(config_path=None):
    try:
        with open(config_path or CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return float(config.get("spend_cap_usd", 0))
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError,
            ValueError):
        return 0.0


class UsageLedger:
    """One ledger for all model/tool usage — $0 is a measurement,
    not just an order."""

    def __init__(self, ledger_path=None, monthly_cap_usd=None,
                 task_cap_usd=0.0):
        self.ledger_path = ledger_path or DEFAULT_LEDGER_PATH
        self.monthly_cap_usd = (monthly_cap_usd
                                if monthly_cap_usd is not None
                                else _load_spend_cap_usd())
        self.task_cap_usd = float(task_cap_usd)
        self._load()

    def _load(self):
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.records = data.get("records", []) if isinstance(data, dict) else []
        except (FileNotFoundError, json.JSONDecodeError):
            self.records = []

    def _save(self):
        payload = {
            "schema": "usage-ledger-v1",
            "note": ("One ledger for every model/tool call. Monthly cap "
                     f"${self.monthly_cap_usd:g} (Boss's $0 rule). Mock "
                     "calls always cost $0.00."),
            "monthly_cap_usd": self.monthly_cap_usd,
            "task_cap_usd": self.task_cap_usd,
            "records": self.records,
        }
        parent = os.path.dirname(self.ledger_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def record(self, kind, provider, model, prompt_tokens=0,
               completion_tokens=0, cost_usd=0.0, task_id=None,
               action=None, note=""):
        """A receipt for one call. Nonzero cost for mock kind — ValueError."""
        if kind not in KINDS:
            raise ValueError(f"Unknown kind {kind!r}. Allowed: {list(KINDS)}")
        cost = float(cost_usd)
        if cost < 0:
            raise ValueError("cost_usd cannot be negative.")
        if kind == "mock" and cost != 0.0:
            raise ValueError("A mock call cannot cost money — cost must be 0.0.")
        entry = {
            "id": f"{len(self.records) + 1:06d}",
            "at": _now_iso(),
            "kind": kind,
            "provider": provider,
            "model": model,
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "cost_usd": cost,
            "task_id": task_id,
            "action": action,
            "note": note,
        }
        self.records.append(entry)
        self._save()
        return dict(entry)

    def monthly_total(self, year_month=None):
        month = year_month or _now_iso()[:7]
        return round(sum(r["cost_usd"] for r in self.records
                         if _month_of(r["at"]) == month), 6)

    def task_total(self, task_id):
        return round(sum(r["cost_usd"] for r in self.records
                         if r.get("task_id") == task_id), 6)

    def check_in_required(self, task_id, threshold_usd=None):
        """If a task's spend passes the threshold, Boss must be asked.
        Default threshold = task_cap_usd ($0 — any live spend at all
        triggers a check-in)."""
        threshold = (self.task_cap_usd if threshold_usd is None
                     else float(threshold_usd))
        return self.task_total(task_id) > threshold

    def over_monthly_cap(self, monthly_cap_usd=None):
        cap = (self.monthly_cap_usd if monthly_cap_usd is None
               else float(monthly_cap_usd))
        return self.monthly_total() > cap

    def summary(self):
        by_month = {}
        by_provider = {}
        by_kind = {}
        total = 0.0
        for record in self.records:
            month = _month_of(record["at"])
            by_month[month] = round(
                by_month.get(month, 0.0) + record["cost_usd"], 6)
            by_provider[record["provider"]] = round(
                by_provider.get(record["provider"], 0.0) + record["cost_usd"], 6)
            by_kind[record["kind"]] = by_kind.get(record["kind"], 0) + 1
            total += record["cost_usd"]
        return {
            "total_calls": len(self.records),
            "total_usd": round(total, 6),
            "monthly_cap_usd": self.monthly_cap_usd,
            "task_cap_usd": self.task_cap_usd,
            "by_month": by_month,
            "by_provider": by_provider,
            "by_kind": by_kind,
        }

    def spend_report(self):
        """Honest $ report — not invented numbers, the ledger's sums."""
        s = self.summary()
        month = _now_iso()[:7]
        lines = [
            f"Usage ledger — {month}",
            f"  Total calls: {s['total_calls']}",
            f"  Total spent: ${s['total_usd']:.2f} (cap ${s['monthly_cap_usd']:.2f}/mo)",
            f"  This month: ${self.monthly_total():.2f}",
            f"  Over monthly cap: {'YES — STOP' if self.over_monthly_cap() else 'no'}",
            f"  By kind: {s['by_kind'] or '(none)'}",
            f"  By provider: {s['by_provider'] or '(none)'}",
        ]
        return "\n".join(lines)


if __name__ == "__main__":
    # Manual check: in a TEMP file, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_ledger = os.path.join(tmp_dir, "usage_ledger-test.json")

    ledger = UsageLedger(ledger_path=tmp_ledger)
    assert ledger.monthly_cap_usd == 0.0, ledger.monthly_cap_usd
    assert ledger.monthly_total() == 0.0
    assert ledger.check_in_required("job-1") is False
    assert ledger.over_monthly_cap() is False

    # Mock call — $0, a receipt is written.
    e = ledger.record("mock", "mock", "mock", cost_usd=0.0,
                      task_id="job-1", action="draft_email")
    assert e["cost_usd"] == 0.0 and ledger.monthly_total() == 0.0
    assert ledger.check_in_required("job-1") is False

    # Nonzero cost on a mock — ValueError (a mock never spends money).
    try:
        ledger.record("mock", "mock", "mock", cost_usd=0.01)
        raise SystemExit("FAIL: mock call with a cost was recorded")
    except ValueError:
        pass

    # Live cost — check-in trips (cap $0).
    ledger.record("live", "openrouter", "openrouter/free",
                  prompt_tokens=100, completion_tokens=50, cost_usd=0.02,
                  task_id="job-2", action="draft_email")
    assert ledger.monthly_total() == 0.02
    assert ledger.check_in_required("job-2") is True
    assert ledger.over_monthly_cap() is True
    assert ledger.task_total("job-2") == 0.02
    assert ledger.task_total("job-1") == 0.0

    s = ledger.summary()
    assert s["total_calls"] == 2 and s["total_usd"] == 0.02
    assert s["by_kind"] == {"mock": 1, "live": 1}
    report = ledger.spend_report()
    assert "$0.02" in report and "YES — STOP" in report
    print("usage_ledger: OK (mock $0, mock cost rejected, live cost trips "
          "check-in + monthly cap, summary/report)")
