"""Social Media Agent — social content planning draft ONLY (Dept 02 Marketing).

ভূমিকা (role): Facebook, Instagram, LinkedIn-এর জন্য content planning-এর
DRAFT লেখা — post idea, hook, caption outline। কখনো post/publish করে না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

Posting Boss main chat থেকে নিজে করেন ("post it" gate); publish-এর prep
PublishPrep-এর কাজ। এই agent comment-এ pitch করে না, group-এ post করে না।

এই agent কখনো করে না: কিছু post/publish করে না, দাম quote করে না, কোনো
guarantee দেয় না, client-এর তথ্য/পরিসংখ্যান বানায় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class SocialMediaAgent:
    """Social content planning draft ONLY — NEVER posts/publishes।"""

    task_kind = "social_manage"
    gate = None
    department = "02-marketing"
    role = "Social Media Agent"

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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        platform = payload.get("platform") or "BOSS INPUT REQUIRED"
        return (
            "Social content planning draft for Talvenor (AI receptionist "
            "for US home-service owners). "
            f"Topic: {topic}. Platform: {platform}. "
            "One idea adapted to Facebook, Instagram, LinkedIn — hook first, "
            "caption outline, format, hashtag counts (IG 5-8 / LinkedIn 3 / "
            "Facebook 0-2), one CTA (15-min demo call). Planning ONLY — "
            "never post. No invented client facts or prices; mark missing "
            "facts 'BOSS INPUT REQUIRED'. No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Social planning DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Social content plan draft"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

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

        payload = task.get("payload") or {}
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        platform = payload.get("platform") or "Facebook + Instagram + LinkedIn"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — social plan built from payload only."

        output = (
            "[MOCK DRAFT] Social content plan — DRAFT ONLY, NEVER POSTS\n"
            f"Topic: {topic} | Platform focus: {platform}\n"
            "One idea, three platforms (same idea adapted — not three ideas):\n"
            "Facebook: short post, one clear image/video, plain language, "
            "one CTA. Hashtags 0-2.\n"
            "Instagram: Reel (15-30 sec, hook in first 2 seconds, captions "
            "on screen) or carousel (5-8 slides, one idea per slide); "
            "caption first line is the hook. Hashtags 5-8.\n"
            "LinkedIn: professional, text-led, founder voice, one image or "
            "short video. Hashtags 3.\n"
            "Hook draft: \"Missed call = lost job. Our AI receptionist "
            "answers 24/7.\"\n"
            "CTA draft: \"Book a 15-min call: "
            f"{BOOKING_LINK}\" (Facebook: \"Message us or book a call. "
            "Link in comments.\")\n"
            "Posting: this agent NEVER posts — PublishPrep only preps; "
            "Boss posts himself from main chat after 'post it'.\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Social planning draft ONLY, "
            "কখনো post/publish নয়। একই idea তিন platform-এ adapt করা। "
            "কোনো invented client, price, statistic, guarantee নেই। "
            "Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
