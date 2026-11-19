"""Analytics Agent — analytics/report draft, visible metrics only (Dept 02 Marketing).

ভূমিকা (role): Talvenor marketing-এর analytics/report-এর DRAFT লেখা — শুধু
VISIBLE metric দিয়ে। যা দেখা যায় তাই; কখনো estimate করে না, সংখ্যা বানায় না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

আসল metric না থাকলে metric 0 — "No visible metrics yet — metrics 0 until
real data exists." Weekly মূল report ReportCompiler-এর (Finance & Admin);
এই agent শুধু marketing-এর draft দেয়।

এই agent কখনো করে না: metric estimate/bানানো নয়, কিছু publish/পাঠানো নয়,
দাম quote করে না, কোনো guarantee দেয় না, client-এর তথ্য/পরিসংখ্যান বানায়
না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class AnalyticsAgent:
    """Analytics/report draft ONLY — visible metrics only, never estimates।"""

    task_kind = "analytics"
    gate = None
    department = "02-marketing"
    role = "Analytics Agent"

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
        period = payload.get("period") or "BOSS INPUT REQUIRED"
        return (
            "Analytics/report draft for Talvenor marketing. "
            f"Period: {period}. "
            "Use ONLY the visible metrics in the task payload. If no metrics "
            "are given, every metric is 0 — never estimate or invent numbers. "
            "List what was posted (payload only), best/worst only where a "
            "visible number exists, and next-week suggestions. No invented "
            "client facts, prices, or statistics. No guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Analytics/report DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Analytics report draft"
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
        period = payload.get("period") or "BOSS INPUT REQUIRED"
        posted = payload.get("posted") or []
        metrics = payload.get("metrics") or {}

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — analytics built from payload only."

        if posted:
            posted_lines = "\n".join(f"- {item}" for item in posted)
        else:
            posted_lines = "- BOSS INPUT REQUIRED — what was posted is not in the payload."
        if metrics:
            metric_lines = "\n".join(
                f"- {key}: {value} (visible metric, from payload)"
                for key, value in sorted(metrics.items())
            )
            best_line = (
                "Best/worst: only where a visible number exists above — "
                "no ranking claimed beyond the visible numbers."
            )
        else:
            metric_lines = (
                "- No visible metrics yet — metrics 0 until real data exists."
            )
            best_line = (
                "Best/worst: cannot tell yet — no visible metrics in the payload."
            )

        output = (
            "[MOCK DRAFT] Analytics report — DRAFT ONLY, VISIBLE METRICS ONLY\n"
            f"Period: {period}\n"
            "Posted (payload only):\n"
            f"{posted_lines}\n"
            "Visible metrics:\n"
            f"{metric_lines}\n"
            f"{best_line}\n"
            "Next week: keep posting what Boss approved; re-check only with "
            "visible numbers Boss pastes — never estimate.\n"
            "Note: weekly main report is ReportCompiler's (Finance & Admin); "
            "this is a marketing draft only.\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Analytics draft ONLY, visible "
            "metrics only — কখনো estimate/invent নয়, metric না থাকলে 0। "
            "কোনো invented client, price, statistic, guarantee নেই। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
