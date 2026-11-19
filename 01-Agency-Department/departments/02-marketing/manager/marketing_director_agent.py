"""Marketing Director Agent — Marketing department-এর manager (Phase 1).

ভূমিকা (role): Marketing department-এর ৪ জন existing specialist-কে delegate
করা — content plan, video produce, caption write, publish prep। এই manager
শুধু delegation plan-এর DRAFT বানায়; কোনো worker execute করে না, নিজে
কিছু post করে না।
Gate: ok — delegation plan-এ Boss-এর "ok" লাগে; publish-এর gate "post it",
send/spend/delete কোনো gated action এই manager নিজে করে না।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
Agency Chief wiring Phase 2 DONE — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।
এই manager কখনো করে না: কোনো worker execute করে না, কিছু post/publish
করে না, paid ad চালায় না, খরচ করে না, মুছে না, client-এর তথ্য/দাম/
পরিসংখ্যান বানায় না, কোনো guarantee দেয় না, dental/medical বা
patient-health ব্যবসা নেয় না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

DEPARTMENT_TASKS = {
    "content_plan": {
        "specialist": "ContentPlanner",
        "file": "engine/workers/src/workers/marketing.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "video_produce": {
        "specialist": "VideoProducer",
        "file": "engine/workers/src/workers/marketing.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "caption_write": {
        "specialist": "CaptionWriter",
        "file": "engine/workers/src/workers/marketing.py",
        "gate": None,
        "status": "EXISTING",
    },
    "publish_prep": {
        "specialist": "PublishPrep",
        "file": "engine/workers/src/workers/marketing.py",
        "gate": "post it",
        "status": "EXISTING",
    },
    "market_position": {
        "specialist": "Market Positioning Agent",
        "file": "ROLE-ONLY — skill: departments/02-marketing/skills/marketing-director-agent.md",
        "gate": None,
        "status": "ROLE-ONLY",
    },
    "social_manage": {
        "specialist": "Social Media Agent",
        "file": "ROLE-ONLY — skill: departments/02-marketing/skills/marketing-director-agent.md",
        "gate": "post it",
        "status": "ROLE-ONLY",
    },
    "ad_campaign": {
        "specialist": "Ad Campaign Agent",
        "file": "GAP — no worker file; paid ads not planned ($0 spend cap)",
        "gate": "ok",
        "status": "GAP",
    },
    "seo": {
        "specialist": "SEO Agent",
        "file": "ROLE-ONLY — skill: departments/02-marketing/skills/marketing-director-agent.md",
        "gate": None,
        "status": "ROLE-ONLY",
    },
    "analytics": {
        "specialist": "Analytics Agent",
        "file": "ROLE-ONLY — skill: departments/02-marketing/skills/marketing-director-agent.md",
        "gate": None,
        "status": "ROLE-ONLY",
    },
}


class MarketingDirectorAgent:
    """Marketing specialist-দের delegation plan DRAFT বানায়। কখনো execute করে না, post করে না।"""

    task_kind = "manage_marketing"
    gate = "ok"
    department = "02-marketing"
    role = "Marketing Director Agent"

    def _gateway(self, approvals_path=None):
        """ApprovalGateway lazy-load — top level-এ কোনো repo import নয়।"""
        here = os.path.dirname(os.path.abspath(__file__))
        ceo_core = os.path.normpath(os.path.join(
            here, "..", "..", "..", "..", "00-CEO-Core"))
        if ceo_core not in sys.path:
            sys.path.insert(0, ceo_core)
        from human_approval_gateway import ApprovalGateway
        if approvals_path:
            return ApprovalGateway(approvals_path=approvals_path)
        return ApprovalGateway()

    def _request_approval(self, gateway, gated_action, title):
        """PENDING approval record করা — execute নয়, auto-approve নয়।"""
        action = _GATE_ACTION_MAP.get(gated_action, gated_action)
        if action in _GATED_ACTIONS:
            return gateway.request(action, title, type(self).__name__)
        return {
            "id": None,
            "action": gated_action,
            "detail": title,
            "requested_by": type(self).__name__,
            "status": "pending",
            "note": "Gate word approval needed; not a gateway action, so no record was written.",
        }

    def _prompt(self, task):
        payload = task.get("payload") or {}
        task_kind = task.get("task_kind") or self.task_kind
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        return (
            "Marketing delegation plan draft for Talvenor. "
            f"Requested task kind: {task_kind}. Topic: {topic}. "
            "Name the specialist, their file, the gate needed, and the "
            "honest status. PublishPrep prepares only — it never posts. "
            "Do not invent any client fact; mark missing facts "
            "'BOSS INPUT REQUIRED'. No price, no guarantee, "
            "no dental/medical. Paid ads are GAP — $0 spend cap."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Delegation plan DRAFT বানানো। কোনো worker execute করে না, file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Manage Marketing"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

        # Gated action থাকলে আগে approval — অনুমোদন ছাড়া draft-ও নয়,
        # PENDING record করে থামা।
        if gated_action:
            gw = gateway if gateway is not None else self._gateway(approvals_path)
            approved = False
            if approval_id:
                try:
                    approved = gw.is_approved(approval_id)
                except KeyError:
                    approved = False
            if not approved:
                approval = self._request_approval(gw, gated_action, title)
                return {
                    "status": "pending-approval",
                    "approval": approval,
                    "draft_only": True,
                    "mock_brain": True,
                    "gate": self.gate,
                }

        task_kind = task.get("task_kind") or self.task_kind
        known_kinds = [self.task_kind] + sorted(DEPARTMENT_TASKS.keys())

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — delegation plan built from DEPARTMENT_TASKS only."

        if task_kind == self.task_kind:
            lines = [
                "[MOCK DRAFT] Marketing — department overview delegation plan (DRAFT ONLY)",
                "Manager: Marketing Director Agent | task_kind: manage_marketing | gate: ok",
                "Specialists (4 EXISTING):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                entry = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {entry['specialist']} | {entry['file']} | "
                    f"gate: {entry['gate'] or 'none'} | {entry['status']}"
                )
            lines.append(
                "Note: PublishPrep শুধু prep করে — কখনো post করে না; publish-এর "
                "gate 'post it'। Ad Campaign Agent GAP — paid ads $0 cap-এ নেই। "
                "Weekly reporting ReportCompiler-এর (Finance & Admin) আওতায়।"
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, কোনো "
                "worker execute নয়, কোনো post নয়। Agency Chief wiring Phase 2 DONE — "
                "Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।"
            )
            return {
                "status": "draft-ready",
                "output": "\n".join(lines),
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        entry = DEPARTMENT_TASKS.get(task_kind)
        if entry is None:
            output = (
                "[MOCK DRAFT] Marketing — unknown task (DRAFT ONLY)\n"
                f"Requested task_kind '{task_kind}' এই department-এ নেই।\n"
                "Known task kinds: " + ", ".join(known_kinds) + ".\n"
                "কোনো worker execute হয়নি; সঠিক task_kind দিয়ে আবার চাইতে হবে।"
            )
            notes = (
                "Unknown task — delegation plan বানানো হয়নি। এই department-এর "
                "task kind-গুলো উপরে তালিকায় আছে।"
            )
            return {
                "status": "unknown-task",
                "output": output,
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        payload = task.get("payload") or {}
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        output = (
            "[MOCK DRAFT] Marketing — delegation plan (DRAFT ONLY)\n"
            f"Task: {task_kind} | Topic: {topic}\n"
            f"Specialist: {entry['specialist']} | File/skill: {entry['file']}\n"
            f"Gate needed: {entry['gate'] or 'none'} | Status: {entry['status']}\n"
            "Plan (DRAFT):\n"
            f"1. {entry['specialist']}-কে task দেওয়া হবে — manager নিজে কাজটি করে না।\n"
            "2. Specialist-এর output DRAFT হিসেবে Boss-কে দেখানো হবে।\n"
        )
        if entry["gate"]:
            output += (
                f"3. Gate '{entry['gate']}' — Boss-এর exact word ছাড়া কিছু "
                "প্রকাশ/পাঠানো/খরচ করা যাবে না।\n"
            )
        if task_kind == "publish_prep":
            output += (
                "4. PublishPrep শুধু prep করে — কখনো post করে না; আসল posting "
                "Boss-এর 'post it' + হাতে করা।\n"
            )
        if entry["status"] == "ROLE-ONLY":
            output += (
                "4. ROLE-ONLY — এই role-এর কোনো worker code নেই; skill doc "
                "অনুযায়ী Boss/Elora হাতে কাজটি করবেন।\n"
            )
        if entry["status"] == "GAP":
            output += (
                "4. GAP — এই role-এর কোনো worker/skill নেই; paid ads $0 spend "
                "cap-এ planned নয়।\n"
            )
        output += (
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan মাত্র; worker "
            "execute হয়নি, কিছু post হয়নি। Agency Chief wiring Phase 2 DONE — "
            "Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
