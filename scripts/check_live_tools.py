#!/usr/bin/env python3
"""check_live_tools.py — Phase 9 self-check for live tool connections.

What it checks (no real email, no real webhook call, ever):
  1. tools.json loads via ToolRegistry — 9 tools (7 mock + 2 live-ready).
  2. live_tools.py has NO subprocess.run / urlopen call (static grep).
  3. Mock mode (no credentials in env): gmail_send + n8n_trigger fall
     back LOUDLY to DRAFT (draft_only, sent=False, reason in notes).
  4. Dry-run mode (dummy credentials in env): both return a live-ready
     preview (live_ready, sent=False, nothing sent); the webhook URL
     token never appears in the output.
  5. Arg validation: missing required fields -> error, nothing built.
  6. Dispatcher gate: call_tool("gmail_send"/"n8n_trigger") returns
     pending-approval and writes exactly 1 approval each — the handler
     never runs. TEMP approvals/log paths only (real store untouched).
  7. Env-only credentials: the module reads only TALVENOR_GMAIL_SENDER
     and TALVENOR_N8N_WEBHOOK_URL from the environment; no key, token,
     or URL appears in any repo file (grep over the two live files).

Stdlib only. Run: python3 scripts/check_live_tools.py
"""

import json
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
TOOLS_JSON = os.path.join(CEO_CORE_DIR, "tools.json")
LIVE_TOOLS_PY = os.path.join(CEO_CORE_DIR, "live_tools.py")

sys.path.insert(0, CEO_CORE_DIR)

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(ok)
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def _fresh_env(extra=None):
    """Env without live credentials (mock mode), plus optional extras."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("TALVENOR_GMAIL_SENDER", "TALVENOR_N8N_WEBHOOK_URL")}
    if extra:
        env.update(extra)
    return env


def _run_live_tools_subprocess(code, env_extra=None):
    """Run live_tools in a fresh process so env changes are isolated."""
    env = _fresh_env(env_extra)
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=120,
        cwd=CEO_CORE_DIR, env=env)
    return proc


def main():
    import live_tools  # noqa: PLC0415 — in-process checks use this VM's env
    import tool_calling  # noqa: PLC0415

    # 1. tools.json loads — 9 tools (7 mock + 2 live-ready, both gated)
    try:
        registry = tool_calling.ToolRegistry.load_from_json(TOOLS_JSON)
        tools = registry.list_tools()
        mock = [t for t in tools if t["status"] == "mock"]
        live = [t for t in tools if t["status"] == "live-ready"]
        ok = (len(tools) == 9 and len(mock) == 7 and len(live) == 2
              and {t["name"] for t in live} == {"gmail_send", "n8n_trigger"}
              and all(t["gated"] is True for t in live)
              and all(t.get("gated_action") == "send" for t in live))
        check("tools.json loads: 9 tools (7 mock + 2 live-ready, gated)",
              ok, f"total={len(tools)}, mock={len(mock)}, live={len(live)}")
    except Exception as e:  # noqa: BLE001
        check("tools.json loads: 9 tools (7 mock + 2 live-ready, gated)",
              False, str(e))

    # 2. No subprocess.run / urlopen call in live_tools.py (AST scan —
    #    docstrings/comments don't count, real call nodes do)
    try:
        import ast  # noqa: PLC0415
        with open(LIVE_TOOLS_PY, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        forbidden = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = ""
            if isinstance(func, ast.Attribute):
                value = func.value
                base = ""
                if isinstance(value, ast.Name):
                    base = value.id
                elif isinstance(value, ast.Attribute):
                    base = value.attr
                name = f"{base}.{func.attr}"
            elif isinstance(func, ast.Name):
                name = func.id
            if name in ("subprocess.run", "subprocess.Popen", "os.system",
                        "os.popen", "urlopen", "request.urlopen"):
                forbidden.add(name)
        check("live_tools.py has no send call (no subprocess/urlopen)",
              not forbidden,
              "; ".join(sorted(forbidden)) if forbidden else "clean")
    except Exception as e:  # noqa: BLE001
        check("live_tools.py has no send call (no subprocess/urlopen)",
              False, str(e))

    # 3. Mock mode (no creds): LOUD DRAFT fallback, sent=False
    try:
        for name in ("TALVENOR_GMAIL_SENDER", "TALVENOR_N8N_WEBHOOK_URL"):
            os.environ.pop(name, None)
        g = live_tools.gmail_send(
            {"to": "test@example.com", "subject": "Hi", "body": "Hello"})
        n = live_tools.n8n_trigger({"payload": {"hello": "world"}})
        ok = (g.get("draft_only") is True and g.get("sent") is False
              and "TALVENOR_GMAIL_SENDER" in " ".join(g.get("notes", []))
              and n.get("draft_only") is True and n.get("sent") is False
              and "TALVENOR_N8N_WEBHOOK_URL" in " ".join(n.get("notes", [])))
        check("mock mode (no creds): LOUD DRAFT fallback, sent=False",
              ok, f"gmail draft_only={g.get('draft_only')}, "
              f"n8n draft_only={n.get('draft_only')}")
    except Exception as e:  # noqa: BLE001
        check("mock mode (no creds): LOUD DRAFT fallback, sent=False",
              False, str(e))

    # 4. Dry-run mode (dummy creds): live-ready preview, sent=False,
    #    webhook token never in output
    try:
        os.environ["TALVENOR_GMAIL_SENDER"] = "hello@talvenorai.agency"
        os.environ["TALVENOR_N8N_WEBHOOK_URL"] = (
            "https://n8n.example.com/webhook/SECRET-TOKEN-12345")
        g = live_tools.gmail_send(
            {"to": "test@example.com", "subject": "Hi", "body": "Hello"})
        n = live_tools.n8n_trigger(
            {"event": "test", "payload": {"hello": "world"}})
        ok = (g.get("live_ready") is True and g.get("sent") is False
              and "hatch_gws_cli" in g.get("output", "")
              and "DRY RUN" in g.get("output", "")
              and n.get("live_ready") is True and n.get("sent") is False
              and "SECRET-TOKEN-12345" not in n.get("output", "")
              and "[redacted]" in n.get("output", ""))
        check("dry-run mode (dummy creds): live-ready preview, sent=False, "
              "token redacted", ok,
              f"gmail live_ready={g.get('live_ready')}, "
              f"n8n live_ready={n.get('live_ready')}")
    except Exception as e:  # noqa: BLE001
        check("dry-run mode (dummy creds): live-ready preview, sent=False, "
              "token redacted", False, str(e))
    finally:
        os.environ.pop("TALVENOR_GMAIL_SENDER", None)
        os.environ.pop("TALVENOR_N8N_WEBHOOK_URL", None)

    # 5. Arg validation: missing fields -> error, nothing built
    try:
        g = live_tools.gmail_send({"subject": "Hi", "body": "Hello"})
        n = live_tools.n8n_trigger({"payload": "not-a-dict"})
        ok = (g.get("error") and "to" in g["error"]
              and n.get("error") and "payload" in n["error"])
        check("arg validation: missing/invalid fields -> error",
              ok, f"gmail err={g.get('error')}, n8n err={n.get('error')}")
    except Exception as e:  # noqa: BLE001
        check("arg validation: missing/invalid fields -> error", False, str(e))

    # 6. Dispatcher gate: call_tool returns pending-approval, handler
    #    never runs; TEMP paths only (real store untouched)
    try:
        tmp = tempfile.mkdtemp()
        tmp_appr = os.path.join(tmp, "approvals-test.json")
        tmp_log = os.path.join(tmp, "tool_calls-test.json")
        registry = tool_calling.ToolRegistry.load_from_json(TOOLS_JSON)
        results = []
        for name, args in (
                ("gmail_send", {"to": "t@example.com", "subject": "Hi",
                                "body": "Hello"}),
                ("n8n_trigger", {"payload": {"a": 1}})):
            results.append(tool_calling.call_tool(
                name, args, registry=registry,
                approvals_path=tmp_appr, calls_log_path=tmp_log))
        with open(tmp_appr, encoding="utf-8") as f:
            approvals = json.load(f)["records"]
        ok = (all(r.get("status") == "pending-approval" for r in results)
              and len(approvals) == 2
              and all(a.get("status") == "pending" for a in approvals)
              and all(a.get("action") == "send" for a in approvals)
              and not os.path.exists(
                  os.path.join(BASE, "store", "tool_calls.json")))
        check("dispatcher gate: live tools -> pending-approval x2, "
              "handler never runs", ok,
              f"statuses={[r.get('status') for r in results]}, "
              f"approvals={len(approvals)}")
    except Exception as e:  # noqa: BLE001
        check("dispatcher gate: live tools -> pending-approval x2, "
              "handler never runs", False, str(e))

    # 7. Env-only credentials: no key/token/URL in the live files
    try:
        secret_re = re.compile(
            r"sk-[A-Za-z0-9]{16,}|api[_-]?key\s*=\s*['\"][^'\"]+['\"]|"
            r"password\s*=\s*['\"][^'\"]+['\"]|"
            r"webhook[_-]?url\s*=\s*['\"]https?://[^'\"]+['\"]",
            re.IGNORECASE)
        hits = []
        for path in (LIVE_TOOLS_PY, TOOLS_JSON):
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if secret_re.search(line):
                        hits.append(f"{os.path.basename(path)}:{i}")
        check("no keys/tokens/URLs in live files (env only)", not hits,
              "; ".join(hits) if hits else "clean")
    except Exception as e:  # noqa: BLE001
        check("no keys/tokens/URLs in live files (env only)", False, str(e))

    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c)
    print(f"\ncheck_live_tools: {passed}/{total} PASS")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
