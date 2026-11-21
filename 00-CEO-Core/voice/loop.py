"""Jarvis voice loop — listen -> brain -> speak (REAL, offline, $0).

One turn: Boss speaks -> listen() -> the brain (BrainFactory, mock default)
answers -> speak() says it. Gated work (send/publish) never executes by voice —
a PENDING record is written to the ApprovalGateway and it goes no further
without Boss's gate word.

Task-like speech ("task: ..." or "find skill ...") does not go to the brain —
it goes to the Main CEO Bot's route_task() (2026-11-21): it is routed to a Chief
/ a skill is searched, and a short answer is spoken. If routing fails,
it falls back to the brain — the voice never stops. Free-form speech stays in
brain.complete() as before.

The brain's answer is a mock (draft) — voice does not make Jarvis intelligent,
it only turns speaking/listening on. That is this loop's honest limit.
"""

import os
import sys

CEO_CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CEO_CORE_DIR not in sys.path:
    sys.path.insert(0, CEO_CORE_DIR)

from brain import BrainFactory  # noqa: E402
from human_approval_gateway import ApprovalGateway  # noqa: E402
from voice.listen import listen  # noqa: E402
from voice.speak import speak  # noqa: E402

# A gate word heard by voice -> gateway action.
# Only send/publish — upload/spend/delete cannot be requested by voice
# (Boss types those); "ok"/"go" are so common in speech that they are not
# treated as gates by voice (to avoid false triggers).
GATE_PHRASES = {
    "send": "send",
    "পাঠাও": "send",
    "post it": "publish",
    "post all": "publish",
}

# Task-like heard speech -> route_task() (not a brain bypass).
TASK_PREFIXES = ("task:",)
FIND_SKILL_PREFIXES = ("find skill",)


def _detect_task_route(heard_text):
    """Whether the heard speech is task-like — if so, route_task()'s task dict,
    otherwise None.

    - "find skill <query>" -> find_skill route
      (no business needed, does not go to a Chief, writes nothing).
    - "task: <title>" -> agency prospect_research
      task (a Chief research task; logged in tasks.json).
    """
    heard = (heard_text or "").strip()
    low = heard.lower()
    for prefix in FIND_SKILL_PREFIXES:
        if low.startswith(prefix):
            query = heard[len(prefix):].strip(" :—-").strip()
            return {"type": "find_skill", "query": query,
                    "title": f"find skill: {query}"}
    for prefix in TASK_PREFIXES:
        if low.startswith(prefix):
            title = heard[len(prefix):].strip()
            if title:
                return {"business": "agency", "type": "prospect_research",
                        "title": title}
    return None


def _route_summary(routed, lang="bn"):
    """route_task()'s result -> a one-line summary fit to speak."""
    routed_to = routed.get("routed_to", "?")
    status = routed.get("status", "?")
    if routed.get("status") == "skill-search":
        matches = routed.get("local_matches") or []
        query = (routed.get("title") or "").replace("find skill:", "").strip()
        if lang == "bn":
            if matches:
                names = ", ".join(m.get("name", "?") for m in matches[:3])
                return (f"Found {len(matches)} local skill(s) for "
                        f"'{query}': {names}.")
            return f"No local skill found for '{query}'."
        if matches:
            names = ", ".join(m.get("name", "?") for m in matches[:3])
            return (f"Found {len(matches)} local skill(s) for "
                    f"'{query}': {names}.")
        return f"No local skill found for '{query}'."
    if lang == "bn":
        return f"Task routed — {routed_to}: {status}."
    return f"Task routed — {routed_to}: {status}."

LISTENING_BN = "Listening, go ahead."
LISTENING_EN = "Listening, go ahead."
NOT_HEARD_BN = "I did not hear anything, please say it again."
NOT_HEARD_EN = "I did not hear anything, please say it again."
GATED_BN = "Sent for approval — it will only move on Boss's word, not by voice."
GATED_EN = "Sent for approval — it will only move on Boss's word, not by voice."


def detect_gated_action(heard_text):
    """If the heard speech contains a gate word, return the action ("send"/"publish").

    None if not. English is case-insensitive; Bengali is a substring match.
    """
    if not heard_text:
        return None
    low = heard_text.lower()
    for phrase, action in GATE_PHRASES.items():
        if phrase in low or phrase in heard_text:
            return action
    return None


def handle_voice_text(heard_text, lang="bn", brain_department="agency",
                      approvals_path=None, voice_dir=None, tasks_path=None):
    """One heard sentence -> brain answer -> voice. No mic needed (testable).

    Returns: {"heard", "reply", "gated_action", "approval_id",
    "spoke_path", "routed_via", "route_result"}. If there is a gated_action,
    the gate's words are spoken instead of the reply, and a PENDING record
    is written to the ApprovalGateway — nothing executes. Task-like speech goes
    to route_task() (routed_via "main_ceo_bot"); free-form speech goes to the brain
    (routed_via "brain"). tasks_path=None means the real store/tasks.json —
    tests must pass a TEMP path.
    """
    lang = (lang or "bn").lower()
    heard = (heard_text or "").strip()
    if not heard:
        reply = NOT_HEARD_BN if lang == "bn" else NOT_HEARD_EN
        return {"heard": heard, "reply": reply,
                "gated_action": None, "approval_id": None,
                "routed_via": None, "route_result": None,
                "spoke_path": speak(reply, lang=lang, play=False,
                                    voice_dir=voice_dir)}

    action = detect_gated_action(heard)
    if action is not None:
        gateway = ApprovalGateway(approvals_path=approvals_path)
        req = gateway.request(
            action,
            f"Voice command (Jarvis): {heard}",
            "Jarvis voice loop",
        )
        reply = GATED_BN if lang == "bn" else GATED_EN
        return {"heard": heard, "reply": reply,
                "gated_action": action, "approval_id": req["id"],
                "routed_via": None, "route_result": None,
                "spoke_path": speak(reply, lang=lang, play=False,
                                    voice_dir=voice_dir)}

    # Task-like speech -> Main CEO Bot's route_task() (Chief / skill-finder).
    # If routing fails, fall back to the brain below — the voice never stops. The try
    # only wraps the route (not speak — if speak fails, that is a real error).
    task = _detect_task_route(heard)
    if task is not None:
        routed = None
        try:
            import main_ceo_bot  # noqa: PLC0415 — lazy: only needed for tasks
            routed = main_ceo_bot.route_task(
                task, tasks_path=tasks_path, approvals_path=approvals_path)
        except Exception as exc:  # noqa: BLE001 — route fail = brain fallback
            print(f"[Jarvis] route_task failed ({type(exc).__name__}: "
                  f"{exc}) — falling back to brain.", file=sys.stderr)
        if routed is not None:
            reply = _route_summary(routed, lang=lang)
            return {"heard": heard, "reply": reply,
                    "gated_action": None, "approval_id": None,
                    "routed_via": "main_ceo_bot", "route_result": routed,
                    "spoke_path": speak(reply, lang=lang, play=False,
                                        voice_dir=voice_dir)}

    brain = BrainFactory.get_brain(brain_department)
    reply = brain.complete(heard)
    if not reply or not str(reply).strip():
        reply = NOT_HEARD_BN if lang == "bn" else NOT_HEARD_EN
    return {"heard": heard, "reply": str(reply),
            "gated_action": None, "approval_id": None,
            "routed_via": "brain", "route_result": None,
            "spoke_path": speak(str(reply), lang=lang, play=False,
                                voice_dir=voice_dir)}


def run_voice_loop(lang="bn", seconds=8, max_turns=None,
                   brain_department="agency", approvals_path=None,
                   voice_dir=None, tasks_path=None):
    """Jarvis voice loop — stops on Ctrl+C. Returns: how many turns ran.

    approvals_path=None means the real store/approvals.json (on Boss's PC that
    is right — the PENDING record will show on the dashboard). Tests must pass a
    TEMP path; the real store must not be touched.
    """
    lang = (lang or "bn").lower()
    print(f"[Jarvis] Voice loop started — language: {lang} | "
          f"brain: {BrainFactory.get_brain_mode()} (mock default, $0) | "
          f"stop with Ctrl+C")
    print("[Jarvis] Gated work (send/publish) only becomes PENDING by voice, "
          "it never executes.")
    turns = 0
    try:
        while max_turns is None or turns < max_turns:
            print(f"\n--- Turn {turns + 1} ---")
            print(LISTENING_BN if lang == "bn" else LISTENING_EN)
            try:
                heard = listen(seconds=seconds, lang=lang)
            except RuntimeError as exc:
                print(f"[Jarvis] could not hear: {exc}")
                break
            print(f"[Boss] {heard!r}")
            result = handle_voice_text(
                heard, lang=lang, brain_department=brain_department,
                approvals_path=approvals_path, voice_dir=voice_dir,
                tasks_path=tasks_path)
            print(f"[Jarvis] {result['reply']}")
            if result["gated_action"]:
                print(f"[Jarvis] Gate: {result['gated_action']} -> "
                      f"PENDING (approval id {result['approval_id']})")
            speak(result["reply"], lang=lang, play=True,
                  voice_dir=voice_dir)
            turns += 1
    except KeyboardInterrupt:
        print("\n[Jarvis] Loop stopped (Ctrl+C).")
    print(f"[Jarvis] total turns: {turns}")
    return turns


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Jarvis voice loop — listen -> brain -> speak (offline, $0)")
    parser.add_argument("--lang", default="bn", choices=["bn", "en"])
    parser.add_argument("--seconds", type=int, default=8)
    parser.add_argument("--turns", type=int, default=None)
    parser.add_argument("--business", default="agency")
    args = parser.parse_args()
    run_voice_loop(lang=args.lang, seconds=args.seconds,
                   max_turns=args.turns, brain_department=args.business)
