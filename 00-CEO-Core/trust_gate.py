"""Trust gate — Nod-style approval gate as code (Improvement Phase 1).

Nod-এর systematic pattern (~/workspace/nod-reverse/reverse-engineering.md,
trust.ts + approvals.ts — file:line evidence সহ):
  - একটাই server-side trust check: শুধু owner-এর (Boss-এর) নিজের কথাই
    permission; বাকি সবকিছু data, কখনো permission নয়।
  - Checker-কে Boss-এর সঠিক কথা quote করতে হয়; server সেই quote verify
    করে — quote করা কথা সত্যিই Boss লিখেছেন/বলেছেন কি না।
  - Reads / drafts চলে free; writes / commits-এর জন্য Boss-এর কথা লাগে।
  - Confirmation একদম exact action + arguments-এর সাথে বাঁধা; একবার
    চলে; failed / interrupted action UNCERTAIN — কখনো re-run নয়;
    repeat-এর জন্য নতুন confirmation লাগে।

এই ফাইলে (Python, rule-based classifier প্রথমে — কোনো model judge নয়,
কোনো live call নয়, stdlib only):
  1. trust_check() — read/write split + quote verification + coverage +
     standing-rule deny (spend cap $0, dental/medical DQ)।
  2. ConfirmationStore — run-once confirmation, ApprovalGateway-এর সাথে
     wired (gateway-ই approval-এর একমাত্র সত্য; confirmation record
     approval_id দিয়ে link করা)।
  3. Dispatcher wiring — tool_calling.call_tool()-এর gated branch
     trust_check চালায়: deny হলে "blocked-trust" (কোনো approval
     রেকর্ড হয় না, কিছু execute হয় না); নইলে আগের মতো PENDING,
     result-এ trust decision attach থাকে।

Standing নিয়ম (config.json থেকে পড়া, Boss-এর সিদ্ধান্ত):
  - Spend cap $0 — cap-এর বেশি খরচ trust deny (কোনো check-এ এই পথ
    ব্যবহৃত হয় না; existing behavior বদলায় না)।
  - Dental / medical / patient-health — hard DQ, trust deny।
  - Email PAUSED (2026-11-14) — deny নয়: decision "ask", note-এ
    PAUSED লেখা থাকে; PENDING approval-ই restart-এর পথ, তাই
    check_live_tools.py-এর "gmail_send -> pending-approval" অপরিবর্তিত।
  - Gateway-ই চূড়ান্ত authority: trust "allow" হলেও gated handler
    execute হয় না — Boss-এর exact gate word ছাড়া কিছু এগোয় না।
    এই repo-তে কোনো auto-approve পথ নেই, কোডেও নেই।

ব্যবহার:
  from trust_gate import trust_check, ConfirmationStore
  d = trust_check("send", {"to": "a@b.com", "subject": "Hi", "body": ".."},
                  owner_words=["Day 4 batch পাঠাও"],
                  owner_source="Boss (chat 2026-11-21): Day 4 batch পাঠাও")
  # d["decision"] = "allow" | "ask" | "deny"
  store = ConfirmationStore()  # store/confirmations.json
  c = store.create("send", {"to": "a@b.com"}, "Day 4 batch পাঠাব?", "Main CEO Bot")
  store.approve(c["id"], gate_word="send")
  store.execute_once(c["id"], runner)  # runner(canonical_args) -> result

Status: REAL (Improvement Phase 1, 2026-11-21) — mock brain-এ চলে, কোনো
live brain / API key / network লাগে না। Brain এখনো mock।
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

# Commit = যা বাইরে কিছু বদলায় (পাঠানো / পাবলিশ / খরচ / মোছা / বুক / পে)।
COMMIT_ACTIONS = ("send", "publish", "spend", "delete", "upload",
                  "book", "pay", "order", "cancel")
# Read = শুধু পড়া / draft — free চলে।
READ_ACTIONS = ("read", "draft", "status", "search", "list")

# Gate word -> action (human_approval_gateway.GATE_WORD_FOR_ACTION-এর mirror;
# import cycle এড়াতে এখানে duplicate — দুটো একই থাকতে হবে, check_gate.py
# সেটা যাচাই করে)।
GATE_WORD_FOR_ACTION = {
    "send": ("send", "পাঠাও"),
    "publish": ("post it", "post all"),
    "spend": ("go",),
    "delete": ("go",),
    "upload": ("upload it",),
}

# Hard-DQ niches (Boss-এর স্থায়ী সিদ্ধান্ত — কখনো target নয়)।
EXCLUDED_NICHE_WORDS = ("dental", "dentist", "medical", "patient-health")

# Email restart-এর স্পষ্ট কথা (PAUSED তোলার একমাত্র override)।
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
    """Boss-এর স্থায়ী কথা (gate words + standing rules) — quote verify-এর
    default source। শুধু এখানে লেখা কথাই standing source হিসেবে গোনা হয়।"""
    words = (config.get("gates") or {}).get("words") or {}
    lines = ["Boss-এর gate words:"]
    for word, meaning in sorted(words.items()):
        lines.append(f"- {word!r} = {meaning}")
    lines.append("Standing rules: spend cap is $0. "
                 "Email sending is PAUSED since 2026-11-14. "
                 "Dental / medical / patient-health never a target. "
                 "No gated action moves without Boss's exact gate word.")
    return "\n".join(lines)


def _normalize(text):
    """Quote মেলানোর জন্য whitespace normalize (case-sensitive — Boss-এর
    সঠিক কথাই মিলতে হবে, ছোট-বড় হাতের ভুল চলবে না)।"""
    return re.sub(r"\s+", " ", str(text or "")).strip()


def verify_quote(quote, source_text):
    """একটা quote সত্যিই source-এ verbatim আছে কি না। খালি quote কখনো
    verify হয় না (Nod: quote না থাকলে ask করো, run করো না)।"""
    q = _normalize(quote)
    if not q:
        return False
    return q in _normalize(source_text)


def _args_text(args):
    """Args-এর সব string value একসাথে — niche scan + coverage-এর জন্য।"""
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
    """এই action-এর material target — quote-এ এগুলোর অন্তত একটা থাকতে
    হবে, নইলে quote এই action-কে cover করে না। Generic শব্দ (যেমন
    শুধু "email") target নয় — প্রাপক / event / পরিমাণের মতো সুনির্দিষ্ট
    মানই target।"""
    args = args or {}
    targets = []
    if action == "send":
        to = (args.get("to") or "").strip()
        if to:
            targets.append(to)
            if "@" in to:
                targets.append(to.split("@", 1)[1])  # domain-ও চলে
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
    """Verified quote-গুলো এই action-কে cover করে কি না: gate word +
    অন্তত একটা material target — দুটোই লাগবে (rule-based)।"""
    allowed_words = GATE_WORD_FOR_ACTION.get(action)
    if not allowed_words:
        # Gate word table-এ নেই এমন commit action (upload/book/pay/...) —
        # rule-based classifier জানে না, তাই cover ধরা যায় না: ask করো।
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
# trust_check() — একটাই server-side check (Nod trust.ts-এর আদলে)
# ---------------------------------------------------------------------------

def trust_check(action, args=None, owner_words=None, owner_source=None,
                config=None, tool_name=None, config_path=None):
    """একটা action চালানোর আগে trust সিদ্ধান্ত।

    Decision:
      "allow" — Boss-এর quote verify হয়েছে + action cover করে।
      "ask"   — Boss-এর কথা লাগবে (quote নেই / cover করে না / PAUSED note)।
      "deny"  — quote verify হয়নি, বা standing rule (spend cap / DQ niche)
                স্পষ্টভাবে বারণ করেছে। Deny মানে: approval-ও রেকর্ড হয় না।

    কোনো সিদ্ধান্তই gated handler execute করে না — execute শুধু
    ApprovalGateway-এ Boss-এর exact gate word-এর পরে, ভবিষ্যৎ live path-এ।
    """
    args = args or {}
    cfg = config if isinstance(config, dict) else _load_config(config_path)
    action = (action or "").strip().lower()

    # 1. Read / draft — free চলে (Nod: reads/drafts run free)।
    if action in READ_ACTIONS:
        return {
            "decision": "allow",
            "action": action,
            "basis": ["Reads and drafts run free — no owner words needed."],
            "reason": f"{action!r} is a read/draft action.",
            "quotes_verified": [],
        }

    # 2. অচেনা action — classifier জানে না: ask করো, deny নয় (fail-safe:
    #    না জানলে Boss-কে জিজ্ঞেস করো, নিজে সিদ্ধান্ত নিয়ো না)।
    if action not in COMMIT_ACTIONS:
        return {
            "decision": "ask",
            "action": action,
            "basis": [f"Unknown action {action!r} — no rule covers it."],
            "reason": "Unknown action — ask Boss.",
            "quotes_verified": [],
        }

    # 3. Standing-rule deny — এগুলো সবকিছুর ওপরে জেতে (Nod: a rule to
    #    ask first wins over everything)।
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
        # amount নেই বা 0 — quote ছাড়া সিদ্ধান্ত নয়, ask-এ পড়বে।

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
        # যেকোনো send tool (gmail_send, n8n_trigger, ...) — PAUSED
        # note শুধু gmail_send-এর নয়; email বন্ধ থাকতে সব send-এই
        # একই সত্য কথা থাকে।
        quotes_so_far = " ".join(owner_words or [])
        restarted = any(m in _normalize(quotes_so_far).lower()
                        for m in EMAIL_RESTART_MARKERS)
        if not restarted:
            notes.append("Email sending is PAUSED since 2026-11-14 — "
                         "the PENDING approval is the restart path; "
                         "execution stays blocked until Boss restarts.")

    # 4. Boss-এর কথা নেই — ask করো (Nod: quote না থাকলে ask, run নয়)।
    owner_words = [w for w in (owner_words or []) if _normalize(w)]
    if not owner_words:
        return {
            "decision": "ask",
            "action": action,
            "basis": ["No owner words provided — Boss's words are needed."] + notes,
            "reason": "No owner words — ask Boss.",
            "quotes_verified": [],
        }

    # 5. Quote verification — প্রতিটা quote source-এ verbatim থাকতে হবে।
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

    # 6. Coverage — quote এই exact action-কে cover করে কি না।
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
# ConfirmationStore — run-once confirmation (Nod approvals.ts-এর আদলে)
# ---------------------------------------------------------------------------

CONFIRMATION_STATUSES = ("asked", "approved", "declined", "executed",
                         "expired", "uncertain")


def _canonical_args(args):
    """Exact action + arguments — canonical JSON (key order স্থির, তাই
    একই args সবসময় একই string)।"""
    return json.dumps(args or {}, sort_keys=True, ensure_ascii=False)


class ConfirmationStore:
    """Run-once confirmation — ApprovalGateway-এর সাথে wired।

    একটা confirmation = একটা exact action + exact args + একটা প্রশ্ন।
    Gateway-ই approval-এর সত্য: create() gateway-এ approval request
    লেখে (approval_id link করা থাকে); approve() gateway record-ও
    approve করে (gate word মিলতেই হবে)। execute_once() runner-কে
    canonical args দিয়ে ঠিক একবার চালায়; fail করলে status UNCERTAIN
    — আর কখনো re-run নয়; repeat-এর জন্য নতুন confirmation লাগে।
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
        """নতুন confirmation + gateway-এ linked approval request।

        শুধু gateway-এর এই ৪টা gated action (send / publish / spend /
        delete) — upload-এর gate word gateway-এ আছে, কিন্তু
        confirmation store-এ upload-এর path এখনো নেই (gateway-এ
        request করা যায়, confirmation এখানে নয়)।
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
        """TTL পেরিয়ে যাওয়া 'asked' confirmation-গুলোকে 'expired' করো।

        TTL: human_approval_gateway.APPROVAL_TTL_MINUTES (২০ মিনিট —
        recorded chat-card expiry, MEMORY.md)। Linked gateway
        record-ও একই sweep-এ expire হয়, তাই দুই store একমত থাকে।
        ফেরত: expired হওয়া confirmation id-গুলো।
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
                continue  # timestamp পড়া না গেলে expire করা হয় না
            if now - asked > timedelta(minutes=APPROVAL_TTL_MINUTES):
                record["status"] = "expired"
                record["decided_at"] = now.isoformat()
                expired_ids.append(record["id"])
        if expired_ids:
            self._save()
            try:
                ApprovalGateway(
                    approvals_path=self.approvals_path).sweep_expired()
            except Exception:  # noqa: BLE001 — gateway sweep কখনো confirmation-কে ভাঙবে না
                pass
        return expired_ids

    def approve(self, confirmation_id, gate_word, decided_by="Boss"):
        """Boss অনুমোদন দিলে — gate word মিলতেই হবে। Gateway record-ও
        approve হয় (একই gate word); gateway fail করলে confirmation
        'asked'-ই থাকে (আধা-অবস্থা নয়)। মেয়াদোত্তীর্ণ (expired)
        confirmation approve করা যায় না — আগে sweep_expired() চলে।"""
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
                pass  # gateway record already decided — confirmation-ই সত্য
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
        """Exact saved action + args ঠিক একবার চালানো।

        runner(canonical_args_dict) -> result (যেকোনো JSON-able মান)।
        Success -> "executed"। Exception / interruption -> "uncertain"
        (আর কখনো re-run নয় — "may have run, check the app")। "executed"
        বা "uncertain"-এ আবার execute করলে ValueError — repeat-এর জন্য
        নতুন confirmation লাগে।
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
    # হাতে চেক: TEMP file-এ, আসল store ছোঁয়া হয় না।
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_conf = os.path.join(tmp_dir, "confirmations-test.json")
    tmp_appr = os.path.join(tmp_dir, "approvals-test.json")

    # 1. Read/draft free।
    assert trust_check("read", {})["decision"] == "allow"
    assert trust_check("draft", {})["decision"] == "allow"
    # 2. Quote নেই -> ask।
    assert trust_check("send", {"to": "a@b.com"})["decision"] == "ask"
    # 3. Spend cap-এর বেশি -> deny।
    assert trust_check("spend", {"amount_usd": 5, "purpose": "ads"})["decision"] == "deny"
    # 4. Dental -> deny।
    assert trust_check("send", {"to": "x@dental.com"})["decision"] == "deny"
    # 5. ভুল quote -> deny।
    d = trust_check("send", {"to": "a@b.com"},
                    owner_words=["Day 4 batch পাঠাও"],
                    owner_source="Boss: আজ ছুটি")
    assert d["decision"] == "deny", d
    # 6. সঠিক quote + coverage -> allow।
    d = trust_check("send", {"to": "a@b.com", "subject": "Hi", "body": "x"},
                    owner_words=["Day 4 batch পাঠাও — a@b.com-কে email"],
                    owner_source="Boss (chat): Day 4 batch পাঠাও — a@b.com-কে email")
    assert d["decision"] == "allow", d

    # 7. Confirmation lifecycle: create -> approve -> execute once।
    store = ConfirmationStore(confirmations_path=tmp_conf,
                              approvals_path=tmp_appr)
    c = store.create("send", {"to": "a@b.com", "subject": "Hi"},
                     "Day 4 batch পাঠাব?", "Main CEO Bot")
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
    # 8. Fail -> uncertain, never re-run।
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
