"""Live tool connections — CODE ONLY, gated, never executes (Phase 9).

Two handlers that connect the Master OS to the real world:

  1. gmail_send   — send an email via the hatch_gws_cli Gmail CLI.
  2. n8n_trigger  — trigger an n8n webhook with a POST (urllib).

HARD RULES (Boss's gates, written in code):
  - Credentials come ONLY from environment variables. No key, password,
    token, or webhook URL is ever written in a file.
      TALVENOR_GMAIL_SENDER    — the From address for gmail_send.
      TALVENOR_N8N_WEBHOOK_URL — the n8n webhook URL for n8n_trigger.
  - Both tools are registered gated=true in tools.json. The dispatcher
    (tool_calling.call_tool) records a PENDING approval and never runs
    these handlers. There is no path in this repo that executes them.
  - Each handler falls back LOUDLY to DRAFT + a reason when its
    credential is missing. Nothing is ever sent.
  - THIS MODULE CONTAINS NO subprocess.run / urlopen CALL. The live
    execution itself is deliberately absent in Phase 9: the handlers
    only BUILD the exact command / request that the live path would
    use, and return it as a dry-run plan (sent=False, always).
    Real sending is future work, after Boss enables it with his word.
  - Webhook URLs may contain a secret token, so previews NEVER print
    the full URL — only scheme + host + a redacted path.

Handler return shape (same as the mock handlers in tool_calling.py):
  {"output": str, "notes": [str], "draft_only": bool,
   "live_ready": bool, "sent": False}

Stdlib only. No network is ever opened by this module.
"""

import json
import os
import shlex
import urllib.parse
import urllib.request

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"

# Environment variable names — the ONLY places credentials may live.
ENV_GMAIL_SENDER = "TALVENOR_GMAIL_SENDER"
ENV_N8N_WEBHOOK_URL = "TALVENOR_N8N_WEBHOOK_URL"


def _redact_url(url):
    """Show scheme + host + a redacted path. The token never appears."""
    try:
        parts = urllib.parse.urlsplit(url)
    except (ValueError, AttributeError):
        return "<unparseable url>"
    host = parts.netloc or "<no host>"
    path = parts.path or "/"
    shown = path[:8] + "..." if len(path) > 8 else path
    return f"{parts.scheme or 'https'}://{host}{shown} [redacted]"


def build_gmail_command(to, subject, body, sender):
    """The exact hatch_gws_cli argv the live path would run.

    Built, never executed. Returns a list (argv), not a shell string,
    so no shell injection is possible from the arguments.
    """
    return [
        "hatch_gws_cli", "gmail", "+send",
        "--to", to,
        "--from", sender,
        "--subject", subject,
        "--body", body,
    ]


def build_n8n_request(url, payload):
    """The exact urllib Request the live path would send.

    Built, never opened (no urlopen call anywhere in this module).
    Returns the Request object; callers only read its preview.
    """
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    return request


def gmail_send(args, context=None):
    """Send an email via hatch_gws_cli — DRAFT fallback, never sends.

    Args: to (required), subject (required), body (required).
    Credential: TALVENOR_GMAIL_SENDER env var (the From address).
    """
    to = (args.get("to") or "").strip()
    subject = (args.get("subject") or "").strip()
    body = args.get("body") or ""
    if not to:
        return {
            "output": "",
            "notes": ["gmail_send needs a 'to' address."],
            "error": "gmail_send needs a 'to' address.",
        }
    if not subject:
        return {
            "output": "",
            "notes": ["gmail_send needs a 'subject'."],
            "error": "gmail_send needs a 'subject'.",
        }
    if not body:
        return {
            "output": "",
            "notes": ["gmail_send needs a 'body'."],
            "error": "gmail_send needs a 'body'.",
        }

    sender = (os.environ.get(ENV_GMAIL_SENDER) or "").strip()
    draft = (
        f"[DRAFT ONLY — never sent] To: {to}\n"
        f"From: {sender or '(no sender configured)'}\n"
        f"Subject: {subject}\n\n{body}\n\n"
        f"Book a 15-minute demo call here: {BOOKING_LINK}"
    )
    if not sender:
        # LOUD fallback: no credential, so this is a draft, not a send.
        return {
            "output": draft,
            "notes": [
                "DRAFT ONLY — nothing was sent.",
                f"No credential: {ENV_GMAIL_SENDER} is not set. "
                "Set it in the environment (never in a file) to enable "
                "the live-ready path.",
                "Email sending is PAUSED — this draft was never sent.",
            ],
            "draft_only": True,
            "live_ready": False,
            "sent": False,
        }

    # Credential present — still only a dry run. The command is built
    # and shown, never executed (no subprocess call in this module).
    command = build_gmail_command(to, subject, body, sender)
    preview = " ".join(shlex.quote(part) for part in command)
    return {
        "output": draft + f"\n\n[DRY RUN — command that would run]\n{preview}",
        "notes": [
            "LIVE-READY — dry run only. Nothing was sent.",
            "Gated tool: the dispatcher records pending-approval and "
            "never executes this handler.",
            "To send for real, Boss's exact gate word is required.",
        ],
        "draft_only": False,
        "live_ready": True,
        "sent": False,
    }


def n8n_trigger(args, context=None):
    """Trigger an n8n webhook with a POST — DRAFT fallback, never sends.

    Args: payload (required dict), event (optional string).
    Credential: TALVENOR_N8N_WEBHOOK_URL env var.
    """
    payload = args.get("payload")
    if not isinstance(payload, dict):
        return {
            "output": "",
            "notes": ["n8n_trigger needs a 'payload' object."],
            "error": "n8n_trigger needs a 'payload' object.",
        }
    event = (args.get("event") or "").strip()
    body = {"event": event, "payload": payload} if event else {"payload": payload}

    url = (os.environ.get(ENV_N8N_WEBHOOK_URL) or "").strip()
    draft = (
        "[DRAFT ONLY — never sent] n8n webhook trigger\n"
        f"Event: {event or '(none)'}\n"
        f"Payload keys: {', '.join(sorted(payload)) or '(empty)'}\n"
        f"Payload: {json.dumps(payload, ensure_ascii=False)}"
    )
    if not url:
        # LOUD fallback: no credential, so this is a draft, not a trigger.
        return {
            "output": draft,
            "notes": [
                "DRAFT ONLY — nothing was sent.",
                f"No credential: {ENV_N8N_WEBHOOK_URL} is not set. "
                "Set it in the environment (never in a file) to enable "
                "the live-ready path.",
                "n8n workflows are READY, NOT LIVE.",
            ],
            "draft_only": True,
            "live_ready": False,
            "sent": False,
        }

    # Credential present — still only a dry run. The request is built
    # and previewed, never opened (no urlopen call in this module).
    request = build_n8n_request(url, body)
    preview = (
        f"POST {_redact_url(url)}\n"
        f"Content-Type: application/json\n"
        f"Body bytes: {len(request.data)}"
    )
    return {
        "output": draft + f"\n\n[DRY RUN — request that would be sent]\n{preview}",
        "notes": [
            "LIVE-READY — dry run only. Nothing was sent.",
            "Webhook URL is redacted in this preview — the token never "
            "appears in output or logs.",
            "Gated tool: the dispatcher records pending-approval and "
            "never executes this handler.",
        ],
        "draft_only": False,
        "live_ready": True,
        "sent": False,
    }


LIVE_HANDLERS = {
    "gmail_send": gmail_send,
    "n8n_trigger": n8n_trigger,
}
