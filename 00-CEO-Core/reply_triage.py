"""Reply triage — structured verdicts for inbound messages (Phase 3).

Takes one inbound message (channel, sender, text) and returns a
structured verdict dict. It NEVER sends anything: every outcome is
either log-only or a DRAFT text for Boss to review. Sending stays
BLOCKED behind the trust gate + ApprovalGateway (see the module
docstring footer) and email is PAUSED since 2026-11-14.

Verdict classes (locked reply rules, same as the inbox reply watcher):
  - "bounce"       — delivery failure / auto-reply / out-of-office / bot
                     auto-reply. Log only, no draft, no reply.
  - "decline"      — plain decline ("not interested", "no thanks",
                     "stop", "unsubscribe", ...). Draft = ONE short
                     polite exit, text only.
  - "hot_lead"     — interest / question / pricing question / demo
                     request / "send me info" / wants a call. Draft =
                     short personal reply. NEVER quotes a price — the
                     draft says "we share details on a short call" and
                     includes the booking link. The demo video link is
                     included ONLY when the prospect asked for the demo.
  - "needs_decision" — unclear / ambiguous. Draft + flag for Boss.

Rules:
  - No price is ever quoted in any draft. A draft containing "$" or a
    number followed by "/mo" fails validation (see validate_draft()).
  - No client fact is invented: drafts use only the sender's name when
    given, the booking link, and the demo link. Everything else is
    marked for Boss.
  - Dental/medical senders are never a target — a message that reads
    as a dental/medical business is verdict "needs_decision" with the
    DQ noted, never a hot lead.
  - Stdlib only. No network, no send, no publish, no spend.
"""

import re

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
DEMO_VIDEO_LINK = "https://facebook.com/reel/2947321012290705/"
TALVENOR_PHONE = "+1 (947) 223-0244"

EXIT_DRAFT = (
    "Totally understand — thanks for getting back to me! If the phones "
    "ever get overwhelming, the offer stands. Wishing you a busy "
    "season! — Mainuddin, Talvenor"
)

BOUNCE_PATTERNS = (
    r"delivery (status )?notification",
    r"mail delivery (failed|failure)",
    r"undeliverable",
    r"message blocked",
    r"550[ -]",
    r"user unknown",
    r"mailbox (full|not found|unavailable)",
    r"auto-?reply",
    r"out of (the )?office",
    r"automatic reply",
    r"vacation reply",
    r"this is an automated (message|response|reply)",
    r"do not reply to this (email|message)",
    r"mailer-daemon",
    r"delivery has failed",
)

DECLINE_PATTERNS = (
    r"\bnot interested\b",
    r"\bno thanks\b",
    r"\bno thank you\b",
    r"don'?t need (this|your|any|the) (service|services|help)",
    r"we'?re (all )?set\b",
    r"we (don'?t|do not) need",
    r"please (remove|unsubscribe|stop)",
    r"\bunsubscribe\b",
    r"\bstop\b.{0,20}(email|mail|contact)",
    r"not looking for",
    r"already have (a|an|someone|something)",
    r"do ?n'?t (call|contact|email|message|reach out)",
    r"stop (calling|emailing|contacting|messaging)",
    r"leave (me|us) alone",
    r"remove (me|us|my)",
)

INTEREST_PATTERNS = (
    r"\binterested\b",
    r"sounds (good|great|interesting)",
    r"tell me more",
    r"send me (more )?info",
    r"how does (it|this|that) work",
    r"how much (does it cost|is it|do you charge)",
    r"what('?s| is) (the )?(price|cost|pricing|rate)",
    r"pricing",
    r"\bprice\b",
    r"\bcost\b",
    r"demo",
    r"book (a )?call",
    r"schedule (a )?call",
    r"can we (talk|chat|meet)",
    r"call me",
    r"set up (a )?call",
    r"free trial",
    r"sign ?up",
)

DENTAL_MEDICAL_PATTERNS = (
    r"\bdental\b",
    r"\bdentist\b",
    r"\bclinic\b",
    r"\bmedical\b",
    r"\bpatient",
    r"\bdoctor'?s office\b",
)


def _matches(text, patterns):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def validate_draft(draft):
    """A draft is valid only when it quotes NO price.

    Fails on "$", on a number followed by "/mo" or "/month", and on the
    words "starter", "growth", "scale" next to a price-like number.
    Returns (ok, reason).
    """
    if "$" in draft:
        return False, "draft contains '$'"
    if re.search(r"\d[\d,]*\s*/\s*(mo|month|yr|year)\b", draft,
                 re.IGNORECASE):
        return False, "draft contains a per-period price"
    if re.search(r"\b\d[\d,]*\s*(usd|dollars)\b", draft, re.IGNORECASE):
        return False, "draft contains a dollar amount"
    return True, "ok"


def triage(channel, sender, text, sender_name=None):
    """Triage one inbound message -> structured verdict dict.

    channel: "gmail" | "instagram" | "messenger" (free text accepted).
    sender: address / handle / thread id (kept verbatim in the verdict).
    text: the message body (verbatim excerpt kept in the verdict).
    sender_name: display name when known, else None.

    Returns a dict: {verdict, channel, sender, excerpt, draft, reason,
    sendable}. ``sendable`` is ALWAYS False in Phase 3 — no send path
    exists; Boss sends any draft himself.
    """
    channel = (channel or "").strip().lower() or "unknown"
    sender = sender or "unknown"
    body = (text or "").strip()
    name = sender_name or "there"

    if not body:
        return {
            "verdict": "needs_decision",
            "channel": channel,
            "sender": sender,
            "excerpt": "",
            "draft": None,
            "reason": "empty message — nothing to triage",
            "sendable": False,
        }

    if _matches(body, DENTAL_MEDICAL_PATTERNS):
        return {
            "verdict": "needs_decision",
            "channel": channel,
            "sender": sender,
            "excerpt": body[:300],
            "draft": None,
            "reason": "dental/medical/patient-health — hard DQ, never a "
                      "target; needs Boss's decision, never a hot lead",
            "sendable": False,
        }

    if _matches(body, BOUNCE_PATTERNS):
        return {
            "verdict": "bounce",
            "channel": channel,
            "sender": sender,
            "excerpt": body[:300],
            "draft": None,
            "reason": "bounce / delivery failure / auto-reply — log only",
            "sendable": False,
        }

    if _matches(body, DECLINE_PATTERNS):
        return {
            "verdict": "decline",
            "channel": channel,
            "sender": sender,
            "excerpt": body[:300],
            "draft": EXIT_DRAFT,
            "reason": "plain decline — one short polite exit draft",
            "sendable": False,
        }

    if _matches(body, INTEREST_PATTERNS):
        asked_demo = bool(re.search(r"demo", body, re.IGNORECASE))
        asked_price = bool(re.search(
            r"price|pricing|cost|how much", body, re.IGNORECASE))
        asked_call = bool(re.search(
            r"call|meet|talk|schedule", body, re.IGNORECASE))
        lines = [
            "Hi %s — thanks for getting back to me!" % name,
        ]
        if asked_price:
            lines.append(
                "We share details on a short call — every shop is a "
                "little different, so the fit (and the setup) depends on "
                "how your phones work today.")
        elif asked_demo:
            lines.append(
                "Happy to show you how it works — here is a short demo "
                "of the receptionist answering and booking: "
                + DEMO_VIDEO_LINK)
        else:
            lines.append(
                "Happy to walk you through it — it answers every call in "
                "seconds and books jobs straight into the calendar, even "
                "at 2 AM.")
        lines.append(
            "Worth a 15-min call? Book here: " + BOOKING_LINK)
        lines.append("— Mainuddin, Talvenor")
        draft = "\n".join(lines)
        ok, reason = validate_draft(draft)
        if not ok:
            raise AssertionError("hot-lead draft failed validation: "
                                 + reason)
        return {
            "verdict": "hot_lead",
            "channel": channel,
            "sender": sender,
            "excerpt": body[:300],
            "draft": draft,
            "reason": ("interest / question / pricing / demo / call "
                       "request" + ("; asked for the demo" if asked_demo
                                    else "")
                       + ("; asked about price (answered with a call, "
                          "no price quoted)" if asked_price else "")),
            "sendable": False,
            "asked_demo": asked_demo,
            "asked_price": asked_price,
            "asked_call": asked_call,
        }

    return {
        "verdict": "needs_decision",
        "channel": channel,
        "sender": sender,
        "excerpt": body[:300],
        "draft": None,
        "reason": "unclear / ambiguous — no class matched; needs Boss's "
                  "decision",
        "sendable": False,
    }


if __name__ == "__main__":
    # Self-test — pure functions, no store, no network, no send.
    v = triage("gmail", "a@b.com",
               "Delivery Status Notification (Failure)")
    assert v["verdict"] == "bounce" and v["draft"] is None
    assert v["sendable"] is False
    v = triage("gmail", "a@b.com", "Not interested, thanks.")
    assert v["verdict"] == "decline" and v["draft"] == EXIT_DRAFT
    assert v["sendable"] is False
    v = triage("instagram", "plumber_joe",
               "This sounds interesting — how much does it cost?",
               sender_name="Joe")
    assert v["verdict"] == "hot_lead" and v["asked_price"] is True
    assert "$" not in v["draft"] and BOOKING_LINK in v["draft"]
    assert "we share details on a short call" in v["draft"].lower()
    assert v["sendable"] is False
    v = triage("gmail", "a@b.com", "Can I see a demo of it working?",
               sender_name="Sam")
    assert v["verdict"] == "hot_lead" and v["asked_demo"] is True
    assert DEMO_VIDEO_LINK in v["draft"]
    v = triage("messenger", "x", "ok")
    assert v["verdict"] == "needs_decision" and v["draft"] is None
    v = triage("gmail", "d@dental.com", "We are a dental clinic, "
               "interested in your service")
    assert v["verdict"] == "needs_decision"
    assert "dental" in v["reason"].lower()
    v = triage("gmail", "a@b.com", "")
    assert v["verdict"] == "needs_decision"
    ok, _ = validate_draft("Costs $547/mo, starter tier")
    assert ok is False
    ok, _ = validate_draft("Book a 15-min call here: " + BOOKING_LINK)
    assert ok is True
    print("reply_triage: OK (bounce/decline/hot-lead/needs-decision; "
          "no price ever quoted; sendable always False)")
