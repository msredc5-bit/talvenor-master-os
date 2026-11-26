#!/usr/bin/env python3
"""FOUNDER OS environment checker — Boss-side checks C1-C5 (F1).

Double-click check_pc_env.bat (repo root) to run this. It CHECKS ONLY:
it installs nothing, changes nothing, and never sends anything.

Checks:
  C1 Git installed?        (needed only for clone-based updates; the ZIP
                            workflow works without Git)
  C2 Node.js version       (needed only for the n8n step, F9/M12 — not F1)
  C3 Antigravity installed? (dev-environment option only — not F1)
  C4 n8n installed?        (not installed is EXPECTED in F1; install is
                            a Boss-PC step in F9/M12)
  C5 Voice models present? (models live in 00-CEO-Core/voice/models/;
                            install is a Boss-PC step, not needed for F1)

Results are written to pc-env-check.txt (repo root) and opened in
Notepad by the .bat. Missing tools are FINDINGS, not failures — this
script exits 0 whenever it ran to completion.

Stdlib only. Works on Windows and on this VM (for testing the logic).
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FILE = os.path.join(REPO_ROOT, "pc-env-check.txt")

# Voice-model sentinel files (relative to the repo root). Sources and
# download commands: 00-CEO-Core/VOICE-SETUP.md.
VOICE_MODELS = [
    ("Piper Bengali voice (bn_BD-google-medium)",
     os.path.join("00-CEO-Core", "voice", "models", "piper",
                  "bn_BD-google-medium.onnx")),
    ("Piper English voice (en_US-lessac-medium)",
     os.path.join("00-CEO-Core", "voice", "models", "piper",
                  "en_US-lessac-medium.onnx")),
    ("Vosk English model (vosk-model-small-en-us-0.15)",
     os.path.join("00-CEO-Core", "voice", "models", "vosk",
                  "vosk-model-small-en-us-0.15", "am", "final.mdl")),
    ("Sherpa Bengali encoder (vosk-model-small-streaming-bn)",
     os.path.join("00-CEO-Core", "voice", "models", "sherpa-bn",
                  "am-onnx", "encoder.onnx")),
    ("Sherpa Bengali tokens (vosk-model-small-streaming-bn)",
     os.path.join("00-CEO-Core", "voice", "models", "sherpa-bn",
                  "lang", "tokens.txt")),
]

# Antigravity install locations on Windows (checked only when the
# matching env var exists; on this VM they are absent, which is fine).
ANTIGRAVITY_PATHS = [
    os.path.join(os.environ.get("LOCALAPPDATA", ""),
                 "Programs", "Antigravity", "antigravity.exe"),
    os.path.join(os.environ.get("PROGRAMFILES", ""),
                 "Antigravity", "antigravity.exe"),
    os.path.join(os.environ.get("PROGRAMFILES(X86)", ""),
                 "Antigravity", "antigravity.exe"),
]


def _run_version(cmd):
    """Run `cmd --version` briefly; return the first line, or None."""
    try:
        proc = subprocess.run([cmd, "--version"], capture_output=True,
                              text=True, timeout=15)
        out = (proc.stdout or proc.stderr or "").strip().splitlines()
        return out[0].strip() if out else None
    except Exception:  # noqa: BLE001 - any failure means "not usable"
        return None


def _which(cmd):
    """shutil.which, but never raises."""
    try:
        return shutil.which(cmd)
    except Exception:  # noqa: BLE001
        return None


def main():
    lines = []
    lines.append("FOUNDER OS — environment check (F1, C1-C5)")
    lines.append("Checks only — nothing was installed or changed.")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Repo folder: {REPO_ROOT}")
    lines.append(f"Python: {sys.version.split()[0]}")
    lines.append("")

    # C1 — Git.
    git = _which("git")
    if git:
        ver = _run_version("git")
        lines.append(f"C1 Git: FOUND ({ver or 'version unknown'}) — {git}")
    else:
        lines.append("C1 Git: NOT FOUND (ZIP workflow works without Git; "
                     "Git is needed only for clone-based updates)")

    # C2 — Node.js (+ npm).
    node = _which("node")
    if node:
        ver = _run_version("node")
        npm = _which("npm")
        npm_ver = _run_version("npm") if npm else None
        lines.append(f"C2 Node.js: FOUND ({ver or 'version unknown'})"
                     + (f", npm {npm_ver}" if npm_ver else ", npm not found")
                     + f" — {node}")
    else:
        lines.append("C2 Node.js: NOT FOUND (needed only for the n8n step, "
                     "F9/M12 — not needed for F1)")

    # C3 — Antigravity.
    ag = _which("antigravity")
    ag_path = None
    if not ag:
        for cand in ANTIGRAVITY_PATHS:
            if cand and os.path.isfile(cand):
                ag_path = cand
                break
    if ag:
        lines.append(f"C3 Antigravity: FOUND on PATH — {ag}")
    elif ag_path:
        lines.append(f"C3 Antigravity: FOUND — {ag_path}")
    else:
        lines.append("C3 Antigravity: NOT FOUND (dev-environment option "
                     "only — not needed for F1; if it is installed, check "
                     "Settings > Apps and tell Mira)")

    # C4 — n8n.
    n8n = _which("n8n")
    if n8n:
        ver = _run_version("n8n")
        lines.append(f"C4 n8n: FOUND ({ver or 'version unknown'}) — {n8n}")
    else:
        lines.append("C4 n8n: NOT FOUND (expected in F1 — install is a "
                     "Boss-PC step in F9/M12)")

    # C5 — Voice models.
    lines.append("C5 Voice models:")
    present = 0
    for label, rel in VOICE_MODELS:
        full = os.path.join(REPO_ROOT, rel)
        ok = os.path.isfile(full)
        present += 1 if ok else 0
        lines.append(f"  [{'PRESENT' if ok else 'MISSING'}] {label}")
    if present == len(VOICE_MODELS):
        lines.append("  C5 result: ALL voice models present.")
    elif present == 0:
        lines.append("  C5 result: NO voice models present (expected in F1 "
                     "— install is a Boss-PC step; sources and commands: "
                     "00-CEO-Core/VOICE-SETUP.md).")
    else:
        lines.append(f"  C5 result: {present}/{len(VOICE_MODELS)} present "
                     "(partial — install is a Boss-PC step; sources and "
                     "commands: 00-CEO-Core/VOICE-SETUP.md).")

    lines.append("")
    lines.append("Done. Send this file (or a screenshot of it) to Mira.")
    text = "\n".join(lines) + "\n"
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
