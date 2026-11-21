#!/usr/bin/env python3
"""List skill proposals — read-only (A5, 2026-11-21).

Shows the DRAFT proposals in store/skill-proposals.json. Writes nothing,
installs nothing — building / installing a skill from a proposal only happens
on Boss's "ok" (skill_finder.py's rule).

Usage:
  python3 scripts/list_skill_proposals.py
  python3 scripts/list_skill_proposals.py --proposals-path /tmp/skill-proposals.json
  python3 scripts/list_skill_proposals.py --query backup

Stdlib only. No network, no send, no spend.
"""

import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROPOSALS_PATH = os.path.join(BASE, "store", "skill-proposals.json")


def load_proposals(path):
    """Read the proposal file — empty list if the file is missing (no
    proposal yet, not an error)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        proposals = data.get("proposals", []) if isinstance(data, dict) else []
        return list(proposals) if isinstance(proposals, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="List DRAFT skill proposals (read-only — nothing is "
                    "installed or written).")
    parser.add_argument("--proposals-path", default=DEFAULT_PROPOSALS_PATH,
                        help="proposals JSON path (default: store/skill-proposals.json)")
    parser.add_argument("--query", default=None,
                        help="only show proposals whose query contains this text")
    args = parser.parse_args(argv)

    proposals = load_proposals(args.proposals_path)
    if args.query:
        needle = args.query.lower()
        proposals = [p for p in proposals
                     if needle in str(p.get("query", "")).lower()
                     or needle in str(p.get("candidate_skill", "")).lower()]
    if not proposals:
        print("No skill proposals yet."
              if not args.query else f"No proposals matching {args.query!r}.")
        print("Propose one via Main CEO Bot: "
              "route_task({'type': 'find_skill', 'query': '...', "
              "'propose': True, ...}) — draft only, Boss's 'ok' needed "
              "before anything is installed.")
        return 0
    for i, proposal in enumerate(proposals, 1):
        print(f"{i}. [{proposal.get('status', 'proposed')}] "
              f"{proposal.get('candidate_skill', '?')} "
              f"from {proposal.get('candidate_repo', '?')}")
        print(f"   query: {proposal.get('query', '')} | "
              f"agent: {proposal.get('agent', '')}")
        print(f"   source: {proposal.get('source_url', '')} "
              f"({proposal.get('license', '')})")
        print(f"   fit: {proposal.get('fit_note', '')}")
    print(f"\n{len(proposals)} proposal(s) — DRAFT ONLY, nothing installed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
