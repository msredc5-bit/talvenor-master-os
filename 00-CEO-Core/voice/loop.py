"""Jarvis voice loop — শোনা -> brain -> বলা (REAL, offline, $0).

এক turn: Boss বলে -> listen() -> brain (BrainFactory, mock default) উত্তর
দেয় -> speak() বলে। Gated কাজ (send/publish) voice-এ execute হয় না —
ApprovalGateway-এ PENDING record লেখা হয়, Boss-এর gate word ছাড়া
আর এগোয় না।

Brain-এর উত্তর mock (draft) — voice Jarvis-কে বুদ্ধিমান বানায় না,
শুধু কথা বলা/শোনা চালু করে। এটা এই loop-এর সৎ সীমা।
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

# Voice-এ শোনা gate word -> gateway action।
# শুধু send/publish — upload/spend/delete voice-এ request করা যায় না
# (Boss টাইপ করে দেবে); "ok"/"go" কথায় এত common যে voice-এ gate
# হিসেবে ধরা হয় না (ভুল trigger এড়াতে)।
GATE_PHRASES = {
    "send": "send",
    "পাঠাও": "send",
    "post it": "publish",
    "post all": "publish",
}

LISTENING_BN = "শুনছি, বলুন।"
LISTENING_EN = "Listening, go ahead."
NOT_HEARD_BN = "শুনতে পাইনি, আবার বলুন।"
NOT_HEARD_EN = "I did not hear anything, please say it again."
GATED_BN = "অনুমোদনের জন্য পাঠিয়েছি — Boss-এর কথায় এগোবে, voice-এ নয়।"
GATED_EN = "Sent for approval — it will only move on Boss's word, not by voice."


def detect_gated_action(heard_text):
    """শোনা কথায় gate word থাকলে action ("send"/"publish") ফেরত দেয়।

    না থাকলে None। English case-insensitive; Bengali substring match।
    """
    if not heard_text:
        return None
    low = heard_text.lower()
    for phrase, action in GATE_PHRASES.items():
        if phrase in low or phrase in heard_text:
            return action
    return None


def handle_voice_text(heard_text, lang="bn", brain_department="agency",
                      approvals_path=None, voice_dir=None):
    """একটা শোনা বাক্য -> brain উত্তর -> voice। Mic লাগে না (test-যোগ্য)।

    ফেরত: {"heard", "reply", "gated_action", "approval_id", "spoke_path"}।
    gated_action থাকলে reply-র বদলে gate-এর কথা বলা হয়, আর
    ApprovalGateway-এ PENDING লেখা হয় — execute কিছুই হয় না।
    """
    lang = (lang or "bn").lower()
    heard = (heard_text or "").strip()
    if not heard:
        reply = NOT_HEARD_BN if lang == "bn" else NOT_HEARD_EN
        return {"heard": heard, "reply": reply,
                "gated_action": None, "approval_id": None,
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
                "spoke_path": speak(reply, lang=lang, play=False,
                                    voice_dir=voice_dir)}

    brain = BrainFactory.get_brain(brain_department)
    reply = brain.complete(heard)
    if not reply or not str(reply).strip():
        reply = NOT_HEARD_BN if lang == "bn" else NOT_HEARD_EN
    return {"heard": heard, "reply": str(reply),
            "gated_action": None, "approval_id": None,
            "spoke_path": speak(str(reply), lang=lang, play=False,
                                voice_dir=voice_dir)}


def run_voice_loop(lang="bn", seconds=8, max_turns=None,
                   brain_department="agency", approvals_path=None,
                   voice_dir=None):
    """Jarvis voice loop — Ctrl+C-তে থামে। ফেরত: কয় turn হলো।

    approvals_path=None মানে আসল store/approvals.json (Boss-এর PC-তে
    এটাই ঠিক — PENDING record dashboard-এ দেখা যাবে)। Test-এ TEMP
    path দিতে হবে, আসল store ছোঁয়া যাবে না।
    """
    lang = (lang or "bn").lower()
    print(f"[Jarvis] Voice loop শুরু — ভাষা: {lang} | "
          f"brain: {BrainFactory.get_brain_mode()} (mock default, $0) | "
          f"থামাতে Ctrl+C")
    print("[Jarvis] Gated কাজ (send/publish) voice-এ শুধু PENDING হয়, "
          "execute হয় না।")
    turns = 0
    try:
        while max_turns is None or turns < max_turns:
            print(f"\n--- Turn {turns + 1} ---")
            print(LISTENING_BN if lang == "bn" else LISTENING_EN)
            try:
                heard = listen(seconds=seconds, lang=lang)
            except RuntimeError as exc:
                print(f"[Jarvis] শোনা গেল না: {exc}")
                break
            print(f"[Boss] {heard!r}")
            result = handle_voice_text(
                heard, lang=lang, brain_department=brain_department,
                approvals_path=approvals_path, voice_dir=voice_dir)
            print(f"[Jarvis] {result['reply']}")
            if result["gated_action"]:
                print(f"[Jarvis] Gate: {result['gated_action']} -> "
                      f"PENDING (approval id {result['approval_id']})")
            speak(result["reply"], lang=lang, play=True,
                  voice_dir=voice_dir)
            turns += 1
    except KeyboardInterrupt:
        print("\n[Jarvis] Loop থামল (Ctrl+C)।")
    print(f"[Jarvis] মোট turn: {turns}")
    return turns


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Jarvis voice loop — শোনা -> brain -> বলা (offline, $0)")
    parser.add_argument("--lang", default="bn", choices=["bn", "en"])
    parser.add_argument("--seconds", type=int, default=8)
    parser.add_argument("--turns", type=int, default=None)
    parser.add_argument("--business", default="agency")
    args = parser.parse_args()
    run_voice_loop(lang=args.lang, seconds=args.seconds,
                   max_turns=args.turns, brain_department=args.business)
