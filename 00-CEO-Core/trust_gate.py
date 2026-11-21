"""Trust gate — Nod-style approval gate as code (Improvement Phase 1).

Nod's systematic pattern (~/workspace/nod-reverse/reverse-engineering.md,
trust.ts + approvals.ts — with file:line evidence):
  - One server-side trust check: only the owner's (Boss's) own words are
    permission; everything else is data, never permission.
  - The checker must quote Boss's exact words; the server verifies that quote
    — whether the quoted words were really written/spoken by Boss.
  - Reads / drafts run free; writes / commits need Boss's words.
  - A confirmation is bound to one exact action + arguments; it runs once;
    a failed / interrupted action is UNCERTAIN — never re-run;
    a repeat needs a new confirmation.

In this file (Python, a rule-based classifier first — no model judge,
no live call, stdlib only):
  1. trust_check() — read/write split + quote verification + coverage +
     standing-rule deny (spend cap $0, dental/medical DQ).
  2. ConfirmationStore — run-once confirmation, wired to the ApprovalGateway
     (the gateway is the only truth of approval; the confirmation record
     is linked by approval_id).
  3. Dispatcher wiring — tool_calling.call_tool()'s gated branch
     runs trust_check: on deny, "blocked-trust" (no approval
     is recorded, nothing executes); otherwise PENDING as before,
     with the trust decision attached to the result.

Standing rules (read from config.json, Boss's decision):
  - Spend cap $0 — spend above the cap is a trust deny (this path is not
    used in any check; existing behaviour does not change).
  - Dental / medical / patient-health — hard DQ, trust deny.
  - Email PAUSED (2026-11-14) — not a deny: decision "ask", with PAUSED
    written in the note; the PENDING approval is the restart path, so
    check_live_tools.py's "gmail_send -> pending-approval" is unchanged.
  - The gateway is the final authority: even when trust says "allow", the gated
    handler does not execute — nothing moves without Boss's exact gate word.
    There is no auto-approve path in this repo, not even in the code.

Usage:
  from trust_gate import trust_check, ConfirmationStore
  d = trust_check("send", {"to": "a@b.com", "subject": "Hi", "body": ".."},
                  owner_words=["Day 4 batch send"],
                  owner_source="Boss (chat 2026-11-21): Day 4 batch send")
  # d["decision"] = "allow" | "ask" | "deny"
  store = ConfirmationStore()  # store/confirmations.json
  c = store.create("send", {"to": "a@b.com"}, "Send the Day 4 batch?", "Main CEO Bot")
  store.approve(c["id"], gate_word="send")
  store.execute_once(c["id"], runner)  # runner(canonical_args) -> result

Status: REAL (Improvement Phase 1, 2026-11-21) — runs on the mock brain, no
live brain / API key / network needed. The brain is still mock.
"""

import json
import os
import re
import uuid
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Paths / config
# ---------------------------------------------------------------------------

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(_MASTER_OS_DIR, "00-CEO-Core")
_STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
CONFIG_PATH = os.path.join(CEO_CORE_DIR, "config.json")
DEFAULT_CONFIRMATIONS_PATH = os.path.join(_STORE_DIR, "confirmations.json")

# Commit = what changes something outside (sending / publishing / spending / deleting / booking / paying).
COMMIT_ACTIONS = ("send", "publish", "spend", "delete", "upload",
                  "book", "pay", "order", "cancel")
# Read = only reading / drafting — runs free.
READ_ACTIONS = ("read", "draft", "status", "search", "list")

# Gate word -> action (a mirror of human_approval_gateway.GATE_WORD_FOR_ACTION;
# duplicated here to avoid an import cycle — the two must stay identical, and
# check_gate.py verifies that).
GATE_WORD_FOR_ACTION = {
    "send": ("send", "পাঠাও"),
    "publish": ("post it", "post all"),
    "spend": ("go",),
    "delete": ("go",),
    "upload": ("upload it",),
}

# Hard-DQ niches (Boss's permanent decision — never a target).
EXCLUDED_NICHE_WORDS = ("dental", "dentist", "medical", "patient-health")

# The explicit words for an email restart (the only override that lifts PAUSED).
EMAIL_RESTART_MARKERS = ("email restart", "email পাঠাও", "email চালু")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_config(config_path=None):
    path = config_path or CONFIG_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _spend_cap_usd(config):
    try:
        return float(config.get("spend_cap_usd", 0))
    except (TypeError, ValueError):
        return 0.0


def _email_paused(config):
    status = (config.get("honest_status") or {}).get("email_outreach", "")
    return isinstance(status, str) and status.strip().upper().startswith("PAUSED")


def _standing_owner_text(config):
    """Boss's standing words (gate words + standing rules) — the default source
    for quote verification. Only the words written here count as a standing source."""
    words = (config.get("gates") or {}).get("words") or {}
    lines = ["Boss's gate words:"]
    for word, meaning in sorted(words.items()):
        lines.append(f"- {word!r} = {meaning}")
    lines.append("Standing rules: spend cap is $0. "
                 "Email sending is PAUSED since 2026-11-14. "
                 "Dental / medical / patient-health never a target. "
                 "No gated action moves without Boss's exact gate word.")
    return "\n".join(lines)


def _normalize(text):
    """Normalize whitespace for quote matching (case-sensitive — Boss's
    exact words must match; a capitalisation mistake does not count)."""
    return re.sub(r"\s+", " ", str(text or "")).strip()


def verify_quote(quote, source_text):
    """Whether a quote really is verbatim in the source. An empty quote never
    verifies (Nod: without a quote, ask; do not run)."""
    q = _normalize(quote)
    if not q:
        return False
    return q in _normalize(source_text)


def _args_text(args):
    """All string values of the args together — for the niche scan + coverage."""
    parts = []
    for value in (args or {}).values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, (dict, list)):
            parts.append(json.dumps(value, ensure_ascii=False))
        else:
            parts.append(str(value))
    return " ".join(parts)


def _material_targets(action, args, tool_name=None):
    """This action's material target — at least one of these must be in the quote,
    otherwise the quote does not cover this action. A generic word (e.g.
    just "email") is not a target — only a specific value like the recipient /
    event / amount is a target."""
    args = args or {}
    targets = []
    if action == "send":
        to = (args.get("to") or "").strip()
        if to:
            targets.append(to)
            if "@" in to:
                targets.append(to.split("@", 1)[1])  # a domain also counts
    if tool_name == "n8n_trigger":
        event = (args.get("event") or "").strip()
        if event:
            targets.append(event)
        targets.append("n8n")
    if action == "publish":
        for key in ("platform", "asset", "caption"):
            value = (args.get(key) or "").strip()
            if value:
                targets.append(value[:80])
        targets.append("publish")
    if action == "spend":
        amount = args.get("amount_usd")
        if amount is not None:
            targets.append(str(amount))
        purpose = (args.get("purpose") or "").strip()
        if purpose:
            targets.append(purpose)
    if action == "delete":
        for key in ("target", "detail", "id", "name"):
            value = (args.get(key) or "").strip()
            if value:
                targets.append(value[:80])
    return targets


def _covers(action, args, quotes_text, tool_name=None):
    """Whether the verified quotes cover this action: gate word +
    at least one material target — both are needed (rule-based)."""
    allowed_words = GATE_WORD_FOR_ACTION.get(action)
    if not allowed_words:
        # A commit action not in the gate-word table (upload/book/pay/...) —
        # the rule-based classifier does not know it, so it cannot count as covered: ask.
        return False, f"No gate word mapping for action {action!r} — ask Boss."
    text = _normalize(quotes_text)
    if not any(_normalize(w) in text for w in allowed_words):
        return False, (f"Quote does not contain the gate word for "
                       f"{action!r} {list(allowed_words)} — ask Boss.")
    targets = _material_targets(action, args, tool_name=tool_name)
    if targets and not any(_normalize(t) in text for t in targets):
        return False, (f"Quote does not name any material target "
                       f"{targets} for {action!r} — ask Boss.")
    return True, "Quote covers the action (gate word + material target)."


# ---------------------------------------------------------------------------
# trust_check() — one server-side check (modelled on Nod's trust.ts)
# ---------------------------------------------------------------------------

def trust_check(action, args=None, owner_words=None, owner_source=None,
                config=None, tool_name=None, config_path=None):
    """The trust decision before running an action.

    Decision:
      "allow" — Boss's quote verified + it covers the action.
      "ask"   — Boss's words are needed (no quote / does not cover / PAUSED note).
      "deny"  — the quote did not verify, or a standing rule (spend cap / DQ niche)
                explicitly refused. Deny means: no approval is recorded either.

    No decision executes a gated handler — execution happens only after
    Boss's exact gate word in the ApprovalGateway, in the future live path.
    """
    args = args or {}
    cfg = config if isinstance(config, dict) else _load_config(config_path)
    action = (action or "").strip().lower()

    # 1. Read / draft — runs free (Nod: reads/drafts run free).
    if action in READ_ACTIONS:
        return {
            "decision": "allow",
            "action": action,
            "basis": ["Reads and drafts run free — no owner words needed."],
            "reason": f"{action!r} is a read/draft action.",
            "quotes_verified": [],
        }

    # 2. Unknown action — the classifier does not know it: ask, do not deny (fail-safe:
    #    if unknown, ask Boss; do not decide yourself).
    if action not in COMMIT_ACTIONS:
        return {
            "decision": "ask",
            "action": action,
            "basis": [f"Unknown action {action!r} — no rule covers it."],
            "reason": "Unknown action — ask Boss.",
            "quotes_verified": [],
        }

    # 3. Standing-rule deny — these win over everything (Nod: a rule to
    #    ask first wins over everything).
    if action == "spend":
        amount = args.get("amount_usd")
        cap = _spend_cap_usd(cfg)
        if isinstance(amount, (int, float)) and not isinstance(amount, bool):
            if amount > cap:
                return {
                    "decision": "deny",
                    "action": action,
                    "basis": [f"Spend cap is ${cap:g} — ${amount:g} exceeds it."],
                    "reason": "Standing rule: spend cap $0 — no spend authorized.",
                    "quotes_verified": [],
                }
        # no amount, or 0 — no decision without a quote; it falls to ask.

    args_text = _args_text(args).lower()
    for word in EXCLUDED_NICHE_WORDS:
        if word in args_text:
            return {
                "decision": "deny",
                "action": action,
                "basis": [f"Excluded niche {word!r} — dental/medical is a hard DQ."],
                "reason": "Standing rule: dental/medical/patient-health is never a target.",
                "quotes_verified": [],
            }

    notes = []
    if action == "send" and _email_paused(cfg):
        # Any send tool (gmail_send, n8n_trigger, ...) — the PAUSED
        # note is not only gmail_send's; while email is off, the same
        # truth applies to every send.
        quotes_so_far = " ".join(owner_words or [])
        restarted = any(m in _normalize(quotes_so_far).lower()
                        for m in EMAIL_RESTART_MARKERS)
        if not restarted:
            notes.append("Email sending is PAUSED since 2026-11-14 — "
                         "the PENDING approval is the restart path; "
                         "execution stays blocked until Boss restarts.")

    # 4. No Boss words — ask (Nod: without a quote, ask; do not run).
    owner_words = [w for w in (owner_words or []) if _normalize(w)]
    if not owner_words:
        return {
            "decision": "ask",
            "action": action,
            "basis": ["No owner words provided — Boss's words are needed."] + notes,
            "reason": "No owner words — ask Boss.",
            "quotes_verified": [],
        }

    # 5. Quote verification — every quote must be verbatim in the source.
    source = owner_source if owner_source is not None else _standing_owner_text(cfg)
    verified = []
    for quote in owner_words:
        if not verify_quote(quote, source):
            return {
                "decision": "deny",
                "action": action,
                "basis": [f"Quote not found verbatim in the named source: {quote!r}"],
                "reason": "Unverified quote — words the owner never wrote.",
                "quotes_verified": verified,
            }
        verified.append(quote)

    # 6. Coverage — whether the quote covers this exact action.
    quotes_text = " ".join(verified)
    covered, cover_reason = _covers(action, args, quotes_text, tool_name=tool_name)
    if not covered:
        return {
            "decision": "ask",
            "action": action,
            "basis": [cover_reason] + notes,
            "reason": "Quote does not cover this action — ask Boss.",
            "quotes_verified": verified,
        }

    return {
        "decision": "allow",
        "action": action,
        "basis": [cover_reason] + notes,
        "reason": "Owner words verified verbatim and cover the action.",
        "quotes_verified": verified,
    }


# ---------------------------------------------------------------------------
# ConfirmationStore — run-once confirmation (modelled on Nod's approvals.ts)
# ---------------------------------------------------------------------------

CONFIRMATION_STATUSES = ("asked", "approved", "declined", "executed",
                         "expired", "uncertain")


def _canonical_args(args):
    """Exact action + arguments — canonical JSON (key order is fixed, so the
    same args always give the same string)."""
    return json.dumps(args or {}, sort_keys=True, ensure_ascii=False)


class ConfirmationStore:
    """Run-once confirmation — wired to the ApprovalGateway.

    One confirmation = one exact action + exact args + one question.
    The gateway is the truth of approval: create() writes an approval request
    to the gateway (linked by approval_id); approve() also approves the gateway
    record (the gate word must match). execute_once() runs the runner exactly once
    with the canonical args; on failure the status is UNCERTAIN
    — never re-run again; a repeat needs a new confirmation.
    """

    def __init__(self, confirmations_path=None, approvals_path=None):
        self.confirmations_path = (
            confirmations_path or DEFAULT_CONFIRMATIONS_PATH)
        self.approvals_path = approvals_path
        self._load()

    def _load(self):
        try:
            with open(self.confirmations_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.records = data.get("records", []) if isinstance(data, dict) else []
        except (FileNotFoundError, json.JSONDecodeError):
            self.records = []

    def _save(self):
        payload = {
            "schema": "confirmations-v1",
            "note": ("One confirmation = one exact action + args, runs once. "
                     "Failed/interrupted = UNCERTAIN, never re-run. "
                     "A repeat needs a new confirmation."),
            "records": self.records,
        }
        parent = os.path.dirname(self.confirmations_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.confirmations_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def create(self, action, args, question, requested_by="Main CEO Bot"):
        """A new confirmation + a linked approval request in the gateway.

        Only these 4 gated actions of the gateway (send / publish / spend /
        delete) — upload's gate word exists in the gateway, but
        the confirmation store has no upload path yet (a request can be made
        in the gateway, but not a confirmation here).
        """
        if action not in ("send", "publish", "spend", "delete"):
            raise ValueError(
                f"Confirmation needs a gateway-gated action, got "
                f"{action!r}. Allowed: send, publish, spend, delete.")
        from human_approval_gateway import ApprovalGateway  # noqa: PLC0415
        gateway = ApprovalGateway(approvals_path=self.approvals_path)
        approval = gateway.request(
            action,
            detail=f"confirmation: {question}",
            requested_by=requested_by,
        )
        record = {
            "id": uuid.uuid4().hex[:12],
            "action": action,
            "args": args or {},
            "args_canonical": _canonical_args(args),
            "question": question,
            "requested_by": requested_by,
            "status": "asked",
            "approval_id": approval["id"] if approval else None,
            "gate_word": None,
            "requested_at": _now_iso(),
            "decided_at": None,
            "executed_at": None,
            "result": None,
            "error": None,
        }
        self.records.append(record)
        self._save()
        return dict(record)

    def get(self, confirmation_id):
        for record in self.records:
            if record["id"] == confirmation_id:
                return dict(record)
        raise KeyError(f"No confirmation with id {confirmation_id!r}")

    def pending(self):
        self.sweep_expired()
        return [dict(r) for r in self.records if r["status"] == "asked"]

    def sweep_expired(self):
        """Mark 'asked' confirmations past their TTL as 'expired'.

        TTL: human_approval_gateway.APPROVAL_TTL_MINUTES (20 minutes —
        recorded chat-card expiry, MEMORY.md). Linked gateway
        record expires in the same sweep, so the two stores agree.
        Returns: the ids of the confirmations that expired.
        """
        from human_approval_gateway import (  # noqa: PLC0415
            APPROVAL_TTL_MINUTES, ApprovalGateway)
        now = datetime.now(timezone.utc)
        expired_ids = []
        for record in self.records:
            if record.get("status") != "asked":
                continue
            try:
                asked = datetime.fromisoformat(
                    str(record.get("requested_at")).replace("Z", "+00:00"))
            except (TypeError, ValueError):
                continue  # if the timestamp cannot be read, it is not expired
            if now - asked > timedelta(minutes=APPROVAL_TTL_MINUTES):
                record["status"] = "expired"
                record["decided_at"] = now.isoformat()
                expired_ids.append(record["id"])
        if expired_ids:
            self._save()
            try:
                ApprovalGateway(
                    approvals_path=self.approvals_path).sweep_expired()
            except Exception:  # noqa: BLE001 — the gateway sweep must never break a confirmation
                pass
        return expired_ids

    def approve(self, confirmation_id, gate_word, decided_by="Boss"):
        """When Boss approves — the gate word must match. The gateway record is
        also approved (with the same gate word); if the gateway fails, the confirmation
        stays 'asked' (no half-state). An expired confirmation
        cannot be approved — sweep_expired() runs first."""
        self.sweep_expired()
        record = self._find(confirmation_id)
        if record["status"] == "expired":
            raise ValueError(
                f"Confirmation {confirmation_id} expired — ask Boss for "
                "a fresh confirmation.")
        if record["status"] != "asked":
            raise ValueError(
                f"Confirmation {confirmation_id} already decided: "
                f"{record['status']}")
        allowed = GATE_WORD_FOR_ACTION.get(record["action"])
        if allowed is None:
            raise ValueError(
                f"No gate word mapping for action {record['action']!r}")
        if gate_word not in allowed:
            raise ValueError(
                f"Gate word {gate_word!r} does not approve action "
                f"{record['action']!r}. Allowed: {list(allowed)}")
        if record.get("approval_id"):
            from human_approval_gateway import ApprovalGateway  # noqa: PLC0415
            gateway = ApprovalGateway(approvals_path=self.approvals_path)
            gateway.approve(record["approval_id"], gate_word=gate_word,
                            decided_by=decided_by)
        record["status"] = "approved"
        record["gate_word"] = gate_word
        record["decided_at"] = _now_iso()
        self._save()
        return dict(record)

    def decline(self, confirmation_id, decided_by="Boss"):
        record = self._find(confirmation_id)
        if record["status"] != "asked":
            raise ValueError(
                f"Confirmation {confirmation_id} already decided: "
                f"{record['status']}")
        if record.get("approval_id"):
            from human_approval_gateway import ApprovalGateway  # noqa: PLC0415
            gateway = ApprovalGateway(approvals_path=self.approvals_path)
            try:
                gateway.reject(record["approval_id"], decided_by=decided_by)
            except ValueError:
                pass  # gateway record already decided — the confirmation is the truth
        record["status"] = "declined"
        record["decided_at"] = _now_iso()
        self._save()
        return dict(record)

    def expire(self, confirmation_id):
        record = self._find(confirmation_id)
        if record["status"] != "asked":
            raise ValueError(
                f"Confirmation {confirmation_id} already decided: "
                f"{record['status']}")
        record["status"] = "expired"
        record["decided_at"] = _now_iso()
        self._save()
        return dict(record)

    def execute_once(self, confirmation_id, runner):
        """Run the exact saved action + args exactly once.

        runner(canonical_args_dict) -> result (any JSON-able value).
        Success -> "executed". Exception / interruption -> "uncertain"
        (Never re-run again — "may have run, check the app"). "executed"
        or "uncertain" — executing again raises ValueError; a repeat needs a
        new confirmation.
        """
        record = self._find(confirmation_id)
        if record["status"] != "approved":
            raise ValueError(
                f"Confirmation {confirmation_id} is {record['status']!r} — "
                "only an approved confirmation can execute, exactly once.")
        args = json.loads(record["args_canonical"])
        try:
            result = runner(args)
        except Exception as exc:  # noqa: BLE001 — fail = uncertain, never re-run
            record["status"] = "uncertain"
            record["error"] = f"{type(exc).__name__}: {exc}"
            record["executed_at"] = _now_iso()
            self._save()
            raise ValueError(
                f"Confirmation {confirmation_id} FAILED during execution — "
                f"status is now UNCERTAIN and it must NEVER be re-run. "
                f"Error: {exc}") from exc
        record["status"] = "executed"
        record["result"] = (str(result)[:500] if result is not None else None)
        record["executed_at"] = _now_iso()
        self._save()
        return dict(record)

    def _find(self, confirmation_id):
        for record in self.records:
            if record["id"] == confirmation_id:
                return record
        raise KeyError(f"No confirmation with id {confirmation_id!r}")


if __name__ == "__main__":
    # Manual check: in a TEMP file, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_conf = os.path.join(tmp_dir, "confirmations-test.json")
    tmp_appr = os.path.join(tmp_dir, "approvals-test.json")

    # 1. Read/draft free.
    assert trust_check("read", {})["decision"] == "allow"
    assert trust_check("draft", {})["decision"] == "allow"
    # 2. No quote -> ask.
    assert trust_check("send", {"to": "a@b.com"})["decision"] == "ask"
    # 3. Above the spend cap -> deny.
    assert trust_check("spend", {"amount_usd": 5, "purpose": "ads"})["decision"] == "deny"
    # 4. Dental -> deny.
    assert trust_check("send", {"to": "x@dental.com"})["decision"] == "deny"
    # 5. Wrong quote -> deny.
    d = trust_check("send", {"to": "a@b.com"},
                    owner_words=["Day 4 batch send"],
                    owner_source="Boss: today is off")
    assert d["decision"] == "deny", d
    # 6. Correct quote + coverage -> allow.
    d = trust_check("send", {"to": "a@b.com", "subject": "Hi", "body": "x"},
                    owner_words=["Day 4 batch send — email a@b.com"],
                    owner_source="Boss (chat): Day 4 batch send — email a@b.com")
    assert d["decision"] == "allow", d

    # 7. Confirmation lifecycle: create -> approve -> execute once.
    store = ConfirmationStore(confirmations_path=tmp_conf,
                              approvals_path=tmp_appr)
    c = store.create("send", {"to": "a@b.com", "subject": "Hi"},
                     "Send the Day 4 batch?", "Main CEO Bot")
    assert c["status"] == "asked" and c["approval_id"]
    ran = []
    store.approve(c["id"], gate_word="send")
    out = store.execute_once(c["id"], lambda a: ran.append(a) or "sent-ok")
    assert out["status"] == "executed" and ran == [{"subject": "Hi", "to": "a@b.com"}]
    try:
        store.execute_once(c["id"], lambda a: "again")
        raise SystemExit("FAIL: re-execution was allowed")
    except ValueError:
        pass
    # 8. Fail -> uncertain, never re-run.
    c2 = store.create("send", {"to": "b@c.com"}, "Test?", "Main CEO Bot")
    store.approve(c2["id"], gate_word="send")
    def _boom(_args):
        raise RuntimeError("network down mid-send")
    try:
        store.execute_once(c2["id"], _boom)
        raise SystemExit("FAIL: failed execution did not raise")
    except ValueError as exc:
        assert "UNCERTAIN" in str(exc)
    assert store.get(c2["id"])["status"] == "uncertain"
    try:
        store.execute_once(c2["id"], lambda a: "retry")
        raise SystemExit("FAIL: uncertain confirmation re-ran")
    except ValueError:
        pass
    print("trust_gate: OK (read free, ask, spend/dental deny, quote verify, "
          "run-once, uncertain never re-runs)")
