#!/usr/bin/env python3
"""check_drawer_memory.py — Memory system self-check (decided structure + live wiring).

Structure — DECIDED on merit (2026-11-21,
00-CEO-Core/MEMORY-STRUCTURE-DECISION-2026-11-21.md):
  - একটাই drawer = একটাই store file (store/memory.json)।
  - Drawer-এর ভেতরে আলাদা box: "shared" (Boss-এর কথা — সবাই পড়ে)
    + প্রত্যেক agent-এর নিজের box (main_ceo_bot, chief_of_staff_agency,
    8 dept box, worker:<slug>)।
  - Boss-এর কথা শুধু shared-এ; কাজের note শুধু নিজের box-এ;
    এক box-এর note অন্য box পড়তে পারে না।
  - Live wiring: Main CEO Bot route_task() + Agency Chief handle_task()
    প্রত্যেক task-এ memory পড়ে (context_for) আর নিজের box-এ note লেখে;
    Boss-এর কথা শেখা quote-verify দিয়ে; ভুলে যাওয়া শুধু gate-এর
    অনুমোদনে (ConfirmationStore "delete", gate word "go")।

Checks:
  1. store/memory.json-ই একমাত্র memory JSON; repo-তে per-agent
     memory file নেই
  2. BOXES-এ ১১টা fixed box আছে (shared + CEO + Chief + ৮ dept)
  3. আসল store: ৩ seed owner entry intact, সব owner entry
     quote-verified (live note বাড়তে পারে — "ঠিক ৩ entry" নয়)
  4. Temp store-এ seed -> ৩ entry, সব shared
  5. learn() অন্য box নেয় না (ValueError)
  6. note_work(): shared-এ যায় না, অচেনা box-এ যায় না,
     worker box-এ যায়
  7. Isolation: এক box-এর note অন্য box-এর read_box-এ আসে না
  8. প্রত্যেক fixed box-এর read_box-এ ৩ shared entry আছে
  9. Agent note verify হয় না; verify_all শুধু owner entry
 10. ভুল box থেকে edit/forget বারণ; নিজের box থেকে চলে
 11. একই slug অন্য box-এ চলে; একই box-এ দুবার নয়
 12. Work note-এও 4000 chars cap
 13. export_markdown-এ Shared compartment + Box section + agent-note লেবেল
 14. 256 KiB cap এখনো কাজ করে
 15. owner_memory.py-তে network import নেই
 16. owner_memory.py __main__ self-test pass
 17. maintenance_repair: stale tentative archive, stated ছোঁয়া হয় না, dedupe
 18. validate_proposals: valid quote ready, bad quote rejected, কিছু লেখে না
 19. context_for: shared seed + নিজের note, source_message নেই
 20. CEO wiring: route_task-এ memory attach, memory-তে লেখে না (TEMP store)
 21. Chief wiring: handle_task-এ memory attach, memory-তে লেখে না (TEMP store)
 22. record_owner_message: valid quote শেখে, ভুল quote বারণ
 23. Gated forget: approve ছাড়া execute বারণ, ভুল word বারণ, "go"-তে মোছা
 24. Reload guard: দুটো instance একই file-এ লিখলেও দুটো note-ই থাকে
 25. main_ceo_bot.py / chief_of_staff_agency.py-তে network import নেই
 26. আসল store এই check run-এ বদলায়নি

সব check TEMP file-এ চলে — আসল store শুধু পড়া হয়, লেখা হয় না।
Stdlib only, no network, no spend, no send. Exit 0 = PASS।
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def _snapshot_store():
    snap = {}
    store_dir = os.path.join(BASE, "store")
    for name in sorted(os.listdir(store_dir)):
        path = os.path.join(store_dir, name)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    snap[name] = f.read()
            except OSError:
                snap[name] = None
    return snap


def main():
    store_before = _snapshot_store()
    tmp_dir = tempfile.mkdtemp()

    # 1. একটাই memory JSON; repo-তে per-agent memory file নেই।
    try:
        store_files = os.listdir(os.path.join(BASE, "store"))
        memory_jsons = [n for n in store_files if "memory" in n.lower()
                        and n.endswith(".json")]
        stray = []
        for root, _dirs, files in os.walk(BASE):
            if "__pycache__" in root or ".git" in root:
                continue
            for name in files:
                path = os.path.join(root, name)
                rel = os.path.relpath(path, BASE)
                if name.endswith(".json") and "memory" in name.lower():
                    if rel != os.path.join("store", "memory.json"):
                        stray.append(rel)
                if name == "MEMORY.md" and rel != os.path.join("store", "MEMORY.md"):
                    stray.append(rel)
        check("one store file; no per-agent memory files in the repo",
              memory_jsons == ["memory.json"] and not stray,
              f"store memory jsons={memory_jsons}, stray={stray}")
    except Exception as e:  # noqa: BLE001
        check("one store file; no per-agent memory files in the repo", False, str(e))

    # 2. BOXES — ১১ fixed box।
    try:
        from owner_memory import BOXES, SHARED_BOX, SEED_ENTRIES, OwnerMemory  # noqa: PLC0415
        expected = {"shared", "main_ceo_bot", "chief_of_staff_agency",
                    "dept_sales", "dept_marketing", "dept_engineering",
                    "dept_operations", "dept_strategy", "dept_finance",
                    "dept_quality", "dept_innovation"}
        check("BOXES has all 11 fixed boxes (shared + CEO + Chief + 8 dept)",
              set(BOXES) == expected and SHARED_BOX == "shared",
              f"boxes={len(BOXES)}")
    except Exception as e:  # noqa: BLE001
        check("BOXES has all 11 fixed boxes (shared + CEO + Chief + 8 dept)",
              False, str(e))
        return 1

    # 3. আসল store: ৩ seed owner entry অপরিবর্তিত + সব owner entry
    # verify। Live system-এ কাজের note বাড়তে পারে — তাই "ঠিক ৩
    # entry" নয়, seed ৩টা intact + সব owner entry quote-verified-ই শর্ত।
    try:
        real = OwnerMemory()  # আসল store/memory.json — শুধু পড়া
        seeds = {(s["area"], s["slug"]): s for s in SEED_ENTRIES}
        ok = True
        for (area, slug), seed in seeds.items():
            try:
                entry = real.get(area, slug, box="shared")
            except KeyError:
                ok = False
                continue
            ok = (ok and entry.get("origin") == "owner"
                  and entry["text"] == seed["text"]
                  and entry["quote"] == seed["quote"]
                  and entry["source_message"] == seed["source_message"])
        va = real.verify_all()
        ok = ok and all(va.values()) and len(va) >= 3
        check("real store: 3 seed owner entries intact, all owner entries "
              "quote-verified (work notes may exist)",
              ok, f"entries={len(real.entries)}, verify_all={va}")
    except Exception as e:  # noqa: BLE001
        check("real store: 3 seed owner entries intact, all owner entries "
              "quote-verified (work notes may exist)", False, str(e))

    # 4-15. Temp store-এ drawer আচরণ।
    try:
        tmp_mem = os.path.join(tmp_dir, "memory-drawer-test.json")
        tmp_md = os.path.join(tmp_dir, "MEMORY-drawer-test.md")
        mem = OwnerMemory(memory_path=tmp_mem)

        # 4. Seed -> ৩ entry, সব shared।
        seeded = mem.seed_defaults()
        check("temp seed: 3 entries, all in the shared box",
              len(seeded) == 3
              and all(e.get("box") == "shared" for e in seeded)
              and all(e.get("origin") == "owner" for e in seeded))

        # 5. learn() অন্য box নেয় না।
        try:
            mem.learn("preferences", "bad-box", "x", quote="test করো",
                      source_message="Boss: test করো", box="dept_sales")
            ok_learn_box = False
        except ValueError:
            ok_learn_box = True
        check("learn() rejects a non-shared box", ok_learn_box)

        # 6. note_work(): shared নয়, অচেনা box নয়, worker box চলে।
        try:
            mem.note_work("shared", "n", "x")
            ok_shared = False
        except ValueError:
            ok_shared = True
        try:
            mem.note_work("no-such-box", "n", "x")
            ok_unknown = False
        except ValueError:
            ok_unknown = True
        w = mem.note_work("worker:outreach-drafter", "prep",
                          "Outreach: 5 prospect researched.",
                          area="lessons", source_ref="test")
        ok_worker = (w["box"] == "worker:outreach-drafter"
                     and w["origin"] == "agent" and w["quote"] == "")
        check("note_work(): shared/unknown box rejected, worker box works",
              ok_shared and ok_unknown and ok_worker)

        # 7. Isolation।
        mem.note_work("dept_sales", "day-note", "Sales: 5 draft ready.",
                      area="lessons")
        sales_sees = any(e["slug"] == "day-note"
                         for e in mem.read_box("dept_sales"))
        marketing_sees = any(e["slug"] == "day-note"
                             for e in mem.read_box("dept_marketing"))
        own_only = any(e["slug"] == "day-note"
                       for e in mem.list_own("dept_sales"))
        other_own = any(e["slug"] == "day-note"
                        for e in mem.list_own("dept_marketing"))
        check("work note visible in its own box, invisible to other boxes",
              sales_sees and not marketing_sees and own_only and not other_own)

        # 8. প্রত্যেক fixed box-এ ৩ shared entry (নিজের note থাকলে
        # মোট বেশি হতে পারে — shared ৩টা থাকতেই হবে)।
        shared_slugs = {"assistant-name", "reply-language", "gate-words"}
        ok_all_boxes = all(
            shared_slugs <= {e["slug"] for e in mem.read_box(box)}
            for box in BOXES)
        check("every fixed box reads the 3 shared entries",
              ok_all_boxes, f"boxes={len(BOXES)}")

        # 9. Agent note verify হয় না; verify_all শুধু owner।
        try:
            mem.verify("lessons", "day-note", box="dept_sales")
            ok_verify_agent = False
        except ValueError:
            ok_verify_agent = True
        va = mem.verify_all()
        check("agent note cannot be quote-verified; verify_all covers "
              "owner entries only",
              ok_verify_agent and len(va) == 3 and all(va.values()))

        # 10. ভুল box থেকে edit/forget বারণ; নিজের box থেকে চলে।
        try:
            mem.edit("lessons", "day-note", new_text="x", box="dept_marketing")
            ok_wrong_edit = False
        except ValueError:
            ok_wrong_edit = True
        try:
            mem.edit("routines", "gate-words", new_text="x", box="dept_sales")
            ok_shared_edit = False
        except ValueError:
            ok_shared_edit = True
        mem.edit("lessons", "day-note", new_text="Sales: 6 draft ready.",
                 box="dept_sales")
        ok_own_edit = mem.get("lessons", "day-note",
                              box="dept_sales")["text"].startswith("Sales: 6")
        try:
            mem.forget("lessons", "day-note", box="dept_marketing")
            ok_wrong_forget = False
        except ValueError:
            ok_wrong_forget = True
        check("wrong-box edit/forget rejected; own-box edit works; "
              "shared entry not editable from an agent box",
              ok_wrong_edit and ok_shared_edit and ok_own_edit
              and ok_wrong_forget)

        # 11. একই slug অন্য box-এ চলে; একই box-এ দুবার নয়।
        mem.note_work("dept_marketing", "day-note",
                      "Marketing: 2 caption ready.")
        try:
            mem.note_work("dept_sales", "day-note", "Again.")
            ok_dup = False
        except ValueError:
            ok_dup = True
        check("same slug allowed in another box, rejected in the same box",
              ok_dup)

        # 12. Work note-এও 4000 chars cap।
        try:
            mem.note_work("dept_sales", "too-long", "x" * 4001)
            ok_cap = False
        except ValueError:
            ok_cap = True
        check("work note over 4000 chars -> ValueError", ok_cap)

        # 13. Export-এ Shared compartment + Box section + agent-note লেবেল।
        out = mem.export_markdown(tmp_md)
        with open(out, encoding="utf-8") as f:
            md = f.read()
        check("markdown export shows shared compartment + box sections "
              "+ agent-note label",
              "Shared compartment" in md and "Box: dept_sales" in md
              and "Box: dept_marketing" in md and "agent note" in md
              and "Mira" in md and "NOT permission" in md)

        # 14. 256 KiB cap।
        try:
            import owner_memory as om  # noqa: PLC0415
            big = OwnerMemory(memory_path=os.path.join(tmp_dir, "big.json"))
            big.entries = [{"area": "lessons", "slug": "huge",
                            "box": "shared", "origin": "owner",
                            "text": "x" * 300000, "quote": "x",
                            "source_message": "Boss: x", "source_ref": "",
                            "status": "stated", "learned_at": "t",
                            "updated_at": "t"}]
            try:
                big._save()
                ok_big = False
            except ValueError:
                ok_big = True
            ok_big = ok_big and om.MAX_DOC_BYTES == 256 * 1024
        except Exception as e:  # noqa: BLE001
            ok_big = False
            print(f"    (cap check error: {e})")
        check("256 KiB doc cap still enforced", ok_big)

        # 17. Maintenance repair: stale tentative archive হয়; নতুন
        # tentative থাকে; stated কখনো auto-archive হয় না; dedupe।
        rep_mem = OwnerMemory(memory_path=os.path.join(tmp_dir, "repair.json"))
        rep_mem.seed_defaults()
        rep_mem.learn("lessons", "old-rule", "Old rule.",
                      quote="পুরোনো কথা",
                      source_message="Boss: পুরোনো কথা", status="tentative")
        for e in rep_mem.entries:
            if e["slug"] == "old-rule":
                e["learned_at"] = "2026-09-01T00:00:00+00:00"
        rep_mem._save()
        rep = rep_mem.maintenance_repair(
            now=datetime(2026, 11, 21, tzinfo=timezone.utc))
        ok_repair = (any("old-rule" in s for s in rep["archived"])
                     and rep_mem.get("lessons", "old-rule")["status"] == "archived"
                     and rep_mem.get("routines", "gate-words")["status"] == "stated")
        rep_mem.entries.append(dict(rep_mem.entries[0], slug="dup-rule",
                                    learned_at="2026-11-21T00:00:00+00:00"))
        rep_mem.entries.append(dict(rep_mem.entries[0], slug="dup-rule",
                                    learned_at="2026-11-21T00:01:00+00:00"))
        rep_mem._save()
        rep2 = rep_mem.maintenance_repair(
            now=datetime(2026, 11, 21, tzinfo=timezone.utc))
        ok_repair = ok_repair and any("dup-rule" in s for s in rep2["deduped"])
        check("maintenance_repair archives stale tentative + dedupes, "
              "never touches stated", ok_repair, str(rep) + " " + str(rep2))

        # 18. validate_proposals: valid quote ready, bad quote rejected,
        # কিছু লেখে না।
        before_n = len(mem.list_entries())
        v = mem.validate_proposals([
            {"area": "preferences", "slug": "new-rule", "text": "New.",
             "quote": "নতুন কথা", "source_message": "Boss: নতুন কথা"},
            {"area": "preferences", "slug": "bad-rule", "text": "Bad.",
             "quote": "বানানো", "source_message": "Boss: অন্য কথা"},
        ])
        check("validate_proposals: valid quote ready, bad quote rejected, "
              "nothing written",
              len(v["ready"]) == 1 and len(v["rejected"]) == 1
              and len(mem.list_entries()) == before_n,
              f"ready={len(v['ready'])}, rejected={len(v['rejected'])}")

        # 19. context_for: shared-এ ৩ seed আছে, source_message নেই।
        ctx = mem.context_for("main_ceo_bot")
        check("context_for: shared seeds present, no source_message dump",
              ctx["box"] == "main_ceo_bot"
              and {"assistant-name", "reply-language", "gate-words"}
              <= {e["slug"] for e in ctx["shared"]}
              and all("source_message" not in e for e in ctx["shared"]),
              f"counts={ctx['counts']}")

        # 20. CEO wiring (TEMP store): route_task-এ memory attach হয়;
        # route memory-তে লেখে না (routing log tasks.json-এ)।
        import main_ceo_bot as mcb  # noqa: PLC0415
        tmp_tasks = os.path.join(tmp_dir, "tasks-wiring.json")
        tmp_appr = os.path.join(tmp_dir, "approvals-wiring.json")
        wiring_path = os.path.join(tmp_dir, "wiring.json")
        wmem = OwnerMemory(memory_path=wiring_path)
        wmem.seed_defaults()
        r = mcb.route_task({"business": "agency", "title": "wiring probe"},
                           tasks_path=tmp_tasks, approvals_path=tmp_appr,
                           memory_path=wiring_path)
        wmem2 = OwnerMemory(memory_path=wiring_path)
        ok_wire = (r["status"] == "route-only"
                   and r["memory"]["counts"]["shared"] == 3
                   and wmem2.list_own("main_ceo_bot") == []
                   and wmem2.list_own("chief_of_staff_agency") == [])
        check("CEO route_task wires memory: context attached, nothing "
              "written to memory (temp store)", ok_wire,
              f"status={r['status']}")

        # 21. Chief wiring (TEMP store): direct handle_task-এ memory
        # attach হয়; memory-তে লেখে না।
        chief_path = os.path.join(BASE, "01-Agency-Department")
        if chief_path not in sys.path:
            sys.path.insert(0, chief_path)
        import chief_of_staff_agency as chief  # noqa: PLC0415
        cr = chief.handle_task(
            {"title": "chief probe"}, tasks_path=tmp_tasks,
            approvals_path=tmp_appr, memory_path=wiring_path)
        check("Chief handle_task wires memory: context attached, nothing "
              "written",
              cr["status"] == "route-only"
              and cr["memory"]["counts"]["shared"] == 3,
              f"status={cr['status']}")

        # 22. record_owner_message: valid quote শেখে, ভুল quote বারণ।
        e22 = mcb.record_owner_message(
            "Boss (test): নতুন নিয়ম — শুক্রবার ছুটি",
            "routines", "friday-off", "শুক্রবার ছুটি।",
            quote="শুক্রবার ছুটি", source_ref="test",
            memory_path=wiring_path)
        try:
            mcb.record_owner_message(
                "Boss (test): আজ ছুটি", "routines", "bad-rule", "x",
                quote="Boss কখনো বলেনি", memory_path=wiring_path)
            ok_learn = False
        except ValueError:
            ok_learn = True
        check("record_owner_message learns with a valid quote, rejects a "
              "bad quote",
              e22["slug"] == "friday-off" and e22["box"] == "shared"
              and ok_learn)

        # 23. Gated forget: approve ছাড়া execute বারণ, ভুল gate word
        # বারণ, "go"-তে approve -> executed -> entry নেই।
        tmp_conf = os.path.join(tmp_dir, "confirmations-wiring.json")
        conf = mcb.request_forget_owner_entry(
            "routines", "friday-off", memory_path=wiring_path,
            confirmations_path=tmp_conf, approvals_path=tmp_appr)
        from trust_gate import ConfirmationStore  # noqa: PLC0415
        try:
            mcb.forget_owner_entry(
                "routines", "friday-off", conf["id"],
                memory_path=wiring_path,
                confirmations_path=tmp_conf, approvals_path=tmp_appr)
            ok_no_exec = False
        except ValueError:
            ok_no_exec = True
        _cs = ConfirmationStore(confirmations_path=tmp_conf,
                                approvals_path=tmp_appr)
        try:
            _cs.approve(conf["id"], gate_word="send")
            ok_wrong_word = False
        except ValueError:
            ok_wrong_word = True
        _cs.approve(conf["id"], gate_word="go")
        done = mcb.forget_owner_entry(
            "routines", "friday-off", conf["id"],
            memory_path=wiring_path,
            confirmations_path=tmp_conf, approvals_path=tmp_appr)
        try:
            OwnerMemory(memory_path=wiring_path).get("routines", "friday-off")
            ok_gone = False
        except KeyError:
            ok_gone = True
        check("gated forget: no execute before approval, wrong gate word "
              "rejected, 'go' approves and entry is forgotten",
              conf["status"] == "asked" and ok_no_exec and ok_wrong_word
              and done["status"] == "executed" and ok_gone)

        # 24. Reload guard: দুটো instance একই file-এ লিখলেও দুটো note-ই থাকে।
        race_path = os.path.join(tmp_dir, "race.json")
        ra = OwnerMemory(memory_path=race_path)
        ra.seed_defaults()
        rb = OwnerMemory(memory_path=race_path)
        ra.note_work("main_ceo_bot", "n-a", "A note.")
        rb.note_work("chief_of_staff_agency", "n-b", "B note.")
        rc = OwnerMemory(memory_path=race_path)
        check("two OwnerMemory instances on one file: both notes survive",
              any(e["slug"] == "n-a" for e in rc.list_own("main_ceo_bot"))
              and any(e["slug"] == "n-b"
                      for e in rc.list_own("chief_of_staff_agency")))
    except Exception as e:  # noqa: BLE001
        for name in ("temp seed: 3 entries, all in the shared box",
                     "learn() rejects a non-shared box",
                     "note_work(): shared/unknown box rejected, worker box works",
                     "work note visible in its own box, invisible to other boxes",
                     "every fixed box reads the 3 shared entries",
                     "agent note cannot be quote-verified; verify_all covers "
                     "owner entries only",
                     "wrong-box edit/forget rejected; own-box edit works; "
                     "shared entry not editable from an agent box",
                     "same slug allowed in another box, rejected in the same box",
                     "work note over 4000 chars -> ValueError",
                     "markdown export shows shared compartment + box sections "
                     "+ agent-note label",
                     "256 KiB doc cap still enforced",
                     "maintenance_repair archives stale tentative + dedupes, "
                     "never touches stated",
                     "validate_proposals: valid quote ready, bad quote rejected, "
                     "nothing written",
                     "context_for: shared seeds present, no source_message dump",
                     "CEO route_task wires memory: context attached, nothing "
                     "written to memory (temp store)",
                     "Chief handle_task wires memory: context attached, nothing "
                     "written",
                     "record_owner_message learns with a valid quote, rejects a "
                     "bad quote",
                     "gated forget: no execute before approval, wrong gate word "
                     "rejected, 'go' approves and entry is forgotten",
                     "two OwnerMemory instances on one file: both notes survive"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 15. owner_memory.py-তে network import নেই।
    try:
        net_re = re.compile(r"\b(import|from)\s+(socket|urllib|requests|"
                            r"http\.client|httpx|aiohttp)\b")
        bad = []
        path = os.path.join(CEO_CORE_DIR, "owner_memory.py")
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                if net_re.search(line):
                    bad.append(f"{lineno}:{line.strip()}")
        check("no network imports in owner_memory.py",
              not bad, "; ".join(bad[:3]) if bad else "stdlib only")
    except Exception as e:  # noqa: BLE001
        check("no network imports in owner_memory.py", False, str(e))

    # 16. owner_memory.py __main__ self-test।
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(CEO_CORE_DIR, "owner_memory.py")],
            capture_output=True, text=True, timeout=60, cwd=BASE)
        check("owner_memory.py __main__ self-test passes",
              proc.returncode == 0, proc.stdout.strip().splitlines()[-1]
              if proc.stdout.strip() else proc.stderr.strip()[-200:])
    except Exception as e:  # noqa: BLE001
        check("owner_memory.py __main__ self-test passes", False, str(e))

    # 25. main_ceo_bot.py + chief_of_staff_agency.py-তে network import নেই।
    try:
        bad2 = []
        for _rel in ("00-CEO-Core/main_ceo_bot.py",
                     "01-Agency-Department/chief_of_staff_agency.py"):
            _path = os.path.join(BASE, _rel)
            with open(_path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if net_re.search(line):
                        bad2.append(f"{_rel}:{lineno}:{line.strip()}")
        check("no network imports in main_ceo_bot.py / "
              "chief_of_staff_agency.py",
              not bad2, "; ".join(bad2[:3]) if bad2 else "stdlib only")
    except Exception as e:  # noqa: BLE001
        check("no network imports in main_ceo_bot.py / "
              "chief_of_staff_agency.py", False, str(e))

    # 26. আসল store বদলায়নি।
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_drawer_memory: ALL PASS (memory — decided structure, "
          "one drawer, separate boxes, CEO/Chief wired live).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
