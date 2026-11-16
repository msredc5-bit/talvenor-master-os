"""Kit Sales — Vet Kit outreach DRAFT (section agent, NEW)।

Role (ভূমিকা): যাচাই করা PA clinic-দের জন্য outreach email-এর DRAFT লেখা —
শুধু pa-vet-clinics.csv-এর verified clinic-দের জন্য, শুধু DRAFT।
Gate (গেট): পাঠাতে Boss-এর `send` লাগে। DRAFT নিজে পাঠানো নয়।
Gate 0 status (গেট ০ অবস্থা): **NOT PASSED** — kit বানানো হয়নি, sale 0।
প্রতিটা output-এ prominent warning থাকে: "DRAFT ONLY — Gate 0 NOT passed,
do not send until Boss says go"। Email channel **PAUSED** (2026-11-14 থেকে)।
যা কখনো করে না: মেইল পাঠায় না; sale হিসেবে কিছু চিহ্নিত করে না
(mark_sold মানেই blocked-gate0); prospect-কে $49 quote করে না Boss confirm
না করলে (draft-এ price জায়গায় placeholder থাকে); contact details
বানায় না — public email না থাকলে "Not publicly listed" clinic-কে email
draft লেখে না; CSV-এর বাইরে কাউকে draft লেখে না; কোনো file লেখে না;
network ছোঁয় না।
"""

import csv
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
GATED_ACTIONS = ("send", "publish", "spend", "delete")

WARNING = ("DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go. "
           "Email channel PAUSED since 2026-11-14. Kit not built yet (0/6), sale 0.")


def _dept_dir():
    """kit-outline.md খুঁজে department dir বের করা (read-only source)।"""
    here = os.path.dirname(os.path.abspath(__file__))
    node = here
    for _ in range(6):
        if os.path.isfile(os.path.join(node, "kit-outline.md")):
            return node
        node = os.path.dirname(node)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))


def _read_pa_list():
    """pa-vet-clinics.csv পড়া (read-only)।"""
    path = os.path.join(_dept_dir(), "pa-vet-list", "pa-vet-clinics.csv")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except (FileNotFoundError, OSError):
        return []


def _find_clinic(rows, name):
    want = (name or "").strip().lower()
    if not want:
        return None
    for row in rows:
        if (row.get("clinic_name") or "").strip().lower() == want:
            return row
    return None


def _first_emailable(rows):
    """প্রথম verified clinic যার public email আছে (CSV order)।"""
    for row in rows:
        email = (row.get("public_email") or "").strip()
        if email and email != "Not publicly listed" and "@" in email:
            return row
    return None


def _load_gateway(gateway, approvals_path):
    """ApprovalGateway lazy import — শুধু gated কাজে দরকার হলে।"""
    if gateway is not None:
        return gateway
    ceo_core = os.path.join(os.path.dirname(_dept_dir()), "00-CEO-Core")
    if ceo_core not in sys.path:
        sys.path.insert(0, ceo_core)
    from human_approval_gateway import ApprovalGateway  # noqa: PLC0415
    if approvals_path:
        return ApprovalGateway(approvals_path=approvals_path)
    return ApprovalGateway()


def _draft_with_brain(brain, prompt, static_text):
    """brain থাকলে brain.complete(prompt) ব্যবহার করে [MOCK DRAFT] লেখা;
    না থাকলে static DRAFT text। কখনো live call / network নয় — brain mock।"""
    if brain is not None:
        try:
            mock_text = brain.complete(prompt)
        except Exception:  # noqa: BLE001
            mock_text = ""
        if mock_text:
            return "[MOCK DRAFT]\n" + str(mock_text) + "\n\n---\n" + static_text
    return "DRAFT ONLY\n" + static_text


def _gated_check(agent, task, gateway, approvals_path):
    """gated_action থাকলে PENDING ফেরত দেয়; approved হলে None (শুধু DRAFT-এ
    এগোনো যাবে — agent কখনো gated action execute করে না)।"""
    gated_action = (task or {}).get("gated_action")
    if not gated_action:
        return None
    if gated_action not in GATED_ACTIONS:
        return {"status": "error",
                "error": "Unknown gated action %r." % (gated_action,),
                "draft_only": True, "mock_brain": True, "gate": agent.gate}
    gw = _load_gateway(gateway, approvals_path)
    approval_id = task.get("approval_id")
    if approval_id:
        try:
            if gw.is_approved(approval_id):
                return None
        except Exception:  # noqa: BLE001
            pass
    approval = gw.request(gated_action, task.get("title") or agent.task_kind,
                          "Digital-Product-Section-Agent")
    return {"status": "pending-approval", "approval": approval,
            "draft_only": True, "mock_brain": True, "gate": agent.gate}


def _email_draft(clinic_name, city):
    """Outreach email DRAFT (plain US English)। Price জায়গায় placeholder —
    Boss confirm না করলে $49 লেখা হয় না।"""
    return "\n".join([
        "Subject: Missed appointments — a simple fix for %s?" % clinic_name,
        "",
        "Hi team at %s (%s)," % (clinic_name, city),
        "",
        "I'm Mainuddin from Talvenor. We work with independent vet clinics on one specific problem: no-show appointments.",
        "",
        "AAHA reports a no-show rate of about 11%, and the average vet visit is about $200 (AVMA 2025) — for a typical clinic that can mean roughly $50k–$150k a year at risk (labeled estimate).",
        "",
        "We put together a Vet No-Show Recovery Kit for front desks: a reminder cadence pack (72h / 24h / 2h), same-day rebooking scripts, a one-page waitlist-fill SOP, a no-show log with a $ tracker, a deposit / no-show policy template, and a front-desk quick card.",
        "",
        "[Price — Boss confirms before sending. Do NOT quote a price to a prospect without Boss confirming.]",
        "",
        "If it's useful, you can book a 15-minute call here:",
        BOOKING_LINK,
        "or reach us at %s." % PHONE,
        "",
        "Best,",
        "Mainuddin — Talvenor",
    ])


class KitSalesAgent:
    """Verified PA clinic-দের জন্য outreach DRAFT লেখে — পাঠায় না।"""

    task_kind = "kit_sales"
    gate = "send"
    section = "sales"
    role = "Kit Sales"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        payload = task.get("payload") or {}
        if payload.get("mark_sold") or payload.get("mark_launched"):
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section,
                    "output": WARNING + "\nSale/launch দাবি Gate 0-তে আটকে আছে — কিছুই sold হিসেবে লেখা হয়নি, sale এখনো 0।",
                    "notes": "Gate 0 NOT PASSED — sale চিহ্নিত করা যাবে না।",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        rows = _read_pa_list()
        clinic_name = payload.get("clinic_name")
        note = "কোনো clinic-কে দুইবার মেইল করা যাবে না (launch-এর সময়)। এই draft পাঠানো হয়নি।"
        if clinic_name:
            clinic = _find_clinic(rows, clinic_name)
            if clinic is None:
                static_text = "\n".join([
                    WARNING,
                    "Clinic '%s' — pa-vet-clinics.csv-এ পাওয়া যায়নি। Verified list-এর বাইরে কাউকে addressed draft লেখা হয় না।" % clinic_name,
                    "নিচে generic template (placeholders সহ) — শুধু verified clinic পাওয়া গেলে ব্যবহার করা যাবে, Boss-এর 'send'-এর পরে।",
                    "",
                    _email_draft("[CLINIC NAME]", "[CITY]"),
                ])
                output = _draft_with_brain(
                    brain, "Vet Kit outreach email draft (generic template)", static_text)
                return {"status": "draft-ready", "task_kind": self.task_kind,
                        "section": self.section, "clinic_verified": False,
                        "output": output, "notes": note,
                        "draft_only": True, "mock_brain": True, "gate": self.gate}
            email = (clinic.get("public_email") or "").strip()
            if not email or email == "Not publicly listed" or "@" not in email:
                static_text = "\n".join([
                    WARNING,
                    "%s (%s) — public email নেই ('Not publicly listed')। Email draft লেখা যাবে না — contact details বানানো যাবে না।" % (
                        clinic.get("clinic_name"), clinic.get("city")),
                    "নিচে generic template (placeholders সহ) — শুধু public email পাওয়া গেলে ব্যবহার করা যাবে।",
                    "",
                    _email_draft("[CLINIC NAME]", "[CITY]"),
                ])
                output = _draft_with_brain(
                    brain, "Vet Kit outreach email draft (generic template)", static_text)
                return {"status": "draft-ready", "task_kind": self.task_kind,
                        "section": self.section, "clinic_verified": True,
                        "clinic": clinic.get("clinic_name"),
                        "output": output, "notes": note,
                        "draft_only": True, "mock_brain": True, "gate": self.gate}
            static_text = "\n".join([
                WARNING,
                "To (verified, pa-vet-clinics.csv): %s, %s — %s (source: %s)।" % (
                    clinic.get("clinic_name"), clinic.get("city"),
                    clinic.get("public_email"), clinic.get("source_url")),
                "",
                _email_draft(clinic.get("clinic_name"), clinic.get("city")),
            ])
            output = _draft_with_brain(
                brain, "Vet Kit outreach email draft for %s" % clinic.get("clinic_name"), static_text)
            return {"status": "draft-ready", "task_kind": self.task_kind,
                    "section": self.section, "clinic_verified": True,
                    "clinic": clinic.get("clinic_name"),
                    "output": output, "notes": note,
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        clinic = _first_emailable(rows)
        if clinic is None:
            static_text = "\n".join([
                WARNING,
                "pa-vet-clinics.csv-এ public email-সহ কোনো clinic পাওয়া যায়নি — addressed draft লেখা যাবে না।",
                "",
                _email_draft("[CLINIC NAME]", "[CITY]"),
            ])
            output = _draft_with_brain(
                brain, "Vet Kit outreach email draft (generic template)", static_text)
            return {"status": "draft-ready", "task_kind": self.task_kind,
                    "section": self.section, "clinic_verified": False,
                    "output": output, "notes": note,
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        static_text = "\n".join([
            WARNING,
            "To (verified, pa-vet-clinics.csv — প্রথম emailable row): %s, %s — %s (source: %s)।" % (
                clinic.get("clinic_name"), clinic.get("city"),
                clinic.get("public_email"), clinic.get("source_url")),
            "",
            _email_draft(clinic.get("clinic_name"), clinic.get("city")),
        ])
        output = _draft_with_brain(
            brain, "Vet Kit outreach email draft for %s" % clinic.get("clinic_name"), static_text)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section, "clinic_verified": True,
                "clinic": clinic.get("clinic_name"),
                "output": output, "notes": note,
                "draft_only": True, "mock_brain": True, "gate": self.gate}
