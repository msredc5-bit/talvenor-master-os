"""QA-as-code for a tenant's call script (Phase 4 buildable part).

Runs acceptance checks against one tenant config + one synthetic
call script (a list of turns: {"role": "agent"|"caller",
"text": ...}). Returns a structured verdict: pass/fail per check +
overall verdict.

Checks (all read-only, pure functions):
  1. greeting_names_business — the first agent turn names the business.
  2. ai_disclosure_present — an agent turn carries the tenant's
     configured AI disclosure (or an equivalent AI-assistant line).
  3. life_safety_present — an agent turn asks the life-safety /
     emergency check.
  4. qualification_present — at least one configured qualification
     question appears in an agent turn.
  5. booking_confirmation — an agent turn confirms the booking AND
     carries the booking link.
  6. no_price_quoted — no agent turn quotes a price.
  7. no_invented_claims — no agent turn makes a guarantee or a
     superlative / served-count claim.
  8. transfer_rule_present — when transfer is enabled, an agent
     turn offers the transfer (not applicable when disabled).

All QA runs use SYNTHETIC fixtures only — see synthetic_call_script()
for the good script (a clearly-labelled fictional example tenant,
never a real business, never a real client; 0 paying clients exist).
No network, no send, no publish, no spend.
"""

import re

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"

_EMERGENCY_RE = re.compile(
    r"emergency|anyone hurt|gas leak|immediate danger|call 911|\b911\b|"
    r"life.?threatening|flooding.*(everywhere|rising)|"
    r"smell (of )?gas",
    re.IGNORECASE)

_PRICE_RE = re.compile(
    r"\$|\d[\d,]*\s*/\s*(mo|month|yr|year)\b|"
    r"\b\d[\d,]*\s*(usd|dollars)\b|per month|a month",
    re.IGNORECASE)

_CLAIM_RE = re.compile(
    r"guarantee|#1\b|number one|best in (the|town|the state)|"
    r"we('ve| have) (served|helped|booked) \d|"
    r"\d{2,}\+? (customers|clients|jobs|reviews)|"
    r"rated \d(\.\d)? ?/ ?5",
    re.IGNORECASE)

_TRANSFER_RE = re.compile(
    r"transfer|connect you|put you through|patch you through",
    re.IGNORECASE)

_CONFIRM_RE = re.compile(
    r"confirmed|booked|you'?re (all )?set|scheduled|all confirmed",
    re.IGNORECASE)


def _norm(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def synthetic_call_script(tenant):
    """The good synthetic call script for the fixture tenant.

    Fictional caller, fictional job — a burst pipe at a fictional
    address. Every check passes against this script.
    """
    name = tenant["business"]["name"]
    disclosure = tenant["call_handling"]["ai_disclosure"]
    greeting = tenant["call_handling"]["greeting_template"].replace(
        "{business_name}", name)
    question = tenant["qualification"]["questions"][0]
    link = tenant["booking"]["calendar_link"]
    return {
        "id": "qa-script-good-001",
        "synthetic": True,
        "tenant_id": tenant.get("tenant_id"),
        "turns": [
            {"role": "agent", "text": greeting},
            {"role": "agent", "text": disclosure},
            {"role": "caller",
             "text": "Hi, I have a burst pipe in the kitchen, water "
                     "everywhere."},
            {"role": "agent",
             "text": "That sounds urgent — first, is anyone hurt, and "
                     "is this an emergency where someone could be in "
                     "danger? If so, please call 911 right away and "
                     "then come back to me."},
            {"role": "caller",
             "text": "No one is hurt, but the water keeps coming."},
            {"role": "agent", "text": question},
            {"role": "caller",
             "text": "A leak — the pipe under the sink split open."},
            {"role": "agent",
             "text": "Got it. I can book a technician for tomorrow "
                     "morning — would that work? If you would rather "
                     "speak to a person, I can transfer you to the "
                     "office."},
            {"role": "caller", "text": "Tomorrow morning works."},
            {"role": "agent",
             "text": "You are booked for tomorrow at 9 AM — confirmed. "
                     "Here is your booking link: " + link + ". "
                     "We will text you a reminder before the visit."},
        ],
    }


def run_qa(tenant, script):
    """Run the acceptance checks for one tenant + one call script.

    Returns {verdict, checks, tenant_id, script_id, turns_checked}.
    verdict is "pass" only when every applicable check passes.
    A malformed script fails closed (verdict "fail", reason in the
    checks).
    """
    checks = []
    tenant_id = None
    script_id = None
    turns = []

    def add(check_id, title, passed, detail):
        checks.append({
            "id": check_id,
            "title": title,
            "passed": bool(passed),
            "detail": detail,
        })

    if not isinstance(tenant, dict):
        add("tenant_valid", "Tenant config is an object", False,
            "tenant is not an object")
        return {"verdict": "fail", "checks": checks, "tenant_id": None,
                "script_id": None, "turns_checked": 0}
    tenant_id = tenant.get("tenant_id")
    if not isinstance(script, dict):
        add("script_valid", "Call script is an object", False,
            "script is not an object")
        return {"verdict": "fail", "checks": checks,
                "tenant_id": tenant_id, "script_id": None,
                "turns_checked": 0}
    script_id = script.get("id")
    turns = script.get("turns") or []
    if not isinstance(turns, list) or not turns:
        add("script_valid", "Call script has turns", False,
            "script has no turns")
        return {"verdict": "fail", "checks": checks,
                "tenant_id": tenant_id, "script_id": script_id,
                "turns_checked": 0}

    agent_turns = [t for t in turns
                   if isinstance(t, dict) and t.get("role") == "agent"]
    agent_text = " ".join(str(t.get("text") or "") for t in agent_turns)
    agent_norm = _norm(agent_text)
    business = tenant.get("business") or {}
    name = (business.get("name") or "").strip()

    # 1. Greeting names the business.
    first_agent = agent_turns[0] if agent_turns else {}
    first_text = str(first_agent.get("text") or "")
    add("greeting_names_business",
        "Greeting names the business",
        bool(name) and name.lower() in first_text.lower(),
        "first agent turn names '" + name + "'"
        if name and name.lower() in first_text.lower()
        else "first agent turn does not name the business")

    # 2. AI disclosure present.
    disclosure = (tenant.get("call_handling") or {}).get("ai_disclosure")
    disc_norm = _norm(disclosure) if disclosure else ""
    disc_ok = bool(disc_norm) and disc_norm in agent_norm
    if not disc_ok:
        disc_ok = ("ai" in agent_norm
                   and ("assistant" in agent_norm
                        or "receptionist" in agent_norm))
    add("ai_disclosure_present",
        "AI disclosure present",
        disc_ok,
        "configured disclosure appears in an agent turn"
        if disc_ok else "no AI disclosure in any agent turn")

    # 3. Life-safety check present.
    add("life_safety_present",
        "Life-safety / emergency check present",
        bool(_EMERGENCY_RE.search(agent_text)),
        "an agent turn asks the emergency check"
        if _EMERGENCY_RE.search(agent_text)
        else "no agent turn asks about an emergency")

    # 4. At least one qualification question present.
    questions = (tenant.get("qualification") or {}).get("questions") or []
    q_hit = None
    for q in questions:
        if _norm(q) and _norm(q) in agent_norm:
            q_hit = q
            break
    add("qualification_present",
        "Qualification question present",
        q_hit is not None,
        "agent asks: '" + q_hit[:80] + "'"
        if q_hit else "no configured qualification question is asked")

    # 5. Booking confirmation + link.
    link = (tenant.get("booking") or {}).get("calendar_link") or ""
    link_ok = bool(link) and link in agent_text
    confirm_ok = bool(_CONFIRM_RE.search(agent_text))
    add("booking_confirmation",
        "Booking ends with confirmation + booking link",
        link_ok and confirm_ok,
        ("confirmation word and booking link both present"
         if link_ok and confirm_ok else
         "missing confirmation word" if link_ok else
         "missing booking link" if confirm_ok else
         "missing confirmation word and booking link"))

    # 6. No price quoted.
    add("no_price_quoted",
        "No price quoted to the caller",
        not _PRICE_RE.search(agent_text),
        "no price in any agent turn"
        if not _PRICE_RE.search(agent_text)
        else "an agent turn quotes a price")

    # 7. No invented claims.
    add("no_invented_claims",
        "No guarantee / superlative / served-count claim",
        not _CLAIM_RE.search(agent_text),
        "no invented claim in any agent turn"
        if not _CLAIM_RE.search(agent_text)
        else "an agent turn makes an invented claim")

    # 8. Transfer rule present when enabled.
    transfer_on = bool(
        (tenant.get("escalation") or {}).get("transfer_enabled"))
    if transfer_on:
        hit = bool(_TRANSFER_RE.search(agent_text))
        add("transfer_rule_present",
            "Transfer offered (transfer is enabled)",
            hit,
            "an agent turn offers the transfer"
            if hit else "transfer is enabled but no agent turn "
                       "offers it")
    else:
        add("transfer_rule_present",
            "Transfer offered (transfer is disabled)",
            True,
            "not applicable — transfer is disabled in the tenant "
            "config")

    verdict = "pass" if all(c["passed"] for c in checks) else "fail"
    return {
        "verdict": verdict,
        "checks": checks,
        "tenant_id": tenant_id,
        "script_id": script_id,
        "turns_checked": len(turns),
    }


if __name__ == "__main__":
    # Self-test — pure functions, no store, no network, no send.
    import tenant_schema
    tenant = tenant_schema.synthetic_tenant()
    good = run_qa(tenant, synthetic_call_script(tenant))
    assert good["verdict"] == "pass", good["checks"]
    assert len(good["checks"]) == 8
    assert good["turns_checked"] == 10

    def broken(mutate):
        script = synthetic_call_script(tenant)
        mutate(script)
        return run_qa(tenant, script)

    def drop_disclosure(s):
        s["turns"] = [t for t in s["turns"]
                      if "AI receptionist" not in t["text"]
                      and "speaking with Talvenor" not in t["text"]]
        # Also strip the bare "AI" from the greeting so no fallback hit.
        for t in s["turns"]:
            t["text"] = t["text"].replace(
                " — this is Talvenor, the AI receptionist.",
                " — this is Talvenor.")
    r = broken(drop_disclosure)
    assert r["verdict"] == "fail"
    assert [c for c in r["checks"]
            if c["id"] == "ai_disclosure_present"][0]["passed"] is False

    def drop_life_safety(s):
        s["turns"] = [t for t in s["turns"]
                      if "emergency" not in t["text"].lower()
                      and "911" not in t["text"]]
    r = broken(drop_life_safety)
    assert r["verdict"] == "fail"
    assert [c for c in r["checks"]
            if c["id"] == "life_safety_present"][0]["passed"] is False

    def quote_price(s):
        s["turns"][-1]["text"] += " The visit costs $99."
    r = broken(quote_price)
    assert r["verdict"] == "fail"
    assert [c for c in r["checks"]
            if c["id"] == "no_price_quoted"][0]["passed"] is False

    def drop_booking_link(s):
        for t in s["turns"]:
            t["text"] = t["text"].replace(BOOKING_LINK, "")
    r = broken(drop_booking_link)
    assert r["verdict"] == "fail"
    assert [c for c in r["checks"]
            if c["id"] == "booking_confirmation"][0]["passed"] is False

    def drop_transfer(s):
        for t in s["turns"]:
            t["text"] = t["text"].replace(
                " If you would rather speak to a person, I can "
                "transfer you to the office.", "")
    r = broken(drop_transfer)
    assert r["verdict"] == "fail"
    assert [c for c in r["checks"]
            if c["id"] == "transfer_rule_present"][0]["passed"] is False
    print("tenant_qa: OK (good synthetic script passes 8/8; each "
          "broken variant fails exactly its check)")
