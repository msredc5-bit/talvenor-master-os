#!/usr/bin/env python3
"""upload_youtube.py — YouTube upload script (stage 9-upload).

SCRIPT ONLY — DEFAULT OFF. This file is never run by the Chief, the
agents, or any cron. Uploading needs ALL THREE, every run:
  1. Boss's exact gate word: --gate-word "upload it"
  2. YOUTUBE_UPLOAD_ENABLED=1 in the environment
  3. Boss's OWN YouTube OAuth credential files (--client-secrets +
     --token) on the machine that runs it

Anything missing -> the script refuses and exits 2, uploading nothing.
Even with all three, the actual upload needs the Google API client
library (googleapiclient) installed on Boss's own machine — this VM has
no YouTube credential and no upload client, so the script refuses here
with instructions instead of pretending to upload. Execution +
verification stay BLOCKED (pipeline.md stage 9-upload; channel
@ToolPilotai69, account sojibprodhan99@gmail.com).

    python3 upload_youtube.py --video video.mp4 --title "..." \\
        --gate-word "upload it" \\
        --client-secrets /path/to/client_secrets.json \\
        --token /path/to/token.json
    python3 upload_youtube.py --self-test   # gate refusals only, no upload

Stdlib only — the Google client is imported lazily, only after the
gates pass, so importing this file never touches the network.
"""

import argparse
import os
import sys

GATE_WORD = "upload it"
ENABLE_ENV = "YOUTUBE_UPLOAD_ENABLED"


def check_gates(gate_word, env=None):
    """Return (ok, reason). All three gates are checked; the first
    failure is the reason — nothing is uploaded on any failure."""
    env = os.environ if env is None else env
    if env.get(ENABLE_ENV) != "1":
        return False, (f"{ENABLE_ENV} is not '1' — upload stage 9 is OFF "
                       "by default. Set YOUTUBE_UPLOAD_ENABLED=1 to enable.")
    if gate_word != GATE_WORD:
        return False, ("gate word missing or wrong — Boss's exact word "
                       "'upload it' is required (--gate-word \"upload it\").")
    return True, ""


def check_files(video, client_secrets, token):
    """Video + Boss's own credential files must exist on disk."""
    missing = []
    for label, path in (("video", video),
                        ("client_secrets", client_secrets),
                        ("token", token)):
        if not path or not os.path.isfile(path):
            missing.append(f"{label}: {path or '(not given)'}")
    if missing:
        return False, ("missing files — " + "; ".join(missing)
                       + ". Credentials are Boss's own OAuth files; "
                         "this system never creates or stores them.")
    return True, ""


def self_test():
    """Gate refusals only — no upload, no network, no files written."""
    cases = [
        ("env off + no gate word", {}, None, False),
        ("env off + right gate word", {}, GATE_WORD, False),
        ("env on + wrong gate word", {ENABLE_ENV: "1"}, "post it", False),
        ("env on + right gate word", {ENABLE_ENV: "1"}, GATE_WORD, True),
    ]
    bad = []
    for label, env, word, want in cases:
        ok, _reason = check_gates(word, env=env)
        good = ok == want
        print(f"  [{'PASS' if good else 'FAIL'}] {label} -> "
              f"{'allowed' if ok else 'refused'}")
        if not good:
            bad.append(label)
    ok_files, _ = check_files("/nonexistent.mp4", None, None)
    print(f"  [{'PASS' if not ok_files else 'FAIL'}] missing video/creds -> refused")
    if ok_files:
        bad.append("missing files")
    print(f"\n  {len(cases) + 1 - len(bad)}/{len(cases) + 1} gate checks pass.")
    return 1 if bad else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Upload a video to YouTube (stage 9 — DEFAULT OFF).")
    parser.add_argument("--video", help="video file to upload")
    parser.add_argument("--title", help="video title")
    parser.add_argument("--description", default="", help="video description")
    parser.add_argument("--gate-word", default="",
                        help='Boss\'s exact gate word: "upload it"')
    parser.add_argument("--client-secrets",
                        help="Boss's own OAuth client_secrets.json")
    parser.add_argument("--token", help="Boss's own OAuth token.json")
    parser.add_argument("--self-test", action="store_true",
                        help="gate refusals only — no upload")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    ok, reason = check_gates(args.gate_word)
    if not ok:
        print(f"REFUSED — upload not run. {reason}", file=sys.stderr)
        return 2
    ok, reason = check_files(args.video, args.client_secrets, args.token)
    if not ok:
        print(f"REFUSED — upload not run. {reason}", file=sys.stderr)
        return 2
    if not args.title:
        print("REFUSED — upload not run. --title is required.",
              file=sys.stderr)
        return 2
    try:
        from googleapiclient.discovery import build  # noqa: F401  (lazy)
        from googleapiclient.http import MediaFileUpload  # noqa: F401
    except ImportError:
        print("REFUSED — upload not run. The Google API client library "
              "(googleapiclient) is not installed on this machine. Install "
              "it on Boss's own machine with his own credentials and run "
              "this script there — nothing was uploaded.",
              file=sys.stderr)
        return 2
    # Gates passed, files present, client library present. The resumable
    # upload itself is Boss's manual step on his own machine — this
    # script stops here by design (execution stays BLOCKED until Boss
    # runs it himself with his own credential).
    print("Gates passed, but this script does not execute uploads from "
          "the Master OS — upload is Boss's manual step on his own "
          "machine (pipeline.md stage 9-upload, BLOCKED). Nothing was "
          "uploaded.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
