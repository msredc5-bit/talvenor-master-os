"""Clinic Researcher — PA vet list যাচাই + বাড়ানো (section agent)।

Role (ভূমিকা): pa-vet-clinics.csv-এর যাচাই করা list-এর অবস্থা জানানো আর
নতুন clinic যাচাইয়ের নিয়ম লেখা — লক্ষ্য ১০০ independent PA vet clinic।
Gate (গেট): কোনো gate নেই — list বানানো নিরাপদ কাজ। কিন্তু list থেকে
কাউকে মেইল করতে Boss-এর `send` লাগে, আর email channel এখন PAUSED
(2026-11-14 থেকে)।
Gate 0 status (গেট ০ অবস্থা): **NOT BLOCKED** — list বাড়ানো Gate 0-র
বাইরে করা যায়; তবে plan অনুযায়ী বাকি 61 clinic Gate 0-র পরে পূর্ণ করা হবে।
যা কখনো করে না: contact details বানায় না — public-এ না থাকলে
"Not publicly listed" লেখে; chain (Banfield, VCA, Vetco, BluePearl,
Thrive, PetVet365) list-এ আনে না; কাউকে মেইল/ফোন করে না (no outreach);
CSV overwrite করে না — এই agent কোনো file লেখে না।
"""

import csv
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
PA_LIST_TARGET = 100
GATED_ACTIONS = ("send", "publish", "spend", "delete")

EXCLUDED_CHAINS = ["Banfield", "VCA", "Vetco", "BluePearl", "Thrive",
                   "PetVet365", "PetVet Care Centers"]

NEXT_CITIES_PLAN = [
    "Pittsburgh আশেপাশে", "Harrisburg আশেপাশে", "Lehigh Valley",
    "Bucks / Montgomery County", "Pittsburgh suburbs", "Central PA ছোট শহর",
]


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
    """pa-vet-clinics.csv পড়া (read-only) — row + শহর ভাগ।"""
    path = os.path.join(_dept_dir(), "pa-vet-list", "pa-vet-clinics.csv")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except (FileNotFoundError, OSError):
        return []


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


class ClinicResearcherAgent:
    """PA vet list-এর অবস্থা + যাচাইয়ের নিয়ম দেয় — outreach করে না।"""

    task_kind = "clinic_research"
    gate = None
    section = "research"
    role = "Clinic Researcher"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        rows = _read_pa_list()
        cities = {}
        with_email = 0
        for row in rows:
            city = (row.get("city") or "").strip()
            if city:
                cities[city] = cities.get(city, 0) + 1
            email = (row.get("public_email") or "").strip()
            if email and email != "Not publicly listed" and "@" in email:
                with_email += 1
        city_lines = "\n".join(
            "  - %s: %d" % (city, count)
            for city, count in sorted(cities.items()))
        static_text = "\n".join([
            "PA Vet Clinic List — যাচাই করা অবস্থা (read-only, pa-vet-clinics.csv থেকে):",
            "  Rows: %d / %d (বাকি %d — Gate 0-র পরে পূর্ণ করা হবে)।" % (
                len(rows), PA_LIST_TARGET, PA_LIST_TARGET - len(rows)),
            "  Public email আছে: %dটি; 'Not publicly listed': %dটি।" % (
                with_email, len(rows) - with_email),
            "  শহর ভাগ:",
            city_lines or "  (কোনো row নেই)",
            "",
            "Verification rule (যাচাইয়ের নিয়ম — pa-vet-list/README.md):",
            "  1. প্রতিটা clinic-এর নিজের official website প্রথমে (সবচেয়ে ভালো), নইলে directory listing (নাম + শহর + website/phone দেখা যায়)।",
            "  2. Chain EXCLUDED — list-এ আনা যাবে না: %s।" % ", ".join(EXCLUDED_CHAINS),
            "  3. Email/phone public-এ না থাকলে 'Not publicly listed' লিখতে হবে — কিছু বানানো যাবে না।",
            "  4. Target: independent companion-animal clinic, ১–৫ vet। Corporate chain নয়, solo mobile vet নয়।",
            "",
            "পরের শহর (README plan): %s।" % "; ".join(NEXT_CITIES_PLAN),
            "No outreach — এই agent কাউকে মেইল/ফোন করে না। List থেকে মেইল করতে Boss-এর 'send' লাগে, আর email channel এখন PAUSED (2026-11-14 থেকে)।",
        ])
        output = _draft_with_brain(
            brain, "PA vet clinic list status draft", static_text)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section,
                "pa_rows": len(rows), "pa_target": PA_LIST_TARGET,
                "with_email": with_email,
                "output": output,
                "notes": "যাচাই করা public তথ্য শুধু — কিছু বানানো নয়। কোনো clinic-কে মেইল করা হয়নি।",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
