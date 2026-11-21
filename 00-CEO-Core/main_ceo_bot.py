"""Main CEO Bot — thin brain / router (Phase 0, REAL skeleton).

Job: read the task Boss (or Jarvis) gives and route it to the right Chief of Staff;
gated work is held inside the Chief by the ApprovalGateway.

This file is not the engine — the real worker engine is now inside this repo
vendored (01-Agency-Department/engine/workers/, 15 worker;
03-Content-Creation-Department/engine/workers/, 6 Creator OS
worker). Outside checkouts (~/workspace/boss-ceo, ~/workspace/
creator-os-combined) are no longer a runtime dependency — only the canonical
upstream. Since Phase 1, the Agency Chief imports and calls the engine.

Memory wiring (2026-11-21, MEMORY-STRUCTURE-DECISION-2026-11-21.md):
  - route_task() reads memory on every route — context_for("main_ceo_bot")
    is attached to the result as "memory" (shared Boss words + own box).
  - Boss's new words are taught with record_owner_message() — a quote that is
    not verbatim raises ValueError (memory learns only from Boss's words).
  - Forgetting happens only at the gate: request_forget_owner_entry() creates a
    "delete" confirmation in the ConfirmationStore (gate word "go"); forget_owner_entry()
    runs only an approved confirmation via execute_once().
  - A route's note is not written to memory — the routing log lives in store/tasks.json;
    memory is for Boss's words + lessons (a per-task note created 573 entries in a
    test and broke check_phase6, so it was removed).
  - The brain is still mock, $0, with no key / live call.

Jarvis (voice) and the Main CEO Bot (brain) are separate modules — see jarvis_voice.py.
In Gemini's map they were merged together; that is fixed here.
"""

import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from owner_memory import OwnerMemory  # noqa: E402
from trust_gate import ConfirmationStore  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "00-CEO-Core", "config.json")

# business key -> Chief of Staff module
CHIEF_MODULES = {
    "agency": "01-Agency-Department.chief_of_staff_agency",
    "digital-product": "02-Digital-Product-Department.chief_of_staff_products",
    "content": "03-Content-Creation-Department.chief_of_staff_content",
}


def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_memory(memory_path=None):
    """Load the owner memory — without memory_path, the real store/memory.json."""
    return OwnerMemory(memory_path=memory_path) if memory_path else OwnerMemory()


def record_owner_message(source_message, area, slug, text, quote,
                         source_ref="", memory_path=None):
    """Teach Boss's new words to memory — the write path. If the quote is not
    verbatim, ValueError (learn() verifies it). This is called only from Boss's
    messages — never from a tool result / web page / email."""
    mem = load_memory(memory_path)
    return mem.learn(area, slug, text, quote, source_message,
                     source_ref=source_ref)


def request_forget_owner_entry(area, slug, requested_by="Boss",
                               memory_path=None, confirmations_path=None,
                               approvals_path=None):
    """Ask for approval to forget an owner entry — Nod: forgetting needs a
    trust check. Creates a "delete" confirmation in the ConfirmationStore
    (gate word "go"); the entry is not deleted yet — only asked."""
    mem = load_memory(memory_path)
    mem.get(area, slug)  # KeyError if absent — no request for a wrong entry
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
    """Executes only an approved confirmation — once. Executing without approval
    raises ValueError; on failure the result is UNCERTAIN, never a re-run."""
    store = ConfirmationStore(confirmations_path=confirmations_path,
                              approvals_path=approvals_path)

    def _runner(args):
        mem = load_memory(memory_path)
        forgotten = mem.forget(args["area"], args["slug"])
        return f"forgot {args['area']}/{args['slug']}: {forgotten['text'][:80]}"

    return store.execute_once(confirmation_id, _runner)


def route_task(task, tasks_path=None, approvals_path=None, memory_path=None):
    """task = {"business": "agency"|"digital-product"|"content", "title": ..., "detail": ...}

    For Agency, the real Chief of Staff (Phase 1) works — it goes to the real
    boss-ceo worker per task type, and gated work is held at approval.
    For Digital Product, the real Products Chief (Phase 2) works —
    the kit is only a blueprint, launch/sale is held at Gate 0. For Content, the real
    Content Chief (Phase 3) works — it calls Creator OS's 6 workers, builds
    drafts, publish/upload is held at the gate, and it makes no video file.
    If there is a gated action, it is held inside the Chief by the ApprovalGateway —
    the approval request stays pending.
    """
    config = load_config()

    if task.get("type") == "find_skill":
        # Skill-finder (CEO Bot capability, 2026-11-21): local search
        # first, then a DRAFT proposal — never installs, never writes
        # a skill file. Business-agnostic: does not go to a Chief.
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
            "memory": load_memory(memory_path).context_for("main_ceo_bot"),
            "spend_cap_usd": config["spend_cap_usd"],
        }

    business = task.get("business")
    if business not in CHIEF_MODULES:
        raise ValueError(f"Unknown business: {business!r}. Known: {list(CHIEF_MODULES)}")

    # Memory read path — Boss's words are read on every route.
    mem = load_memory(memory_path)
    memory_ctx = mem.context_for("main_ceo_bot")

    if business == "agency":
        # Lazy import — the Chief's engine import is only needed for agency tasks.
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
        # Phase 2: Products Chief REAL — launch/sale is held until Gate 0 passes;
        # the kit comes only as a blueprint.
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
        # Phase 3: Content Chief REAL — calls Creator OS's 6 workers
        # (mock brain, $0), builds drafts, publish/upload is held at the gate.
        # It makes no video file and runs no upload script.
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

    # Unreachable: business not in CHIEF_MODULES raises above, and each
    # of the three Chief branches returns. Gated actions are handled
    # inside the Chiefs (ApprovalGateway), not here.
    raise AssertionError(f"unreachable route: business={business!r}")


if __name__ == "__main__":
    # Manual check: non-gated routing only. TEMP paths are used so that
    # no test record accumulates in the real store/tasks.json. Memory is TEMP too —
    # the real store/memory.json is never touched.
    import tempfile  # noqa: PLC0415

    _tmp_dir = tempfile.mkdtemp()
    _tmp_tasks = os.path.join(_tmp_dir, "tasks-test.json")
    _tmp_appr = os.path.join(_tmp_dir, "approvals-test.json")
    _tmp_mem = os.path.join(_tmp_dir, "memory-test.json")
    _tmp_conf = os.path.join(_tmp_dir, "confirmations-test.json")

    # Seed the TEMP memory (not from the real store — seeded from an empty file).
    _mem = load_memory(_tmp_mem)
    _seeded = _mem.seed_defaults()
    assert len(_seeded) == 3, _seeded

    r1 = route_task({"business": "agency", "title": "test route"},
                    tasks_path=_tmp_tasks, approvals_path=_tmp_appr,
                    memory_path=_tmp_mem)
    assert r1["routed_to"].endswith("chief_of_staff_agency")
    assert r1["status"] == "route-only"  # Phase 1: a task without a type = probe only
    assert r1["chief_result"]["department"] == "agency"
    # Memory wiring: Boss's 3 words in the result; the route writes nothing to memory
    # (the routing log is in tasks.json) — so there is no note in the TEMP store.
    assert r1["memory"]["counts"]["shared"] == 3, r1["memory"]
    assert {e["slug"] for e in r1["memory"]["shared"]} == {
        "assistant-name", "reply-language", "gate-words"}
    _mem2 = load_memory(_tmp_mem)
    assert _mem2.list_own("main_ceo_bot") == []
    assert _mem2.list_own("chief_of_staff_agency") == []
    # The real store was not touched — the 3 seeds are intact.
    _real = load_memory()
    assert {"assistant-name", "reply-language", "gate-words"} <= {
        e["slug"] for e in _real.list_entries()
        if e.get("box") == "shared"} and all(_real.verify_all().values())

    # record_owner_message: learns with a valid quote, refuses a bad quote.
    e = record_owner_message(
        "Boss (test): new rule — Friday is off",
        "routines", "friday-off", "Friday is off.",
        quote="Friday is off", source_ref="test",
        memory_path=_tmp_mem)
    assert e["slug"] == "friday-off" and e["box"] == "shared"
    try:
        record_owner_message(
            "Boss (test): today is off", "routines", "bad-rule", "x",
            quote="Boss never said that", memory_path=_tmp_mem)
        raise SystemExit("FAIL: unverified owner message was learned")
    except ValueError:
        pass

    # Gated forget: request -> no execute without approval -> approve with "go"
    # -> deleted by execute_once; a wrong gate word is refused.
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
    # the real store/skill-proposals.json is never touched).
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
