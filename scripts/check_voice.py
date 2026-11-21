#!/usr/bin/env python3
"""Voice self-check — Jarvis voice loop (Piper + Vosk/sherpa-onnx).

Verifies:
  1. Voice package + setup doc + script files exist
  2. jarvis_voice.py is not a STUB — the same public functions (listen/speak/
     handle_voice_command) delegate to the voice package
  3. Voice modules import (stdlib only at import time)
  4. Voice modules' top-level imports have no piper/vosk/sherpa_onnx/
     sounddevice/numpy (lazy import — imports even without them)
  5. piper / vosk / sherpa_onnx importable (probe)
  6. sounddevice importable — FAILs because this VM has no PortAudio
     (the Windows wheel bundles PortAudio — a VM-only limit, not a pretence)
  7. config.json's voice block = the VERIFIED ids + brain mock +
     phase 11 + v0.9.0
  8. No secrets in new files (api key / password / secret / bearer)
  9. Gate test (TEMP approvals): saying "send" by voice gives PENDING,
     never executes; does not touch the real store
 10. scripts/voice_test.py subprocess PASS (real synth + transcribe)
 11. Real store unchanged by this run (Phase 9: live queue)
 12. check_phase0 still PASS

Stdlib only — piper/vosk/sherpa only in importlib probes (not imported).
Exit 0 = PASS. Any FAIL's reason is printed.
"""

import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
VOICE_DIR = os.path.join(CEO_CORE_DIR, "voice")
sys.path.insert(0, CEO_CORE_DIR)

# VERIFIED 2026-11-17 — upstream sources (see VOICE-SETUP.md).
EXPECTED_VOICES = {"bn": "bn_BD-google-medium", "en": "en_US-lessac-medium"}
EXPECTED_MODELS = {"vosk_en": "vosk-model-small-en-us-0.15",
                   "sherpa_bn": "vosk-model-small-streaming-bn"}

NEW_FILES = [
    os.path.join(VOICE_DIR, "__init__.py"),
    os.path.join(VOICE_DIR, "speak.py"),
    os.path.join(VOICE_DIR, "listen.py"),
    os.path.join(VOICE_DIR, "loop.py"),
    os.path.join(CEO_CORE_DIR, "jarvis_voice.py"),
    os.path.join(CEO_CORE_DIR, "VOICE-SETUP.md"),
    os.path.join(BASE, "scripts", "voice_test.py"),
    os.path.join(BASE, "scripts", "check_voice.py"),
    os.path.join(BASE, "scripts", "jarvis_voice_loop.py"),
]

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))


def _snapshot_store():
    """Snapshot of the real store (Phase 9: store is now a live queue — taskboard /
    bridge really writes tasks, so 'empty' is no longer an invariant). The check's
    only job is to prove this run did not change the store."""
    snap = {}
    for name in ("store/tasks.json", "store/approvals.json"):
        try:
            with open(os.path.join(BASE, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    snap["tool_calls"] = os.path.exists(
        os.path.join(BASE, "store", "tool_calls.json"))
    return snap


def main():
    store_before = _snapshot_store()
    # 1. files exist
    missing = [p for p in NEW_FILES if not os.path.exists(p)]
    check("voice files exist (4 voice modules + jarvis_voice + setup + 3 scripts)",
          not missing,
          f"total {len(NEW_FILES)} files" + (f"; missing: {missing}" if missing else ""))

    # 2. jarvis_voice.py — not a STUB, same public functions
    try:
        with open(os.path.join(CEO_CORE_DIR, "jarvis_voice.py"),
                  encoding="utf-8") as f:
            src = f.read()
        has_fns = all(f"def {fn}(" in src for fn in
                      ("listen", "speak", "handle_voice_command"))
        # The word "STUB" may stay in a docstring as history ("was"
        # STUB) — the real check: no STUB_NOTICE/NotImplementedError + REAL.
        no_stub = ("STUB_NOTICE" not in src
                   and "NotImplementedError" not in src
                   and "REAL" in src)
        delegates = "from voice.listen import" in src \
            and "from voice.speak import" in src
        check("jarvis_voice.py REAL (not a STUB, same 3 functions, delegate)",
              has_fns and no_stub and delegates,
              f"fns={has_fns}, no-STUB={no_stub}, delegate={delegates}")
    except Exception as e:  # noqa: BLE001
        check("jarvis_voice.py REAL (not a STUB, same 3 functions, delegate)",
              False, str(e))

    # 3. voice modules import OK
    try:
        import voice  # noqa: PLC0415
        import voice.listen  # noqa: PLC0415
        import voice.loop  # noqa: PLC0415
        import voice.speak  # noqa: PLC0415
        check("voice package import OK", True,
              f"VOICE_IDS={voice.VOICE_IDS}")
    except Exception as e:  # noqa: BLE001
        check("voice package import OK", False,
              f"{type(e).__name__}: {e}")

    # 4. top-level imports stdlib/repo-local only (lazy piper/vosk/...)
    forbidden = {"piper", "vosk", "sherpa_onnx", "sounddevice", "numpy"}
    bad = {}
    for path in (os.path.join(VOICE_DIR, "speak.py"),
                 os.path.join(VOICE_DIR, "listen.py"),
                 os.path.join(VOICE_DIR, "loop.py"),
                 os.path.join(VOICE_DIR, "__init__.py"),
                 os.path.join(CEO_CORE_DIR, "jarvis_voice.py")):
        try:
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception as e:  # noqa: BLE001
            bad[path] = str(e)
            continue
        found = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                found.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                found.add(node.module.split(".")[0])
        hit = found & forbidden
        if hit:
            bad[path] = sorted(hit)
    check("voice module top-level import stdlib-only (piper/vosk lazy)",
          not bad, f"problem: {bad}" if bad else "piper/vosk/sherpa only in functions")

    # 5-7. engine probes (importlib — not imported)
    for mod, label in (("piper", "piper-tts"),
                       ("vosk", "vosk"),
                       ("sherpa_onnx", "sherpa-onnx")):
        spec = importlib.util.find_spec(mod)
        if spec is not None:
            try:
                m = importlib.import_module(mod)
                ver = getattr(m, "__version__", "n/a")
            except Exception as e:  # noqa: BLE001
                ver = f"import error: {type(e).__name__}"
            check(f"{label} importable", True, f"version: {ver}")
        else:
            check(f"{label} importable", False,
                  f"run pip install {label} (VOICE-SETUP.md)")
    spec = importlib.util.find_spec("sounddevice")
    if spec is not None:
        try:
            import sounddevice  # noqa: PLC0415
            check("sounddevice importable (mic path)", True,
                  f"version: {getattr(sounddevice, '__version__', 'n/a')}")
        except OSError as e:
            check("sounddevice importable (mic path)", False,
                  "No PortAudio on this VM (no apt candidate) — "
                  "VM-only limit; the Windows wheel bundles PortAudio. "
                  f"({e})")
    else:
        check("sounddevice importable (mic path)", False,
              "run pip install sounddevice — the Windows wheel bundles PortAudio "
              "bundles it.")

    # 8. config voice block = VERIFIED ids + brain mock + phase 7
    try:
        with open(os.path.join(CEO_CORE_DIR, "config.json"),
                  encoding="utf-8") as f:
            cfg = json.load(f)
        v = cfg.get("voice", {})
        ok = (v.get("voices") == EXPECTED_VOICES
              and v.get("models", {}).get("vosk_en")
              == EXPECTED_MODELS["vosk_en"]
              and v.get("models", {}).get("sherpa_bn")
              == EXPECTED_MODELS["sherpa_bn"]
              and cfg.get("brain") == "mock"
              and cfg.get("phase") == 11
              and cfg.get("version") == "0.9.0")
        check("config voice block = VERIFIED ids + brain mock + phase 11",
              ok, f"voices={v.get('voices')}, brain={cfg.get('brain')}, "
              f"phase={cfg.get('phase')}, version={cfg.get('version')}")
    except Exception as e:  # noqa: BLE001
        check("config voice block = VERIFIED ids + brain mock + phase 11",
              False, str(e))

    # 9. no secrets in new files
    # (this check file itself excluded: the pattern literal + the word "secret" in docstrings
    # are always there — that is not a credential, it is the scanner's own word.)
    secret_re = re.compile(
        r"api[_-]?key|apikey|password|passwd|\bsecret\b|bearer|"
        r"sk-[A-Za-z0-9]{16,}", re.IGNORECASE)
    hits = {}
    for path in NEW_FILES:
        if os.path.abspath(path) == os.path.abspath(__file__):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if secret_re.search(line):
                        hits.setdefault(path, []).append(i)
        except FileNotFoundError:
            hits[path] = ["FILE MISSING"]
    check("no secrets in new files (key/password/secret/bearer)", not hits,
          f"found: {hits}" if hits else "clean")

    # 10. gate test — TEMP approvals path only
    try:
        with tempfile.TemporaryDirectory() as tmp:
            temp_appr = os.path.join(tmp, "approvals.json")
            from voice.loop import handle_voice_text  # noqa: PLC0415
            result = handle_voice_text(
                "please send the Day 4 batch", lang="en",
                approvals_path=temp_appr)
            with open(temp_appr, encoding="utf-8") as f:
                temp_data = json.load(f)
            recs = temp_data.get("records", [])
            gate_ok = (result.get("gated_action") == "send"
                       and result.get("approval_id")
                       and len(recs) == 1
                       and recs[0]["action"] == "send"
                       and recs[0]["status"] == "pending")
            check("gate test (TEMP): voice 'send' -> PENDING, never executes",
                  gate_ok,
                  f"gated={result.get('gated_action')}, "
                  f"approval={result.get('approval_id')}, "
                  f"temp records={len(recs)}")
    except Exception as e:  # noqa: BLE001
        check("gate test (TEMP): voice 'send' -> PENDING, never executes",
              False, f"{type(e).__name__}: {e}")

    # 11. voice_test.py subprocess (real synth + transcribe)
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(BASE, "scripts", "voice_test.py")],
            capture_output=True, text=True, timeout=900)
        tail = (proc.stdout or "").strip().splitlines()[-3:]
        check("scripts/voice_test.py PASS (real synth + transcribe)",
              proc.returncode == 0, " | ".join(tail))
    except subprocess.TimeoutExpired:
        check("scripts/voice_test.py PASS (real synth + transcribe)",
              False, "timeout 900s — the HF CDN may be slow")
    except Exception as e:  # noqa: BLE001
        check("scripts/voice_test.py PASS (real synth + transcribe)",
              False, str(e))

    # 12. real store unchanged by this check run (Phase 9: live queue)
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    # 13. check_phase0 still PASS
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(BASE, "scripts", "check_phase0.py")],
            capture_output=True, text=True, timeout=300)
        check("check_phase0 still PASS", proc.returncode == 0,
              f"exit={proc.returncode}")
    except Exception as e:  # noqa: BLE001
        check("check_phase0 still PASS", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} voice checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Voice self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
