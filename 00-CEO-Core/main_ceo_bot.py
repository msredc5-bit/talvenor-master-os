"""Main CEO Bot — thin brain / router (Phase 0, REAL skeleton).

কাজ: Boss-এর (বা Jarvis-এর) দেওয়া task-টা পড়ে ঠিক Chief of Staff-এর
দিকে পাঠানো, আর gated কাজ হলে ApprovalGateway দিয়ে আটকে রাখা।

এই ফাইল ইঞ্জিন নয় — আসল worker engine এখন এই repo-র ভেতরে
vendored (01-Agency-Department/engine/workers/, 15 worker;
03-Content-Creation-Department/engine/workers/, 6 Creator OS
worker)। বাইরের checkout (~/workspace/boss-ceo, ~/workspace/
creator-os-combined) আর runtime dependency নয় — শুধু canonical
upstream। Phase 1 থেকে Agency Chief engine-কে import করে ডাকে।

Memory wiring (2026-11-21, MEMORY-STRUCTURE-DECISION-2026-11-21.md):
  - route_task() প্রত্যেক route-এ memory পড়ে — context_for("main_ceo_bot")
    result-এ "memory" হিসেবে attach হয় (shared Boss-কথা + নিজের box)।
  - Boss-এর নতুন কথা record_owner_message() দিয়ে শেখানো হয় — quote
    verbatim না থাকলে ValueError (memory শুধু Boss-এর কথা থেকে শেখে)।
  - ভুলে যাওয়া শুধু gate-এ: request_forget_owner_entry() ConfirmationStore-এ
    "delete" confirmation বানায় (gate word "go"); forget_owner_entry()
    শুধু approved confirmation-ই execute_once() দিয়ে চালায়।
  - Route-এর note memory-তে লেখা হয় না — routing-এর log store/tasks.json-এ
    থাকে; memory Boss-এর কথা + lesson-এর জন্য (per-task note test-এ
    ৫৭৩ entry বানিয়ে check_phase6 ভেঙেছিল, তাই সরানো হয়েছে)।
  - Brain এখনো mock, $0, কোনো key / live call নেই।

Jarvis (voice) আর Main CEO Bot (brain) আলাদা module — jarvis_voice.py
দেখুন। Gemini-র map-এ ওরা একসাথে মিশে গিয়েছিল, সেটা এখানে ঠিক করা
হয়েছে।
"""

import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from human_approval_gateway import ApprovalGateway, GATED_ACTIONS  # noqa: E402
from owner_memory import OwnerMemory  # noqa: E402
from trust_gate import ConfirmationStore  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "00-CEO-Core", "config.json")

# business key -> Chief of Staff module (Phase 0: stub module-গুলো)
CHIEF_MODULES = {
    "agency": "01-Agency-Department.chief_of_staff_agency",
    "digital-product": "02-Digital-Product-Department.chief_of_staff_products",
    "content": "03-Content-Creation-Department.chief_of_staff_content",
}


def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_memory(memory_path=None):
    """Owner memory load করা — memory_path না দিলে আসল store/memory.json।"""
    return OwnerMemory(memory_path=memory_path) if memory_path else OwnerMemory()


def record_owner_message(source_message, area, slug, text, quote,
                         source_ref="", memory_path=None):
    """Boss-এর নতুন কথা memory-তে শেখানো — write path। Quote verbatim
    না থাকলে ValueError (learn() যাচাই করে)। এটা শুধু Boss-এর message
    থেকে ডাকা হয় — tool result / web page / email থেকে নয়।"""
    mem = load_memory(memory_path)
    return mem.learn(area, slug, text, quote, source_message,
                     source_ref=source_ref)


def request_forget_owner_entry(area, slug, requested_by="Boss",
                               memory_path=None, confirmations_path=None,
                               approvals_path=None):
    """Owner entry ভুলে যাওয়ার অনুমোদন চাওয়া — Nod: forgetting-এ
    trust check লাগে। ConfirmationStore-এ "delete" confirmation বানায়
    (gate word "go"); entry এখনো মোছা হয়নি — শুধু asked।"""
    mem = load_memory(memory_path)
    mem.get(area, slug)  # না থাকলে KeyError — ভুল entry-তে request নয়
    store = ConfirmationStore(confirmations_path=confirmations_path,
                              approvals_path=approvals_path)
    return store.create(
        "delete",
        {"area": area, "slug": slug},
        f"Forget owner memory {area}/{slug}?",
        requested_by=requested_by,
    )


def forget_owner_entry(area, slug, confirmation_id, memory_path=None,
                       confirmations_path=None, approvals_path=None):
    """Approved confirmation-ই execute করে — একবারই। Approve ছাড়া
    execute করলে ValueError; fail হলে UNCERTAIN, কখনো re-run নয়।"""
    store = ConfirmationStore(confirmations_path=confirmations_path,
                              approvals_path=approvals_path)

    def _runner(args):
        mem = load_memory(memory_path)
        forgotten = mem.forget(args["area"], args["slug"])
        return f"forgot {args['area']}/{args['slug']}: {forgotten['text'][:80]}"

    return store.execute_once(confirmation_id, _runner)


def route_task(task, tasks_path=None, approvals_path=None, memory_path=None):
    """task = {"business": "agency"|"digital-product"|"content", "title": ..., "detail": ...}

    Agency হলে আসল Chief of Staff (Phase 1) কাজ করে — task type
    অনুযায়ী real boss-ceo worker-এর দিকে যায়, gated কাজ approval-এ
    আটকায়। Digital Product হলে আসল Products Chief (Phase 2) কাজ করে —
    kit শুধু blueprint, launch/sale Gate 0-তে আটকায়। Content হলে আসল
    Content Chief (Phase 3) কাজ করে — Creator OS-র ৬ worker ডাকে, draft
    বানায়, publish/upload gate-এ আটকায়, video file বানায় না।
    Gated action থাকলে task এগোয় না — approval request pending থাকে।
    """
    config = load_config()

    if task.get("type") == "find_skill":
        # Skill-finder (CEO Bot capability, 2026-11-21): local search
        # first, then a DRAFT proposal — never installs, never writes
        # a skill file. Business-agnostic: Chief-এ যায় না।
        import skill_finder  # noqa: PLC0415

        query = task.get("query", "")
        local = skill_finder.find_skill_local(query)
        proposal = None
        if task.get("propose") and task.get("candidate_repo"):
            proposal = skill_finder.propose_skill(
                query, task.get("agent", ""),
                task["candidate_repo"], task.get("candidate_skill", ""),
                task.get("source_url", ""), task.get("license", ""),
                task.get("fit_note", ""), why=task.get("detail", ""),
                proposals_path=task.get("proposals_path"),
            )
        return {
            "routed_to": "00-CEO-Core.skill_finder",
            "business": task.get("business"),
            "title": task.get("title", f"find skill: {query}"),
            "status": "skill-search",
            "local_matches": local,
            "proposal": proposal,
            "spend_cap_usd": config["spend_cap_usd"],
        }

    business = task.get("business")
    if business not in CHIEF_MODULES:
        raise ValueError(f"Unknown business: {business!r}. Known: {list(CHIEF_MODULES)}")

    # Memory read path — প্রত্যেক route-এ Boss-এর কথা পড়া হয়।
    mem = load_memory(memory_path)
    memory_ctx = mem.context_for("main_ceo_bot")

    if business == "agency":
        # Lazy import — Chief-এর engine import শুধু agency task-এ লাগে।
        chief_path = os.path.join(BASE_DIR, "01-Agency-Department")
        if chief_path not in sys.path:
            sys.path.insert(0, chief_path)
        import chief_of_staff_agency  # noqa: PLC0415

        chief_result = chief_of_staff_agency.handle_task(
            task, tasks_path=tasks_path, approvals_path=approvals_path,
            memory_path=memory_path,
        )
        result = {
            "routed_to": CHIEF_MODULES[business],
            "business": business,
            "title": task.get("title"),
            "status": chief_result["status"],
            "chief_result": chief_result,
            "approval": chief_result.get("approval"),
            "spend_cap_usd": config["spend_cap_usd"],
            "memory": memory_ctx,
        }
        return result

    if business == "digital-product":
        # Phase 2: Products Chief REAL — Gate 0 না পাস হওয়া পর্যন্ত
        # launch/sale আটকায়, kit শুধু blueprint হিসেবে আসে।
        chief_path = os.path.join(BASE_DIR, "02-Digital-Product-Department")
        if chief_path not in sys.path:
            sys.path.insert(0, chief_path)
        import chief_of_staff_products  # noqa: PLC0415

        chief_result = chief_of_staff_products.handle_task(
            task, tasks_path=tasks_path, approvals_path=approvals_path
        )
        result = {
            "routed_to": CHIEF_MODULES[business],
            "business": business,
            "title": task.get("title"),
            "status": chief_result["status"],
            "chief_result": chief_result,
            "approval": chief_result.get("approval"),
            "spend_cap_usd": config["spend_cap_usd"],
            "memory": memory_ctx,
        }
        return result

    if business == "content":
        # Phase 3: Content Chief REAL — Creator OS-র ৬ worker ডাকে
        # (mock brain, $0), draft বানায়, publish/upload gate-এ আটকায়।
        # video file বানায় না, upload script চালায় না।
        chief_path = os.path.join(BASE_DIR, "03-Content-Creation-Department")
        if chief_path not in sys.path:
            sys.path.insert(0, chief_path)
        import chief_of_staff_content  # noqa: PLC0415

        chief_result = chief_of_staff_content.handle_task(
            task, tasks_path=tasks_path, approvals_path=approvals_path
        )
        result = {
            "routed_to": CHIEF_MODULES[business],
            "business": business,
            "title": task.get("title"),
            "status": chief_result["status"],
            "chief_result": chief_result,
            "approval": chief_result.get("approval"),
            "spend_cap_usd": config["spend_cap_usd"],
            "memory": memory_ctx,
        }
        return result

    approval = None
    action = task.get("gated_action")
    if action:
        if action not in GATED_ACTIONS:
            raise ValueError(f"Unknown gated action: {action!r}")
        gateway = ApprovalGateway()
        approval = gateway.request(action, task.get("detail", task.get("title", "")), task.get("requested_by", "Main CEO Bot"))
        # NOTE: এখানেই থেমে যায়। approve() শুধু Boss-এর gate word-এ চলে।

    return {
        "routed_to": CHIEF_MODULES[business],
        "business": business,
        "title": task.get("title"),
        "status": "routed-pending-approval" if approval else "routed-stub",
        "note": "Phase 3: Agency + Digital Product + Content Chiefs are REAL. Only Jarvis voice stays a STUB.",
        "approval": approval,
        "spend_cap_usd": config["spend_cap_usd"],
        "memory": memory_ctx,
    }


if __name__ == "__main__":
    # হাতে চেক: শুধু non-gated routing। TEMP paths ব্যবহার করা হয়,
    # যাতে আসল store/tasks.json-এ test record না জমে। Memory-ও TEMP —
    # আসল store/memory.json ছোঁয়া হয় না।
    import tempfile  # noqa: PLC0415

    _tmp_dir = tempfile.mkdtemp()
    _tmp_tasks = os.path.join(_tmp_dir, "tasks-test.json")
    _tmp_appr = os.path.join(_tmp_dir, "approvals-test.json")
    _tmp_mem = os.path.join(_tmp_dir, "memory-test.json")
    _tmp_conf = os.path.join(_tmp_dir, "confirmations-test.json")

    # TEMP memory seed করা (আসল store থেকে নয় — file খালি থেকে seed)।
    _mem = load_memory(_tmp_mem)
    _seeded = _mem.seed_defaults()
    assert len(_seeded) == 3, _seeded

    r1 = route_task({"business": "agency", "title": "test route"},
                    tasks_path=_tmp_tasks, approvals_path=_tmp_appr,
                    memory_path=_tmp_mem)
    assert r1["routed_to"].endswith("chief_of_staff_agency")
    assert r1["status"] == "route-only"  # Phase 1: type ছাড়া task = probe only
    assert r1["chief_result"]["department"] == "agency"
    # Memory wiring: result-এ Boss-এর ৩ কথা; route memory-তে লেখে না
    # (routing log tasks.json-এ) — তাই TEMP store-এ note নেই।
    assert r1["memory"]["counts"]["shared"] == 3, r1["memory"]
    assert {e["slug"] for e in r1["memory"]["shared"]} == {
        "assistant-name", "reply-language", "gate-words"}
    _mem2 = load_memory(_tmp_mem)
    assert _mem2.list_own("main_ceo_bot") == []
    assert _mem2.list_own("chief_of_staff_agency") == []
    # আসল store ছোঁয়া হয়নি — ৩ seed intact।
    _real = load_memory()
    assert {"assistant-name", "reply-language", "gate-words"} <= {
        e["slug"] for e in _real.list_entries()
        if e.get("box") == "shared"} and all(_real.verify_all().values())

    # record_owner_message: valid quote শেখে, ভুল quote বারণ।
    e = record_owner_message(
        "Boss (test): নতুন নিয়ম — শুক্রবার ছুটি",
        "routines", "friday-off", "শুক্রবার ছুটি।",
        quote="শুক্রবার ছুটি", source_ref="test",
        memory_path=_tmp_mem)
    assert e["slug"] == "friday-off" and e["box"] == "shared"
    try:
        record_owner_message(
            "Boss (test): আজ ছুটি", "routines", "bad-rule", "x",
            quote="Boss কখনো বলেনি", memory_path=_tmp_mem)
        raise SystemExit("FAIL: unverified owner message was learned")
    except ValueError:
        pass

    # Gated forget: request -> approve ছাড়া execute বারণ -> "go"-তে
    # approve -> execute_once-এ মোছা; ভুল gate word বারণ।
    conf = request_forget_owner_entry(
        "routines", "friday-off", memory_path=_tmp_mem,
        confirmations_path=_tmp_conf, approvals_path=_tmp_appr)
    assert conf["status"] == "asked" and conf["action"] == "delete"
    try:
        forget_owner_entry("routines", "friday-off", conf["id"],
                           memory_path=_tmp_mem,
                           confirmations_path=_tmp_conf,
                           approvals_path=_tmp_appr)
        raise SystemExit("FAIL: forget ran without approval")
    except ValueError:
        pass
    _store = ConfirmationStore(confirmations_path=_tmp_conf,
                               approvals_path=_tmp_appr)
    try:
        _store.approve(conf["id"], gate_word="send")
        raise SystemExit("FAIL: wrong gate word approved a delete")
    except ValueError:
        pass
    _store.approve(conf["id"], gate_word="go")
    done = forget_owner_entry("routines", "friday-off", conf["id"],
                              memory_path=_tmp_mem,
                              confirmations_path=_tmp_conf,
                              approvals_path=_tmp_appr)
    assert done["status"] == "executed", done
    try:
        load_memory(_tmp_mem).get("routines", "friday-off")
        raise SystemExit("FAIL: forgotten entry still present")
    except KeyError:
        pass
    # Skill-finder: local search + DRAFT proposal (TEMP proposals path —
    # আসল store/skill-proposals.json ছোঁয়া হয় না)।
    _tmp_props = os.path.join(_tmp_dir, "skill-proposals.json")
    r2 = route_task({"type": "find_skill", "query": "backup",
                     "propose": True, "agent": "Backup & Recovery Agent",
                     "candidate_repo": "makash/godmode",
                     "candidate_skill": "backup",
                     "source_url": "https://github.com/makash/godmode",
                     "license": "MIT",
                     "fit_note": "test proposal",
                     "proposals_path": _tmp_props},
                    tasks_path=_tmp_tasks, approvals_path=_tmp_appr)
    assert r2["status"] == "skill-search"
    assert r2["routed_to"] == "00-CEO-Core.skill_finder"
    assert any(m["name"] == "backup-recovery-agent"
               for m in r2["local_matches"])
    assert r2["proposal"]["status"] == "proposed"
    print("main_ceo_bot: OK (routing works, Agency Chief is REAL, "
          "memory wired: read + quote-verified learn + "
          "gated forget, skill-finder wired)")
