"""Lead store — read access to the repo lead store (Phase 3, Unified OS).

The store lives at ``store/leads.json`` (schema ``leads-v1``). It is seeded
from the REAL workspace pool — never invented:

  - ``~/workspace/talvenor/leads-organized/scoring/``
    ``outreach-pool-tier1-tier2.csv`` — 507 rows (Tier 1: 2, Tier 2: 505).
  - ``~/workspace/talvenor/leads-organized/*/emailed.csv`` — 162 filed
    rows (PA 39, FL 54, GA 16, TX 15, CA 14, IL 9, MI 5, NC 5, NY 4,
    OH 1), PLUS 1 verified filing gap: Isackson Plumbing (San Francisco
    CA) was sent 2026-11-12 (Gmail Sent verified 2026-11-23, message
    1a1cfb0ff25cdb8c) but has no emailed.csv row — true first-mail
    total is 163 (CA 15). 132 of the filed rows are in the pool; 30 are
    sent-history-only leads (Tier 3/4, kept so we never double-mail —
    see DELETION-LOG-2026-11-10.md).
  - One held business: Premier Plumbing, San Antonio TX
    (``prospects/tx-prospects.csv``), HELD_DO_NOT_CONTACT — it is
    already in the pool, so the flag merges into that lead (no extra row).

Dedup: by normalized domain first, falling back to normalized phone,
then email, then business-name+city. Rows sharing a key are branches of
one business (same domain/phone, different city — e.g. Apex Plumbing
Tampa + St. Petersburg, UGI Harrisburg + Allentown); they merge into ONE
lead record and the branch rows are kept in ``locations``. 507 pool rows
merge to 494 unique pool businesses (13 branch rows merged); + 30
sent-history-only = 524 unique leads in the store.
Source-row total 537 (507 + 30) is kept in ``meta`` for audit.

Scoring rules (locked, Boss 2026-11-10/12): STRONG >= 80 -> Tier 1,
MEDIUM caps Tier 2, WEAK -> Tier 4; dental/medical = disqualified
(never a target — no dental/medical business is in the pool);
legal gated until the 4th client.

Flags (never silently dropped):
  - BOUNCED_DEAD_ADDRESS — the 6 confirmed dead addresses
    (Athens, Alberto, ServiceProz, Napps, All Masters, Thompson &
    Thompson). Never re-mail.
  - NEVER_REMAIL_DOUBLE_SENT — Metz Plumbing, AAA Sewer & Drain
    (emailed twice by accident). Never re-mail.
  - HELD_DO_NOT_CONTACT — Premier Plumbing, San Antonio TX.
  - HELD_LOW_CONFIDENCE — Always Plumbing LLC (PA).
  - OTHER_CHANNEL_CONTACTED — Remarkable Plumbing and Heating (PA).
  - SHARED_PHONE / SHARED_EMAIL — same phone/email on two different
    businesses; verify before contacting.

Rules:
  - READ-ONLY by default. The only writer is scripts/build_lead_store.py,
    which writes through store_io (atomic + flock). This module's
    ``save()`` is that same store_io path, used by the builder only.
  - Counts are COMPUTED from the store, never hardcoded. A missing file
    or missing key returns "UNKNOWN" (honest_status pattern) — callers
    must surface that marker, never substitute a hardcoded number.
  - No network, no send, no publish, no spend.

Stdlib only.
"""

import json
import os
import re
from urllib.parse import urlparse

UNKNOWN = "UNKNOWN"

# Boss's standing rule: no follow-up for a state until 100 first mails
# are complete in that state (2026-11-10). The queue module enforces it.
FOLLOWUP_THRESHOLD_PER_STATE = 100

LEADS_SCHEMA = "leads-v1"


def _store_path(leads_path=None):
    """store/leads.json next to this module's repo, unless given (tests)."""
    if leads_path:
        return leads_path
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(here)
    return os.path.join(repo, "store", "leads.json")


def norm_domain(website):
    """Normalized domain: lowercased, no scheme/www/trailing slash."""
    if not website:
        return ""
    value = website.strip().lower()
    if value.startswith("http"):
        try:
            value = urlparse(value).netloc
        except Exception:
            pass
    if value.startswith("www."):
        value = value[4:]
    return value.rstrip("/")


def norm_phone(phone):
    """Normalized phone: digits only, US country code stripped."""
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits


def norm_email(email):
    """Normalized email: lowercased, stripped."""
    return (email or "").strip().lower()


def dedup_key(business_name="", website="", phone="", email="", city=""):
    """Dedup key for one source row: domain > phone > email > name+city.

    Returns (kind, key). Two rows with the same key are the same business
    (branches merge; see the module docstring)."""
    domain = norm_domain(website)
    if domain:
        return ("domain", domain)
    digits = norm_phone(phone)
    if digits:
        return ("phone", digits)
    mail = norm_email(email)
    if mail:
        return ("email", mail)
    return ("name_city",
            (business_name or "").strip().lower() + "|" +
            (city or "").strip().lower())


def load_store(leads_path=None):
    """The lead store dict, or None when the file is missing/corrupt.

    Missing/corrupt is reported as None (never an empty store pretended
    to be real data) — callers turn it into UNKNOWN.
    """
    try:
        with open(_store_path(leads_path), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or data.get("schema") != LEADS_SCHEMA:
        return None
    return data


def leads(leads_path=None):
    """All lead records (list), or [] when the store is unreadable."""
    data = load_store(leads_path)
    if data is None:
        return []
    records = data.get("leads")
    return records if isinstance(records, list) else []


def find_by_domain(domain, leads_path=None):
    """Lead whose normalized domain matches, or None."""
    want = norm_domain(domain)
    if not want:
        return None
    for lead in leads(leads_path):
        if lead.get("domain") == want:
            return lead
    return None


def find_by_phone(phone, leads_path=None):
    """Lead whose normalized phone matches, or None."""
    want = norm_phone(phone)
    if not want:
        return None
    for lead in leads(leads_path):
        if lead.get("phone_norm") == want:
            return lead
        for loc in lead.get("locations") or []:
            if norm_phone(loc.get("phone")) == want:
                return lead
    return None


def find_by_email(email, leads_path=None):
    """Lead whose normalized email matches, or None."""
    want = norm_email(email)
    if not want:
        return None
    for lead in leads(leads_path):
        if norm_email(lead.get("email")) == want:
            return lead
        for loc in lead.get("locations") or []:
            if norm_email(loc.get("email")) == want:
                return lead
    return None


def first_mails_by_state(leads_path=None):
    """First mails per state, computed from sent records in the store.

    Returns {state: count}. A state with no sent lead is absent (not 0 —
    callers use .get(state, 0) and must not claim a count the store
    cannot support). Returns {} when the store is unreadable.
    """
    counts = {}
    for lead in leads(leads_path):
        sent = lead.get("sent") or {}
        if sent.get("emailed") is True:
            state = (lead.get("state") or "").strip().upper()
            if state:
                counts[state] = counts.get(state, 0) + 1
    return counts


def first_mails_total(leads_path=None):
    """Total first mails (int), or "UNKNOWN" when the store is unreadable."""
    data = load_store(leads_path)
    if data is None:
        return UNKNOWN
    return sum(first_mails_by_state(leads_path).values())


def first_mails_for_state(state, leads_path=None):
    """First mails for one state (int), or "UNKNOWN" when unreadable."""
    data = load_store(leads_path)
    if data is None:
        return UNKNOWN
    return first_mails_by_state(leads_path).get(
        (state or "").strip().upper(), 0)


def flagged_leads(flag, leads_path=None):
    """Leads carrying a given flag (e.g. "BOUNCED_DEAD_ADDRESS")."""
    return [lead for lead in leads(leads_path)
            if flag in (lead.get("flags") or [])]


def store_meta(leads_path=None):
    """The store's meta dict (build sources + reconciliation), or {}."""
    data = load_store(leads_path)
    if data is None:
        return {}
    meta = data.get("meta")
    return meta if isinstance(meta, dict) else {}


def save_store(payload, leads_path=None):
    """Write the lead store through store_io (atomic + flock).

    Builder-only. Payload must carry schema "leads-v1".
    """
    if not isinstance(payload, dict) or payload.get("schema") != LEADS_SCHEMA:
        raise ValueError("lead store payload must carry schema 'leads-v1'")
    here = os.path.dirname(os.path.abspath(__file__))
    import sys
    if here not in sys.path:
        sys.path.insert(0, here)
    import store_io
    return store_io.update_json(_store_path(leads_path),
                                lambda _old: payload,
                                default=None)


if __name__ == "__main__":
    # Self-test — TEMP store only, the real store is only read.
    import tempfile

    data = load_store()
    assert data is not None, "real store/leads.json missing — run the builder"
    assert data["schema"] == LEADS_SCHEMA
    assert len(leads()) == data["meta"]["total_unique_leads"]
    assert first_mails_total() == 163
    by_state = first_mails_by_state()
    assert by_state.get("PA") == 39, by_state
    assert by_state.get("FL") == 54, by_state
    assert by_state.get("CA") == 15, by_state
    assert first_mails_for_state("TX") == 15
    assert first_mails_for_state("XX") == 0
    assert find_by_domain("https://www.ugihvac.com/") is not None
    assert find_by_domain("https://www.ugihvac.com/")["business_name"].startswith("UGI")
    assert len(find_by_domain("https://www.ugihvac.com/")["locations"]) == 2
    assert find_by_phone("+1 412-872-4105")["business_name"].startswith("Metz")
    assert find_by_email("info@athensplumbing.com") is not None
    assert len(flagged_leads("BOUNCED_DEAD_ADDRESS")) == 6
    assert len(flagged_leads("NEVER_REMAIL_DOUBLE_SENT")) == 2
    assert len(flagged_leads("HELD_DO_NOT_CONTACT")) == 1
    assert find_by_domain("premierplumbing.us") is not None
    assert find_by_domain("no-such-domain.example") is None
    assert first_mails_total("/tmp/no-such-leads.json") == UNKNOWN
    assert first_mails_for_state("PA", "/tmp/no-such-leads.json") == UNKNOWN
    assert first_mails_by_state("/tmp/no-such-leads.json") == {}
    # A corrupt store is None, never an empty store.
    tmp = os.path.join(tempfile.mkdtemp(), "leads.json")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("{not json")
    assert load_store(tmp) is None
    print("lead_store: OK (load, dedup lookups, per-state counts 163/PA 39/CA 15, "
          "flags 6 bounced + 2 double-sent + 1 held; missing/corrupt -> UNKNOWN)")
