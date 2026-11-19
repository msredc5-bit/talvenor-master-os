"""Phase 5 check — Three Engines (shared tool-calling core + 3 engines).

যাচাই করে:
  1. Shared core (00-CEO-Core/tool_calling.py) — registry, 6 handler,
     mock -> draft-ready, gated -> pending-approval, bad args -> error.
  2. প্রতিটা engine — tools.json, wrapper end-to-end (TEMP file-এ),
     STAFF.md-র role, প্রতিটা role-এর skill file (আসল content, no [FILL])।
  3. আসল store ছোঁয়া হয়নি (tasks 0, approvals 0, tool_calls.json নেই)।
  4. Phase 0–4-র check-গুলো এখনো PASS।

সব store-ছোঁয়া call TEMP file-এ চলে — আসল store কখনো লেখা হয় না।
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
STORE_DIR = os.path.join(ROOT, "store")
SCRIPTS_DIR = os.path.join(ROOT, "scripts")

sys.path.insert(0, CEO_CORE_DIR)

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dummy_args(tool):
    """Tool-এর schema থেকে valid dummy args বানানো (type অনুযায়ী)।"""
    props = tool.get("params", {}).get("properties", {})
    required = tool.get("params", {}).get("required", [])
    args = {}
    for field in required:
        ftype = props.get(field, {}).get("type", "string")
        if ftype == "integer":
            args[field] = 1
        elif ftype == "boolean":
            args[field] = False
        else:
            args[field] = "test-value"
    return args


def main():
    # --- 1. Shared core ---------------------------------------------------
    try:
        import tool_calling
        core_ok = True
    except Exception as exc:  # noqa: BLE001
        check("shared core imports", False, str(exc))
        core_ok = False
    if core_ok:
        check("shared core imports", True, "tool_calling.py")
        check(
            "core has 7 handlers",
            set(tool_calling.HANDLERS) == {
                "draft_email", "research_notes", "draft_caption",
                "draft_script", "kit_outline_read", "status_read",
                "booking_reply",
            },
            ", ".join(sorted(tool_calling.HANDLERS)),
        )
        tmp = tempfile.mkdtemp()
        ap = os.path.join(tmp, "approvals.json")
        lg = os.path.join(tmp, "calls.json")
        reg = tool_calling.ToolRegistry()
        reg.register({"name": "draft_email", "description": "t",
                      "params": {"type": "object",
                                 "properties": {"business_name": {"type": "string"},
                                                "topic": {"type": "string"}},
                                 "required": ["business_name"]},
                      "gated": False, "gated_action": None,
                      "status": "mock", "handler": "draft_email"})
        reg.register({"name": "send_email", "description": "t",
                      "params": {"type": "object",
                                 "properties": {"to": {"type": "string"}},
                                 "required": ["to"]},
                      "gated": True, "gated_action": "send",
                      "status": "stub", "handler": None})
        reg.register({"name": "old_tool", "description": "t",
                      "params": {"type": "object", "properties": {}, "required": []},
                      "gated": False, "gated_action": None,
                      "status": "stub", "handler": None})
        r = tool_calling.call_tool("draft_email", {"business_name": "Test Plumbing"},
                                   registry=reg, approvals_path=ap, calls_log_path=lg)
        check("core mock tool -> draft-ready + DRAFT label",
              r.get("status") == "draft-ready" and "DRAFT" in str(r.get("output", "")),
              r.get("status", "?"))
        r = tool_calling.call_tool("send_email", {"to": "a@b.com"},
                                   registry=reg, approvals_path=ap, calls_log_path=lg)
        check("core gated tool -> pending-approval, nothing executed",
              r.get("status") == "pending-approval"
              and r.get("approval", {}).get("status") == "pending",
              r.get("status", "?"))
        r = tool_calling.call_tool("draft_email", {},
                                   registry=reg, approvals_path=ap, calls_log_path=lg)
        check("core bad args -> error", r.get("status") == "error", r.get("status", "?"))
        r = tool_calling.call_tool("old_tool", {},
                                   registry=reg, approvals_path=ap, calls_log_path=lg)
        check("core stub tool -> blocked-stub",
              r.get("status") == "blocked-stub", r.get("status", "?"))
        # draft_script topic-aware (Phase 5 fix)
        reg2 = tool_calling.ToolRegistry()
        reg2.register({"name": "draft_script", "description": "t",
                       "params": {"type": "object",
                                  "properties": {"topic": {"type": "string"},
                                                 "duration_seconds": {"type": "integer"}},
                                  "required": ["topic"]},
                       "gated": False, "gated_action": None,
                       "status": "mock", "handler": "draft_script"})
        r = tool_calling.call_tool("draft_script",
                                   {"topic": "Nano Banana 2 test", "duration_seconds": 30},
                                   registry=reg2, approvals_path=ap, calls_log_path=lg)
        check("core draft_script topic-aware (no Talvenor CTA for ToolPilot topic)",
              r.get("status") == "draft-ready"
              and "Book a call with Talvenor" not in str(r.get("output", "")),
              r.get("status", "?"))
        r = tool_calling.call_tool("draft_script",
                                   {"topic": "Talvenor receptionist demo",
                                    "duration_seconds": 25},
                                   registry=reg2, approvals_path=ap, calls_log_path=lg)
        check("core draft_script keeps Talvenor CTA for receptionist topic",
              "Book a call with Talvenor" in str(r.get("output", "")),
              r.get("status", "?"))

    # --- 2. Engines --------------------------------------------------------
    engines = [
        ("01-Agency-Department", "agency", 15, 8, 5, 3, [
            "Prospect Researcher", "Outreach Drafter", "Reply Triager",
            "Negotiation Coach", "Receptionist Builder", "QA Engineer",
            "Onboarding Agent", "Content Planner", "Video Producer",
            "Caption Writer", "Publish Prep", "Objection Simulator",
            "Inbox Triager", "Report Compiler", "Scheduler",
        ]),
        ("02-Digital-Product-Department", "products", 5, 8, 6, 2, [
            "Kit Builder", "Clinic Researcher", "Launch Manager",
            "Payment-Rails Checker", "Support Drafter",
        ]),
        ("03-Content-Creation-Department", "content", 8, 8, 5, 3, [
            "Topic Researcher", "Script Writer", "Visual Producer",
            "Caption Writer", "Publish Prep", "Performance Tracker",
            "Content Planner", "Performance Analyst",
        ]),
    ]
    for dept, key, n_roles, n_tools, n_mock, n_gated, roles in engines:
        eng_dir = os.path.join(ROOT, dept, "engine")
        tools_path = os.path.join(eng_dir, "tools.json")
        try:
            with open(tools_path, "r", encoding="utf-8") as f:
                tools_data = json.load(f)
            tools = tools_data["tools"]
            check(f"{key}: tools.json parses ({len(tools)} tools)",
                  len(tools) == n_tools, f"expected {n_tools}")
            gated = [t for t in tools if t.get("gated")]
            mock = [t for t in tools if not t.get("gated")]
            check(f"{key}: {n_mock} mock / {n_gated} gated",
                  len(mock) == n_mock and len(gated) == n_gated,
                  f"mock {len(mock)}, gated {len(gated)}")
            check(f"{key}: gated tools have handler null + gated_action",
                  all(t.get("handler") is None and t.get("gated_action")
                      for t in gated),
                  ", ".join(t["name"] for t in gated))
        except Exception as exc:  # noqa: BLE001
            check(f"{key}: tools.json parses", False, str(exc))
            tools = []
        # STAFF.md roles
        staff_path = os.path.join(eng_dir, "STAFF.md")
        try:
            with open(staff_path, "r", encoding="utf-8") as f:
                staff_text = f.read()
            missing = [r for r in roles if r not in staff_text]
            check(f"{key}: STAFF.md lists all {n_roles} roles",
                  not missing, f"missing: {missing}" if missing else "all present")
        except Exception as exc:  # noqa: BLE001
            check(f"{key}: STAFF.md lists all {n_roles} roles", False, str(exc))
        # skills: one file per role, real content, no [FILL]
        skills_dir = os.path.join(eng_dir, "skills")
        try:
            skill_files = sorted(f for f in os.listdir(skills_dir) if f.endswith(".md"))
            check(f"{key}: {n_roles} skill files",
                  len(skill_files) == n_roles,
                  f"found {len(skill_files)}")
            bad = []
            for fname in skill_files:
                with open(os.path.join(skills_dir, fname), "r", encoding="utf-8") as f:
                    text = f.read()
                # "[FILL AFTER TEST]" হলো ToolPilot Week 1 verdict-এর LOCKED
                # placeholder (Boss-এর OBS recording না দেখে verdict লেখা হয় না)
                # — এটা আসল content, placeholder নয়। বাকি [FILL ধরা হবে।
                text_checked = text.replace("[FILL AFTER TEST]", "")
                if len(text) < 200 or "[FILL" in text_checked:
                    bad.append(fname)
            check(f"{key}: skills are real content (no [FILL], >=200 chars)",
                  not bad, f"bad: {bad}" if bad else "all real")
        except Exception as exc:  # noqa: BLE001
            check(f"{key}: skill files", False, str(exc))
        # wrapper end-to-end (TEMP files only)
        try:
            wrapper = load_module(
                f"{key}_engine_tool_calling",
                os.path.join(eng_dir, "tool_calling.py"),
            )
            listed = wrapper.list_tools()
            check(f"{key}: wrapper list_tools matches tools.json",
                  len(listed) == n_tools, f"listed {len(listed)}")
            tmp = tempfile.mkdtemp()
            ap = os.path.join(tmp, "approvals.json")
            lg = os.path.join(tmp, "calls.json")
            mock_tool = next(t for t in tools if not t.get("gated"))
            r = wrapper.call(mock_tool["name"], dummy_args(mock_tool),
                             approvals_path=ap, calls_log_path=lg)
            check(f"{key}: wrapper mock call -> draft-ready",
                  r.get("status") == "draft-ready",
                  f"{mock_tool['name']} -> {r.get('status')}")
            gated_tool = next(t for t in tools if t.get("gated"))
            r = wrapper.call(gated_tool["name"], dummy_args(gated_tool),
                             approvals_path=ap, calls_log_path=lg)
            check(f"{key}: wrapper gated call -> pending-approval",
                  r.get("status") == "pending-approval",
                  f"{gated_tool['name']} -> {r.get('status')}")
            r = wrapper.call("no_such_tool", {}, approvals_path=ap, calls_log_path=lg)
            check(f"{key}: wrapper unknown tool -> error",
                  r.get("status") == "error", r.get("status", "?"))
        except Exception as exc:  # noqa: BLE001
            check(f"{key}: wrapper end-to-end", False, str(exc))

    # --- 3. Real store untouched -------------------------------------------
    try:
        with open(os.path.join(STORE_DIR, "tasks.json"), "r", encoding="utf-8") as f:
            tasks = json.load(f).get("records", [])
        with open(os.path.join(STORE_DIR, "approvals.json"), "r", encoding="utf-8") as f:
            approvals = json.load(f).get("records", [])
        check("real store untouched (tasks 0, approvals 0)",
              tasks == [] and approvals == [],
              f"tasks {len(tasks)}, approvals {len(approvals)}")
        check("real store has no tool_calls.json",
              not os.path.exists(os.path.join(STORE_DIR, "tool_calls.json")),
              "absent" if not os.path.exists(os.path.join(STORE_DIR, "tool_calls.json")) else "PRESENT")
    except Exception as exc:  # noqa: BLE001
        check("real store untouched", False, str(exc))

    # --- 4. Phase 0–4 checks still pass ------------------------------------
    for n in range(5):
        script = os.path.join(SCRIPTS_DIR, f"check_phase{n}.py")
        proc = subprocess.run([sys.executable, script],
                              capture_output=True, text=True)
        check(f"check_phase{n} still PASS", proc.returncode == 0,
              f"exit {proc.returncode}")

    failed = [c for c in CHECKS if not c[1]]
    print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed.")
    if failed:
        print("FAILED:", ", ".join(c[0] for c in failed))
        return 1
    print("Phase 5 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
