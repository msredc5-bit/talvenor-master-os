#!/usr/bin/env python3
"""Build store/leads.json from the REAL workspace lead files (Phase 3).

Sources (read-only — this script never writes to them):
  - ~/workspace/talvenor/leads-organized/scoring/outreach-pool-tier1-tier2.csv
    (507 rows; Tier 1: 2, Tier 2: 505)
  - ~/workspace/talvenor/leads-organized/*/emailed.csv (162 filed rows)
  - One verified filing gap: Isackson Plumbing (San Francisco CA) was
    sent 2026-11-12 (Gmail Sent verified, message 1a1cfb0ff25cdb8c) but
    has no emailed.csv row — true first-mail total is 163 (CA 15), not
    the 162 in the older locked count. See VERIFIED_SENT_CORRECTIONS.
  - ~/workspace/talvenor/prospects/tx-prospects.csv (1 extra held row:
    Premier Plumbing, San Antonio TX — HELD_DO_NOT_CONTACT)

Dedup: by normalized domain first, falling back to phone, email,
name+city (see 00-CEO-Core/lead_store.py dedup_key). Branch rows of one
business merge into ONE lead; every branch row is kept in ``locations``.

Flags applied (never silently dropped):
  - BOUNCED_DEAD_ADDRESS: the 6 confirmed dead addresses (brief list).
  - NEVER_REMAIL_DOUBLE_SENT: notes contain "DUPLICATE SENT".
  - HELD_DO_NOT_CONTACT: Premier Plumbing, San Antonio TX.
  - HELD_LOW_CONFIDENCE: notes contain "HELD".
  - OTHER_CHANNEL_CONTACTED: pool sent_status == "other-channel".
  - SHARED_PHONE / SHARED_EMAIL: same phone/email on leads with
    different domains (computed after the merge).

The script FAILS LOUDLY (non-zero exit, no write) when a locked number
does not reconcile: pool rows 507, filed emailed rows 162 (+ 1 verified
filing gap = 163 first mails), per-state first mails (PA 39, FL 54,
GA 16, TX 15, CA 15, IL 9, MI 5, NC 5, NY 4, OH 1), 6 bounced,
2 double-sent, 1 held. Run:

    python3 scripts/build_lead_store.py [--store-dir DIR]

Default store dir is the repo store/. Writes through store_io
(atomic + flock). No network, no send, no publish, no spend.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
WORKSPACE = os.path.dirname(BASE)
LEADS_DIR = os.path.join(WORKSPACE, "talvenor", "leads-organized")
POOL_CSV = os.path.join(LEADS_DIR, "scoring",
                        "outreach-pool-tier1-tier2.csv")
PREMIER_CSV = os.path.join(WORKSPACE, "talvenor", "prospects",
                           "tx-prospects.csv")

sys.path.insert(0, CEO_CORE_DIR)
import lead_store  # noqa: E402
import store_io  # noqa: E402

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"

# Confirmed dead addresses (Boss briefing 2026-11-14) — never re-mail.
BOUNCED_EMAILS = {
    "info@athensplumbing.com",
    "info@albertoplumbing.com",
    "office@plumbproz.com",
    "napps@nappsac.com",
    "privacy@allmastersplumbing.com",
    "service@tnt.jdpps.com",
}

# Double-sent by accident (CLI timeout retried as if it failed) — never re-mail.
DOUBLE_SENT_NAMES = {"metz plumbing", "aaa sewer"}

EXPECTED_EMAILED_BY_STATE = {"PA": 39, "FL": 54, "GA": 16, "TX": 15,
                             "CA": 15, "IL": 9, "MI": 5, "NC": 5,
                             "NY": 4, "OH": 1}
# Verified sent corrections: pool rows that say SENT but have no
# emailed.csv row. Each entry was verified against Gmail Sent before
# being written here — never add an entry without that check.
# Isackson Plumbing (San Francisco CA): pool says SENT 2026-11-12, CA
# emailed.csv has no row (filing gap, same class as Ory's Plumbing
# 2026-10-13). Gmail Sent verified 2026-11-23: in:sent
# to:isacksonplumbing@gmail.com, message 1a1cfb0ff25cdb8c, Thu 12 Nov
# 2026 18:17 Dhaka, from hello@talvenorai.agency. True first-mail
# total is therefore 163 (CA 15), not the 162 in the older locked count.
VERIFIED_SENT_CORRECTIONS = {
    "isacksonplumbing@gmail.com": {
        "sent_date": "2026-11-12",
        "message_id": "1a1cfb0ff25cdb8c",
        "evidence": "Gmail Sent verified 2026-11-23: in:sent "
                    "to:isacksonplumbing@gmail.com, 2026-11-12 18:17 "
                    "Dhaka, from hello@talvenorai.agency",
    },
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_score_qual(qualification):
    """"Tier 2 | 64/100 | STRONG 7 signals" -> (64, "Tier 2")."""
    score = None
    tier = None
    if qualification:
        m = re.search(r"(\d{1,3})/100", qualification)
        if m:
            score = int(m.group(1))
        m = re.search(r"(Tier\s*[1-4])", qualification)
        if m:
            tier = m.group(1).replace(" ", " ")
            tier = "Tier " + tier.split()[-1]
    return score, tier


def as_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def read_pool():
    with open(POOL_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_emailed():
    """All */emailed.csv rows, in sorted file order (00-PA .. 09-NY)."""
    rows = []
    sources = []
    import glob
    paths = sorted(glob.glob(os.path.join(LEADS_DIR, "*/emailed.csv")))
    for path in paths:
        with open(path, newline="", encoding="utf-8") as f:
            file_rows = list(csv.DictReader(f))
        sources.append({"file": os.path.relpath(path, WORKSPACE),
                        "rows": len(file_rows),
                        "sha256": sha256_file(path)})
        for row in file_rows:
            row["_source_file"] = os.path.relpath(path, WORKSPACE)
            rows.append(row)
    return rows, sources


def location_from_pool(row):
    return {
        "city": row.get("city", ""),
        "state": row.get("state", ""),
        "website": row.get("website", ""),
        "email": row.get("email", ""),
        "phone": row.get("phone", ""),
        "score": as_int(row.get("score")),
        "tier": row.get("tier", "") or None,
        "sent_status": row.get("sent_status", ""),
        "source_row": "pool",
    }


def location_from_emailed(row):
    score, tier = parse_score_qual(row.get("qualification", ""))
    return {
        "city": row.get("city", ""),
        "state": row.get("state", ""),
        "website": row.get("website", ""),
        "email": row.get("email", ""),
        "phone": row.get("phone", ""),
        "score": score,
        "tier": tier,
        "sent_status": row.get("status", ""),
        "source_row": "emailed",
    }


def flags_from_notes(notes):
    flags = set()
    text = notes or ""
    if "DUPLICATE SENT" in text.upper():
        flags.add("NEVER_REMAIL_DOUBLE_SENT")
    if "BOUNCED" in text.upper():
        flags.add("BOUNCED_DEAD_ADDRESS")
    # HELD counts only when the note says THIS lead is held — "(held)"
    # about another listing (e.g. Stars and Pipes ATL vs the Lilburn
    # listing) does not flag this lead.
    upper = text.upper()
    if re.search(r"(^|\|)\s*HELD\b|ROW IS HELD|IS HELD", upper):
        flags.add("HELD_LOW_CONFIDENCE")
    return flags


def build():
    pool_rows = read_pool()
    emailed_rows, emailed_sources = read_emailed()

    # ---- 1. Pool groups, deduped by domain/phone/email/name+city ----
    groups = {}   # (kind, key) -> group dict
    order = []
    for row in pool_rows:
        key = lead_store.dedup_key(row.get("business_name", ""),
                                   row.get("website", ""),
                                   row.get("phone", ""),
                                   row.get("email", ""),
                                   row.get("city", ""))
        if key not in groups:
            groups[key] = {"key": key, "pool_rows": [], "emailed_rows": []}
            order.append(key)
        groups[key]["pool_rows"].append(row)

    # ---- 2. Attach emailed rows (domain > phone > email) ----
    def find_group(row):
        domain = lead_store.norm_domain(row.get("website", ""))
        if domain:
            hit = groups.get(("domain", domain))
            if hit is not None:
                return hit
        phone = lead_store.norm_phone(row.get("phone", ""))
        if phone:
            for g in groups.values():
                if any(lead_store.norm_phone(r.get("phone", "")) == phone
                       for r in g["pool_rows"]):
                    return g
        email = lead_store.norm_email(row.get("email", ""))
        if email:
            for g in groups.values():
                if any(lead_store.norm_email(r.get("email", "")) == email
                       for r in g["pool_rows"]):
                    return g
        return None

    sent_only = []
    for row in emailed_rows:
        group = find_group(row)
        if group is None:
            sent_only.append(row)
        else:
            group["emailed_rows"].append(row)

    # ---- 3. Extra held row: Premier Plumbing, San Antonio TX ----
    # The pool already contains this business (Premier Plumbing, San
    # Antonio, premierplumbing.us) — so the held flag merges INTO that
    # lead instead of creating a duplicate row. Only if the pool ever
    # loses it would a new extra row be appended (fallback below).
    premier = None
    with open(PREMIER_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("name", "").strip() == "Premier Plumbing"
                    and "San Antonio" in (row.get("city", "") or "")):
                premier = row
                break
    if premier is None:
        raise SystemExit("FAIL: Premier Plumbing (San Antonio) not found in "
                         + PREMIER_CSV)
    premier_key = lead_store.dedup_key(
        "Premier Plumbing", premier.get("website", ""),
        premier.get("phone", ""), "", "San Antonio")
    premier_group = groups.get(premier_key)
    premier_merged = premier_group is not None

    # ---- 4. Build lead records ----
    leads = []
    branch_rows_merged = 0
    for key in order:
        group = groups[key]
        prows = group["pool_rows"]
        erows = group["emailed_rows"]
        branch_rows_merged += max(0, len(prows) - 1)
        # Primary row: highest score; tie -> emailed first; then file order.
        def primary_rank(r):
            sent = 1 if r.get("sent_status", "") in (
                "emailed", "SENT 2026-11-11", "SENT 2026-11-12") else 0
            return (-(as_int(r.get("score")) or 0), -sent)
        primary = sorted(prows, key=primary_rank)[0]
        locations = [location_from_pool(r) for r in prows]
        for r in erows:
            loc = location_from_emailed(r)
            # Emailed location not already in locations (same city+phone)?
            if not any(l["city"] == loc["city"]
                       and lead_store.norm_phone(l["phone"])
                       == lead_store.norm_phone(loc["phone"])
                       for l in locations):
                locations.append(loc)
        notes = []
        for r in prows:
            if r.get("notes", "").strip():
                notes.append(r["notes"].strip())
        for r in erows:
            if r.get("notes", "").strip():
                notes.append(r["notes"].strip())
        flags = set()
        for r in prows:
            flags |= flags_from_notes(r.get("notes", ""))
            if (r.get("sent_status", "") == "other-channel"):
                flags.add("OTHER_CHANNEL_CONTACTED")
        for r in erows:
            flags |= flags_from_notes(r.get("notes", ""))
        for loc in locations:
            if lead_store.norm_email(loc.get("email")) in BOUNCED_EMAILS:
                flags.add("BOUNCED_DEAD_ADDRESS")
        name_low = (primary.get("business_name", "") or "").lower()
        if any(n in name_low for n in DOUBLE_SENT_NAMES):
            flags.add("NEVER_REMAIL_DOUBLE_SENT")
        # Premier Plumbing San Antonio is already in the pool — the held
        # flag merges into this lead instead of a duplicate row.
        if premier_merged and group is premier_group:
            flags.add("HELD_DO_NOT_CONTACT")
            notes.append(
                "HELD_DO_NOT_CONTACT — already_contacted=yes; verify "
                "(mail-batch-final200-2-candidates.md). Never contact "
                "without Boss's word. Email office@premierplumbing.us "
                "is UNVERIFIED (emails-tx.csv).")
        sent = None
        if erows:
            first = erows[0]
            sent = {
                "emailed": True,
                "sent_date": first.get("sent_date", "") or None,
                "message_id": first.get("message_id", "") or None,
                "followup_status": first.get("followup_status", "") or None,
                "source_file": first.get("_source_file", "") or None,
            }
        elif primary.get("sent_status", "") in (
                "emailed", "SENT 2026-11-11", "SENT 2026-11-12"):
            # Pool says sent, but no emailed.csv row matched. If the send
            # was verified against Gmail Sent, use that evidence; else
            # keep the pool's word and mark the gap honestly (no
            # date/message id claimed).
            correction = None
            for loc in locations:
                correction = VERIFIED_SENT_CORRECTIONS.get(
                    lead_store.norm_email(loc.get("email")))
                if correction:
                    break
            if correction:
                sent = {"emailed": True,
                        "sent_date": correction["sent_date"],
                        "message_id": correction["message_id"],
                        "followup_status": None,
                        "source_file": None,
                        "note": "No emailed.csv row (filing gap); "
                                + correction["evidence"]}
            else:
                sent = {"emailed": True, "sent_date": None,
                        "message_id": None,
                        "followup_status": None, "source_file": None,
                        "note": "pool sent_status says sent; no emailed.csv "
                                "row matched — date/message id UNKNOWN"}
        else:
            sent = {"emailed": False, "sent_date": None,
                    "message_id": None, "followup_status": None,
                    "source_file": None}
        leads.append({
            "business_name": primary.get("business_name", ""),
            "city": primary.get("city", ""),
            "state": primary.get("state", ""),
            "website": primary.get("website", ""),
            "email": primary.get("email", ""),
            "phone": primary.get("phone", ""),
            "domain": lead_store.norm_domain(primary.get("website", "")),
            "phone_norm": lead_store.norm_phone(primary.get("phone", "")),
            "score": as_int(primary.get("score")),
            "tier": primary.get("tier", "") or None,
            "confidence": primary.get("confidence", "") or None,
            "best_channel": primary.get("best_channel", "") or None,
            "score_breakdown": primary.get("score_breakdown", "") or None,
            "reason_line": primary.get("reason_line", "") or None,
            "dq_reason": primary.get("dq_reason", "") or None,
            "source": "pool",
            "locations": locations,
            "sent": sent,
            "flags": sorted(flags),
            "notes": " | ".join(dict.fromkeys(notes)),
        })

    # Sent-history-only leads (emailed, not in the pool).
    for row in sent_only:
        score, tier = parse_score_qual(row.get("qualification", ""))
        flags = flags_from_notes(row.get("notes", ""))
        if lead_store.norm_email(row.get("email", "")) in BOUNCED_EMAILS:
            flags.add("BOUNCED_DEAD_ADDRESS")
        leads.append({
            "business_name": row.get("business_name", ""),
            "city": row.get("city", ""),
            "state": row.get("state", ""),
            "website": row.get("website", ""),
            "email": row.get("email", ""),
            "phone": row.get("phone", ""),
            "domain": lead_store.norm_domain(row.get("website", "")),
            "phone_norm": lead_store.norm_phone(row.get("phone", "")),
            "score": score,
            "tier": tier,
            "confidence": None,
            "best_channel": None,
            "score_breakdown": None,
            "reason_line": None,
            "dq_reason": None,
            "source": "sent_history_only",
            "locations": [location_from_emailed(row)],
            "sent": {"emailed": True,
                     "sent_date": row.get("sent_date", "") or None,
                     "message_id": row.get("message_id", "") or None,
                     "followup_status": row.get("followup_status", "")
                     or None,
                     "source_file": row.get("_source_file", "") or None},
            "flags": sorted(flags),
            "notes": row.get("notes", "") or "",
        })

    # Extra held row — only appended when the pool does NOT already
    # contain Premier Plumbing San Antonio (it does, as of this build).
    extra_held_rows = 0
    if not premier_merged:
        leads.append({
            "business_name": "Premier Plumbing",
            "city": "San Antonio",
            "state": "TX",
            "website": premier.get("website", ""),
            "email": "",
            "phone": premier.get("phone", ""),
            "domain": lead_store.norm_domain(premier.get("website", "")),
            "phone_norm": lead_store.norm_phone(premier.get("phone", "")),
            "score": None,
            "tier": None,
            "confidence": None,
            "best_channel": None,
            "score_breakdown": None,
            "reason_line": premier.get("why_qualified", "") or None,
            "dq_reason": None,
            "source": "extra_held",
            "locations": [{
                "city": "San Antonio", "state": "TX",
                "website": premier.get("website", ""),
                "email": "", "phone": premier.get("phone", ""),
                "score": None, "tier": None, "sent_status": "HELD",
                "source_row": "prospects",
            }],
            "sent": {"emailed": False, "sent_date": None, "message_id": None,
                     "followup_status": None, "source_file": None},
            "flags": ["HELD_DO_NOT_CONTACT"],
            "notes": "HELD_DO_NOT_CONTACT — already_contacted=yes; verify "
                     "(mail-batch-final200-2-candidates.md). Never contact "
                     "without Boss's word. Email office@premierplumbing.us "
                     "is UNVERIFIED (emails-tx.csv) — not used as the lead email.",
        })
        extra_held_rows = 1

    # ---- 5. Cross-lead shared phone/email flags (different domains) ----
    by_phone = {}
    by_email = {}
    for lead in leads:
        if lead["phone_norm"]:
            by_phone.setdefault(lead["phone_norm"], []).append(lead)
        if lead_store.norm_email(lead.get("email")):
            by_email.setdefault(lead_store.norm_email(lead["email"]),
                                []).append(lead)
    for phone, group in by_phone.items():
        domains = {l["domain"] for l in group if l["domain"]}
        if len(group) > 1 and len(domains) > 1:
            for lead in group:
                lead["flags"] = sorted(set(lead["flags"]) |
                                       {"SHARED_PHONE"})
                lead["notes"] += (" | SHARED_PHONE: phone " + phone +
                                  " is also on " +
                                  ", ".join(sorted(
                                      x["business_name"] for x in group
                                      if x is not lead)) +
                                  " — verify before contacting.")
    for email, group in by_email.items():
        domains = {l["domain"] for l in group if l["domain"]}
        if len(group) > 1 and len(domains) > 1:
            for lead in group:
                lead["flags"] = sorted(set(lead["flags"]) |
                                       {"SHARED_EMAIL"})
                # The shared address is a form relay (Wix sentry) or an
                # agency inbox (WSI Priority Media) — not the business's
                # own email. Say so; do not pretend it reaches the shop.
                lead["notes"] += (" | SHARED_EMAIL: " + email +
                                  " is also on " +
                                  ", ".join(sorted(
                                      x["business_name"] for x in group
                                      if x is not lead)) +
                                  " — this address looks like a form "
                                  "relay or agency inbox, not the "
                                  "business's own email; verify before "
                                  "contacting.")

    # ---- 6. IDs + meta + reconciliation checks (fail loudly) ----
    for i, lead in enumerate(leads, 1):
        lead["id"] = "L-%04d" % i
    # IDs first, then order the keys the way the store keeps them.
    for lead in leads:
        lead["id"] = lead.pop("id")
        ordered = {"id": lead["id"]}
        for key in ("business_name", "city", "state", "website", "email",
                    "phone", "domain", "phone_norm", "score", "tier",
                    "confidence", "best_channel", "score_breakdown",
                    "reason_line", "dq_reason", "source", "locations",
                    "sent", "flags", "notes"):
            ordered[key] = lead[key]
        lead.clear()
        lead.update(ordered)

    first_by_state = {}
    for lead in leads:
        if lead["sent"]["emailed"] is True:
            first_by_state[lead["state"]] = \
                first_by_state.get(lead["state"], 0) + 1
    total_first = sum(first_by_state.values())
    fl_unique = sum(1 for l in leads if l["state"] == "FL")
    fl_mailed = first_by_state.get("FL", 0)

    errors = []
    if len(pool_rows) != 507:
        errors.append("pool rows %d != 507" % len(pool_rows))
    if len(emailed_rows) != 162:
        errors.append("emailed rows %d != 162" % len(emailed_rows))
    if first_by_state != EXPECTED_EMAILED_BY_STATE:
        errors.append("first mails by state %s != %s"
                      % (first_by_state, EXPECTED_EMAILED_BY_STATE))
    bounced = sum(1 for l in leads
                  if "BOUNCED_DEAD_ADDRESS" in l["flags"])
    if bounced != 6:
        errors.append("bounced flagged %d != 6" % bounced)
    double = sum(1 for l in leads
                 if "NEVER_REMAIL_DOUBLE_SENT" in l["flags"])
    if double != 2:
        errors.append("double-sent flagged %d != 2" % double)
    held = sum(1 for l in leads if "HELD_DO_NOT_CONTACT" in l["flags"])
    if held != 1:
        errors.append("held flagged %d != 1" % held)
    if errors:
        raise SystemExit("FAIL: lead store does not reconcile:\n  - "
                         + "\n  - ".join(errors))

    payload = {
        "schema": lead_store.LEADS_SCHEMA,
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "built_by": "scripts/build_lead_store.py (Phase 3)",
        "sources": [
            {"file": os.path.relpath(POOL_CSV, WORKSPACE),
             "rows": len(pool_rows), "sha256": sha256_file(POOL_CSV)},
            {"file": os.path.relpath(PREMIER_CSV, WORKSPACE),
             "rows": 1, "sha256": sha256_file(PREMIER_CSV)},
        ] + emailed_sources,
        "meta": {
            "pool_rows": len(pool_rows),
            "pool_unique_after_dedup": len(order),
            "branch_rows_merged": branch_rows_merged,
            "emailed_rows": len(emailed_rows),
            "emailed_in_pool": len(emailed_rows) - len(sent_only),
            "sent_history_only": len(sent_only),
            "extra_held_rows": extra_held_rows,
            "premier_held_merged_into_pool": premier_merged,
            "total_unique_leads": len(leads),
            "source_row_total": (len(pool_rows) + len(sent_only)
                                 + extra_held_rows),
            "first_mails_total": total_first,
            "first_mails_by_state": dict(sorted(first_by_state.items())),
            "fl_unique_leads": fl_unique,
            "fl_first_mails": fl_mailed,
            "fl_max_first_mails": fl_unique,
            "flags": {
                "BOUNCED_DEAD_ADDRESS": bounced,
                "NEVER_REMAIL_DOUBLE_SENT": double,
                "HELD_DO_NOT_CONTACT": held,
                "HELD_LOW_CONFIDENCE": sum(
                    1 for l in leads
                    if "HELD_LOW_CONFIDENCE" in l["flags"]),
                "OTHER_CHANNEL_CONTACTED": sum(
                    1 for l in leads
                    if "OTHER_CHANNEL_CONTACTED" in l["flags"]),
                "SHARED_PHONE": sum(
                    1 for l in leads if "SHARED_PHONE" in l["flags"]),
                "SHARED_EMAIL": sum(
                    1 for l in leads if "SHARED_EMAIL" in l["flags"]),
            },
            "reconciliation": (
                "507 pool rows merge to %d unique pool businesses "
                "(%d branch rows merged into locations); + %d "
                "sent-history-only = %d unique leads. Premier Plumbing "
                "San Antonio (HELD_DO_NOT_CONTACT) was already in the "
                "pool, so the held flag merged into that lead — no extra "
                "row. Source-row total %d (507 + 30) is the pre-dedup "
                "count behind the old 537 figure (507 + 30). First mails: "
                "162 filed emailed.csv rows + 1 verified filing gap "
                "(Isackson Plumbing, CA — sent 2026-11-12, Gmail Sent "
                "message 1a1cfb0ff25cdb8c, no emailed.csv row) = 163 "
                "true total (CA 15, not the older locked 14). FL ceiling: "
                "%d unique FL leads, %d first mails sent — max first "
                "mails FL can reach is %d (the 2026-11-10 figure of 98 "
                "was the Nov 10 pool snapshot; the current pool + sent "
                "history gives %d)."
                % (len(order), branch_rows_merged, len(sent_only),
                   len(leads),
                   len(pool_rows) + len(sent_only) + extra_held_rows,
                   fl_unique, fl_mailed, fl_unique, fl_unique)),
        },
        "leads": leads,
    }
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--store-dir", default=None,
                        help="store dir (default: repo store/)")
    args = parser.parse_args()
    payload = build()
    store_dir = args.store_dir or os.path.join(BASE, "store")
    path = os.path.join(store_dir, "leads.json")
    store_io.update_json(path, lambda _old: payload, default=None)
    meta = payload["meta"]
    print("lead store built: %s" % path)
    print("  pool rows %d -> unique %d (merged %d branch rows)"
          % (meta["pool_rows"], meta["pool_unique_after_dedup"],
             meta["branch_rows_merged"]))
    print("  emailed rows %d (%d in pool, %d sent-history-only)"
          % (meta["emailed_rows"], meta["emailed_in_pool"],
             meta["sent_history_only"]))
    print("  total unique leads: %d (source rows %d)"
          % (meta["total_unique_leads"], meta["source_row_total"]))
    print("  first mails total %d: %s"
          % (meta["first_mails_total"], meta["first_mails_by_state"]))
    print("  flags: %s" % (meta["flags"],))
    print("  FL unique %d, FL first mails %d, FL max %d"
          % (meta["fl_unique_leads"], meta["fl_first_mails"],
             meta["fl_max_first_mails"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
