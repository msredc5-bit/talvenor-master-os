"""Marketing Director Agent — manager of the Marketing department (Phase 1).

Role: delegate to the 9 existing specialists of the Marketing department —
content plan, video produce, caption write, publish prep, market
position, social manage, seo, analytics. This manager only makes a DRAFT of the delegation plan;
it loads the new 5 standalone specialists (Phase 3 + 2026-11-21) with importlib and
returns their drafts — it posts nothing itself.
Gate: ok — the delegation plan needs Boss's "ok"; the publish gate is "post it",
send/spend/delete This manager itself performs no gated action.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
Agency Chief wiring Phase 2 DONE — the Chief now calls this manager via DEPARTMENT_ROUTING.
This manager never: executes the engine/section's old workers, posts/publishes anything,
runs paid ads, spends anything, deletes anything, invents client facts/prices/
statistics, gives any guarantee, takes dental/medical or
patient-health businesses.
"""

import importlib.util
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
        "class": "MarketPositioningAgent",
        "file": "departments/02-marketing/specialists/market_positioning_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "social_manage": {
        "specialist": "Social Media Agent",
        "class": "SocialMediaAgent",
        "file": "departments/02-marketing/specialists/social_media_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "ad_campaign": {
        "specialist": "Ad Campaign Agent",
        "class": "AdCampaignAgent",
        "file": "departments/02-marketing/specialists/ad_campaign_agent.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "seo": {
        "specialist": "SEO Agent",
        "class": "SEOAgent",
        "file": "departments/02-marketing/specialists/seo_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "analytics": {
        "specialist": "Analytics Agent",
        "class": "AnalyticsAgent",
        "file": "departments/02-marketing/specialists/analytics_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
}


class MarketingDirectorAgent:
    """Makes a DRAFT of the delegation plan for marketing specialists + loads and runs the Phase 3 specialists (DRAFT only); does not post."""

    task_kind = "manage_marketing"
    gate = "ok"
    department = "02-marketing"
    role = "Marketing Director Agent"

    def _gateway(self, approvals_path=None):
        """ApprovalGateway lazy-load — no repo import at top level."""
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
        """Record a PENDING approval — not execute, not auto-approve."""
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
            "no dental/medical. Paid ads: DRAFT plan only — $0 spend cap, no live ads."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Build a delegation plan DRAFT + Phase 3 specialist load+run (DRAFT only). Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Manage Marketing"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

        # If there is a gated action, approval first — no draft without approval,
        # record PENDING and stop.
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
                "Specialists (9 EXISTING):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                entry = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {entry['specialist']} | {entry['file']} | "
                    f"gate: {entry['gate'] or 'none'} | {entry['status']}"
                )
            lines.append(
                "Note: PublishPrep only does prep — it never posts; the publish "
                "gate is 'post it'. Ad Campaign Agent EXISTING — DRAFT plan only; paid ads $0 cap, no live ad. "
                "Weekly reporting is under ReportCompiler (Finance & Admin)."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, no "
                "not a worker execution, no post. Agency Chief wiring Phase 2 DONE — "
                "The Chief now calls this manager via DEPARTMENT_ROUTING."
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
                f"Requested task_kind '{task_kind}' is not in this department.\n"
                "Known task kinds: " + ", ".join(known_kinds) + ".\n"
                "No worker executed; ask again with the correct task_kind."
            )
            notes = (
                "Unknown task — no delegation plan was made. This department's "
                "task kinds are listed above."
            )
            return {
                "status": "unknown-task",
                "output": output,
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        # Phase 3 standalone specialists — departments/02-marketing/specialists/
        # If it has a .py, load it with importlib like the Chief's loader and
        # run the specialist; its result is returned. Existing engine
        # workers' (content_plan / video_produce / caption_write /
        # publish_prep) plan-draft behaviour stays unchanged below.
        if entry.get("status") == "EXISTING" and entry.get("class"):
            specialist_path = os.path.normpath(os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..",
                "specialists", os.path.basename(entry["file"])))
            spec = importlib.util.spec_from_file_location(
                f"marketing_specialist_{task_kind}", specialist_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            specialist_cls = getattr(mod, entry["class"])
            specialist = specialist_cls()
            return specialist.run(task, brain, gateway, approvals_path)

        payload = task.get("payload") or {}
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        output = (
            "[MOCK DRAFT] Marketing — delegation plan (DRAFT ONLY)\n"
            f"Task: {task_kind} | Topic: {topic}\n"
            f"Specialist: {entry['specialist']} | File/skill: {entry['file']}\n"
            f"Gate needed: {entry['gate'] or 'none'} | Status: {entry['status']}\n"
            "Plan (DRAFT):\n"
            f"1. {entry['specialist']} will be given the task — the manager does not do the work itself.\n"
            "2. The specialist's output will be shown to Boss as a DRAFT.\n"
        )
        if entry["gate"]:
            output += (
                f"3. Gate '{entry['gate']}' — nothing without Boss's exact word "
                "must not be published/sent/spent.\n"
            )
        if task_kind == "publish_prep":
            output += (
                "4. PublishPrep only does prep — it never posts; the real posting "
                "is done by Boss with 'post it' + by hand.\n"
            )
        if entry["status"] == "ROLE-ONLY":
            output += (
                "4. ROLE-ONLY — this role has no worker code; the skill doc "
                "says Boss/Elora will do the work by hand.\n"
            )
        if entry["status"] == "GAP":
            output += (
                "4. GAP — (worker + skill EXISTING on 2026-11-21) — Ad Campaign "
                "Agent: departments/02-marketing/specialists/ad_campaign_agent.py; "
                "paid ads are still DRAFT plan only, no live ad under the $0 spend cap.\n"
            )
        output += (
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan only; the worker "
            "was not executed, nothing was posted. Agency Chief wiring Phase 2 DONE — "
            "The Chief now calls this manager via DEPARTMENT_ROUTING."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
