"""Owner memory — quote-verified memory, owner-messages-only
(Improvement Phase 2, modelled on Nod's memory.ts).

Nod's pattern (~/workspace/nod-reverse/reverse-engineering.md,
memory.ts + memory-learning.ts):
  - Memory learns only from the owner's own messages — never from a tool result,
    web page, or email.
  - Every note carries a verbatim quote; the server verifies that the quote
    really is in the owner's message.
  - One private JSON doc (256 KiB cap), 5 areas (about / preferences /
    people / routines / lessons), each entry ≤ 4,000 chars, status
    tentative / observed / stated / archived.
  - Memory is context, NOT permission — something being written in memory
    never approves an action; approval lives only in trust_gate + ApprovalGateway.
  - All notes visible + editable: view / change / archive / forget
    — exported as Markdown.

In this file (Python, stdlib only, no network / live call):
  - OwnerMemory: learn / verify / get / list / edit / archive /
    forget / export_markdown.
  - learn() takes no entry without a quote: the quote must be verbatim in the
    source_message, otherwise ValueError (Nod: a note without a quote is not kept).
  - Seed: 3 entries — from Boss's recorded exact words (MEMORY.md
    2026-11-21 + human_approval_gateway.py), each with its quote +
    source_message. Seeding happens only when seed_defaults() is called — the module
    never writes to the store on its own.

Usage:
  mem = OwnerMemory()  # store/memory.json
  mem.seed_defaults()  # first time — 3 of Boss's words
  mem.learn("preferences", "reply-language", "Answer Boss in Bengali.",
            quote="তুমি এখন থেকে বাংলায় কথা বলবা",
            source_message="Boss (voice call 2026-11-21): তুমি এখন থেকে বাংলায় কথা বলবা",
            source_ref="MEMORY.md 2026-11-21")
  mem.verify("preferences", "reply-language")  # True — the quote still matches
  mem.export_markdown()  # store/MEMORY.md

Status: REAL (Improvement Phase 2, 2026-11-21) — runs on the mock brain.

Structure — DECIDED on merit (2026-11-21,
00-CEO-Core/MEMORY-STRUCTURE-DECISION-2026-11-21.md — Boss's rule:
decide on merit, not from analogy):
  - One drawer = one store file (store/memory.json) — one owner
    → one memory doc (Nod §4); not 79 files for 79 agents
    (bot-hq's per-bot files are for their separate Hermes homes; our
    agents are modules of one repo).
  - Separate boxes inside the drawer: "shared" (Boss's words — everyone reads)
    + each agent's own box (main_ceo_bot, chief_of_staff_agency,
    dept_sales / dept_marketing / dept_engineering / dept_operations /
    dept_strategy / dept_finance / dept_quality / dept_innovation,
    products, content, worker:<specialist-slug>).
  - Boss's words go only to the shared box (learn() takes no other box).
  - Agents' work notes go only to their own box (note_work()) —
    one box's note cannot be read by another box; no work note can be
    written to the shared box.
  - A work note carries no Boss quote — it is the agent's writing, not owner
    memory, not permission. verify() runs only on owner entries.
  - Old entries (without box/origin) migrate on load: box="shared",
    origin="owner" — text/quote/source stay unchanged.
  - Maintenance (Nod's repair, no-model): maintenance_repair() —
    archives tentative entries older than 60 days + duplicate archives.
    Reflect is proposal-only: validate_proposals() — candidates that pass
    quote-verify are "ready", the rest "rejected"; it writes nothing.
  - context_for(box) — a compact view to attach in CEO/Chief routing.
"""

import json
import os
import re
from datetime import datetime, timezone

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
DEFAULT_MEMORY_PATH = os.path.join(_STORE_DIR, "memory.json")
DEFAULT_EXPORT_PATH = os.path.join(_STORE_DIR, "MEMORY.md")

AREAS = ("about", "preferences", "people", "routines", "lessons")
STATUSES = ("tentative", "observed", "stated", "archived")
MAX_DOC_BYTES = 256 * 1024  # 256 KiB cap, like Nod's
MAX_ENTRY_CHARS = 4000
STALE_TENTATIVE_DAYS = 60  # Nod: a tentative entry unrepeated for 60 days is stale

# Drawer boxes — one drawer (store/memory.json), separate boxes inside.
# "shared": Boss's words — every agent reads them. The rest are one agent's
# own box each; a worker box is named "worker:<specialist-slug>".
# Phase 1 (Unified OS): "products" + "content" are the Digital Product
# and Content Creation departments' boxes, alongside the 8 agency dept
# boxes — 13 fixed boxes in total.
SHARED_BOX = "shared"
BOXES = (
    "shared",
    "main_ceo_bot",
    "chief_of_staff_agency",
    "dept_sales",
    "dept_marketing",
    "dept_engineering",
    "dept_operations",
    "dept_strategy",
    "dept_finance",
    "dept_quality",
    "dept_innovation",
    "products",
    "content",
)


def _is_valid_box(box):
    """A fixed box, or worker:<slug> — no other name."""
    if box in BOXES:
        return True
    if isinstance(box, str) and box.startswith("worker:"):
        slug = box[len("worker:"):]
        return bool(slug) and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", slug) is not None
    return False


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _normalize(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def quote_in_source(quote, source_message):
    """Whether the quote is verbatim in the source message. No empty quote."""
    q = _normalize(quote)
    if not q:
        return False
    return q in _normalize(source_message)


# Seed entries — Boss's recorded exact words (with verbatim quotes).
# Source: MEMORY.md 2026-11-21 + human_approval_gateway.py.
SEED_ENTRIES = [
    {
        "area": "about",
        "slug": "assistant-name",
        "text": "The assistant's name is Mira — Boss changed it permanently on 2026-11-21.",
        "quote": "Your name is Mira",
        "source_message": ("Boss (voice call, 2026-11-21 ~08:38 Dhaka): "
                           "'Basanti is not your name. Your name is Mira. "
                           "Permanently save your name is Mira.'"),
        "source_ref": "MEMORY.md 2026-11-21",
        "status": "stated",
    },
    {
        "area": "preferences",
        "slug": "reply-language",
        "text": "Boss must be answered in Bengali; client-facing copy in US English.",
        "quote": "তুমি এখন থেকে বাংলায় কথা বলবা",
        "source_message": ("Boss (voice call, 2026-11-21 ~08:36 Dhaka): "
                           "'তুমি এখন থেকে বাংলায় কথা বলবা'"),
        "source_ref": "MEMORY.md 2026-11-21",
        "status": "stated",
    },
    {
        "area": "routines",
        "slug": "gate-words",
        "text": ("Gate words: ok = plan/asset approval; post it = publish; "
                 "send = send; go = phase advance; upload it = video upload."),
        "quote": "post it",
        "source_message": ("Gate words (Boss's decision): ok = plan / finished "
                           "asset approval; post it = publish; upload it = "
                           "upload a video; send = send a message or email; "
                           "go = advance a build phase"),
        "source_ref": "00-CEO-Core/human_approval_gateway.py",
        "status": "stated",
    },
]


class OwnerMemory:
    """Memory learned from Boss's words — quote-verified, visible, editable."""

    def __init__(self, memory_path=None):
        self.memory_path = memory_path or DEFAULT_MEMORY_PATH
        self._load()

    def _load(self):
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.entries = data.get("entries", []) if isinstance(data, dict) else []
        except (FileNotFoundError, json.JSONDecodeError):
            self.entries = []
        # Drawer migration: an old entry without box/origin becomes
        # shared + owner — text/quote/source stay unchanged.
        for entry in self.entries:
            entry.setdefault("box", SHARED_BOX)
            entry.setdefault("origin", "owner")

    def migrate_legacy(self):
        """If entries without box/origin exist (in the file on disk), fill them
        in and save — the file is not touched if nothing changed. Run once on
        the real store. (_load() fills defaults in memory, so the real file on
        disk is read separately — otherwise migration would never save.)"""
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False
        raw_entries = raw.get("entries", []) if isinstance(raw, dict) else []
        needs = any("box" not in e or "origin" not in e
                    for e in raw_entries)
        needs = needs or "boxes" not in raw
        # Phase 1 (Unified OS): the stored boxes list must match BOXES —
        # a store written before the products/content boxes were added
        # is healed here (entries are untouched).
        needs = needs or raw.get("boxes") != list(BOXES)
        if needs:
            self._save()
            return True
        return False

    def _save(self):
        payload = {
            "schema": "owner-memory-v1",
            "note": ("Memory learns ONLY from the owner's own messages. "
                     "Every entry carries a verbatim quote + its source "
                     "message. Memory is context, NOT permission. "
                     "One drawer, separate boxes: 'shared' holds the "
                     "owner's words (readable by all); each agent box "
                     "holds only that agent's work notes."),
            "boxes": list(BOXES),
            "entries": self.entries,
        }
        encoded = json.dumps(payload, indent=2, ensure_ascii=False)
        if len(encoded.encode("utf-8")) > MAX_DOC_BYTES:
            raise ValueError(
                f"Memory doc would exceed the {MAX_DOC_BYTES // 1024} KiB cap — "
                "archive or forget old entries first.")
        parent = os.path.dirname(self.memory_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.memory_path, "w", encoding="utf-8") as f:
            f.write(encoded)

    def size_bytes(self):
        try:
            return os.path.getsize(self.memory_path)
        except OSError:
            return 0

    def seed_defaults(self):
        """3 seed entries (Boss's recorded words) — only in an empty memory."""
        self._load()  # Fresh from disk — another instance's write is not lost.
        if self.entries:
            return [dict(e) for e in self.entries]
        seeded = []
        for seed in SEED_ENTRIES:
            seeded.append(self.learn(
                seed["area"], seed["slug"], seed["text"], seed["quote"],
                seed["source_message"], source_ref=seed["source_ref"],
                status=seed["status"]))
        return seeded

    def learn(self, area, slug, text, quote, source_message,
              source_ref="", status="stated", box=SHARED_BOX):
        """A new entry from the owner's message. If the quote is not verbatim,
        ValueError — a note without a quote is not kept.
        Boss's words always go to the shared box — another box raises ValueError
        (Boss's words cannot be locked away in one agent's box)."""
        self._load()  # Fresh from disk — another instance's write is not lost.
        if box != SHARED_BOX:
            raise ValueError(
                "Owner entries always go to the shared box — an agent box "
                f"cannot hold the owner's words (got box={box!r}).")
        if area not in AREAS:
            raise ValueError(f"Unknown area {area!r}. Allowed: {list(AREAS)}")
        if status not in STATUSES:
            raise ValueError(f"Unknown status {status!r}. Allowed: {list(STATUSES)}")
        if not slug or not str(slug).strip():
            raise ValueError("slug must be a non-empty string.")
        if len(text or "") > MAX_ENTRY_CHARS:
            raise ValueError(
                f"Entry text exceeds {MAX_ENTRY_CHARS} chars.")
        if not quote_in_source(quote, source_message):
            raise ValueError(
                "Quote not found verbatim in the source message — "
                "memory learns only from the owner's own words.")
        if any(e["area"] == area and e["slug"] == slug
               and e.get("box", SHARED_BOX) == SHARED_BOX
               and e["status"] != "archived" for e in self.entries):
            raise ValueError(
                f"Entry {area}/{slug} already exists — edit it instead.")
        entry = {
            "area": area,
            "slug": slug,
            "box": SHARED_BOX,
            "origin": "owner",
            "text": text,
            "quote": _normalize(quote),
            "source_message": source_message,
            "source_ref": source_ref,
            "status": status,
            "learned_at": _now_iso(),
            "updated_at": _now_iso(),
        }
        self.entries.append(entry)
        self._save()
        return dict(entry)

    def note_work(self, box, slug, text, area="lessons", source_ref=""):
        """An agent's own work note — only in its own box.
        No Boss quote is needed (this is not owner memory), but:
          - box must be the agent's own box — not "shared",
            not an unknown box (ValueError).
          - The same (box, area, slug) cannot appear twice — edit it instead.
        The note carries origin="agent" — it is not Boss's words and
        is never treated as permission."""
        self._load()  # Fresh from disk — another instance's write is not lost.
        if not _is_valid_box(box):
            raise ValueError(f"Unknown memory box {box!r}.")
        if box == SHARED_BOX:
            raise ValueError(
                "Work notes cannot go in the shared box — the shared box "
                "holds only the owner's words.")
        if area not in AREAS:
            raise ValueError(f"Unknown area {area!r}. Allowed: {list(AREAS)}")
        if not slug or not str(slug).strip():
            raise ValueError("slug must be a non-empty string.")
        if len(text or "") > MAX_ENTRY_CHARS:
            raise ValueError(
                f"Entry text exceeds {MAX_ENTRY_CHARS} chars.")
        if any(e["area"] == area and e["slug"] == slug
               and e.get("box", SHARED_BOX) == box
               and e["status"] != "archived" for e in self.entries):
            raise ValueError(
                f"Work note {box}/{area}/{slug} already exists — edit it instead.")
        entry = {
            "area": area,
            "slug": slug,
            "box": box,
            "origin": "agent",
            "text": text,
            "quote": "",
            "source_message": "",
            "source_ref": source_ref,
            "status": "stated",
            "learned_at": _now_iso(),
            "updated_at": _now_iso(),
        }
        self.entries.append(entry)
        self._save()
        return dict(entry)

    def verify(self, area, slug, box=None):
        """Whether this entry's quote is still verbatim in its source message.
        An agent work note has no owner quote — verify() raises ValueError
        there (a work note is never verified as Boss's words)."""
        entry = self.get(area, slug, box=box)
        if entry.get("origin", "owner") != "owner":
            raise ValueError(
                "Agent work notes carry no owner quote — they cannot be "
                "quote-verified as the owner's words.")
        return quote_in_source(entry["quote"], entry["source_message"])

    def verify_all(self):
        """Verify all active OWNER entries — {area/slug: bool}. Agent work
        notes do not appear here (they have no quote)."""
        return {f"{e['area']}/{e['slug']}": self.verify(e["area"], e["slug"])
                for e in self.entries
                if e["status"] != "archived"
                and e.get("origin", "owner") == "owner"}

    def maintenance_repair(self, now=None):
        """Nod-style repair — no model, no live call.

        - A tentative entry older than 60 days (said once, never
          repeated) is archived. Stated/observed are never auto-archived
          (they are confirmed/learned).
        - If the same (box, area, slug) has two active entries, the later one
          is archived (duplicate).
        - Saves only if something changed. Returns: {"archived": [...],
          "deduped": [...]} — in "box:area/slug" form."""
        self._load()  # Fresh from disk — another instance's write is not lost.
        now_dt = now or datetime.now(timezone.utc)
        archived = []
        deduped = []
        first_active = {}
        for entry in list(self.entries):
            key = (entry.get("box", SHARED_BOX), entry["area"],
                   entry["slug"])
            if entry["status"] != "archived":
                if key in first_active:
                    entry["status"] = "archived"
                    entry["updated_at"] = _now_iso()
                    deduped.append(
                        f"{entry.get('box', SHARED_BOX)}:{entry['area']}/"
                        f"{entry['slug']}")
                    continue
                first_active[key] = entry
            if entry["status"] == "tentative":
                try:
                    learned = datetime.fromisoformat(
                        entry.get("learned_at", ""))
                except ValueError:
                    learned = None
                if learned is not None and learned.tzinfo is not None:
                    if (now_dt - learned).days > STALE_TENTATIVE_DAYS:
                        entry["status"] = "archived"
                        entry["updated_at"] = _now_iso()
                        archived.append(
                            f"{entry.get('box', SHARED_BOX)}:"
                            f"{entry['area']}/{entry['slug']}")
        if archived or deduped:
            self._save()
        return {"archived": archived, "deduped": deduped}

    def validate_proposals(self, candidates):
        """Reflect proposal — verification only, never written.

        Candidate: {"area", "slug", "text", "quote", "source_message",
        "source_ref"?} — a future live brain / Mira writes the proposal;
        the server only calls a candidate "ready" if it passes quote-verify.
        Returns: {"ready": [...], "rejected": [{"candidate": ..., "reason": ...}]}.
        Nothing changes in the store — learn() must be called to teach a ready candidate."""
        self._load()  # Fresh from disk — the duplicate check stays correct.
        ready = []
        rejected = []
        for cand in candidates or []:
            cand = dict(cand or {})
            area = cand.get("area")
            slug = cand.get("slug")
            reason = None
            if area not in AREAS:
                reason = f"Unknown area {area!r}."
            elif not slug or not str(slug).strip():
                reason = "slug must be a non-empty string."
            elif len(cand.get("text") or "") > MAX_ENTRY_CHARS:
                reason = f"Entry text exceeds {MAX_ENTRY_CHARS} chars."
            elif not quote_in_source(cand.get("quote"),
                                     cand.get("source_message")):
                reason = ("Quote not found verbatim in the source message — "
                          "memory learns only from the owner's own words.")
            elif any(e["area"] == area and e["slug"] == slug
                     and e.get("box", SHARED_BOX) == SHARED_BOX
                     and e["status"] != "archived" for e in self.entries):
                reason = (f"Entry {area}/{slug} already exists — "
                          "edit it instead.")
            if reason is not None:
                rejected.append({"candidate": cand, "reason": reason})
            else:
                ready.append({
                    "area": area,
                    "slug": slug,
                    "text": cand.get("text", ""),
                    "quote": _normalize(cand.get("quote")),
                    "source_message": cand.get("source_message", ""),
                    "source_ref": cand.get("source_ref", ""),
                })
        return {"ready": ready, "rejected": rejected}

    def context_for(self, box):
        """A compact view to attach in CEO/Chief routing: shared owner
        entries + this box's own notes. No source_message — to keep it
        small. Another box's notes do not appear here."""
        if not _is_valid_box(box):
            raise ValueError(f"Unknown memory box {box!r}.")

        def _brief(entry):
            return {
                "area": entry["area"],
                "slug": entry["slug"],
                "text": entry["text"],
                "status": entry["status"],
                "source_ref": entry.get("source_ref", ""),
            }

        shared = [_brief(e) for e in self.list_entries(include_archived=False)
                  if e.get("box", SHARED_BOX) == SHARED_BOX]
        own = [_brief(e) for e in self.list_own(box)]
        active = [e for e in self.entries if e["status"] != "archived"]
        return {
            "box": box,
            "shared": shared,
            "own": own,
            "counts": {"shared": len(shared), "own": len(own),
                       "total_active": len(active)},
        }

    def get(self, area, slug, box=None):
        """box=None: shared is searched first, then other boxes (for old
        callers). If a box is given, only that box is searched."""
        if box is not None:
            for entry in self.entries:
                if (entry["area"] == area and entry["slug"] == slug
                        and entry.get("box", SHARED_BOX) == box):
                    return dict(entry)
            raise KeyError(f"No memory entry {area}/{slug} in box {box!r}.")
        for entry in self.entries:
            if (entry["area"] == area and entry["slug"] == slug
                    and entry.get("box", SHARED_BOX) == SHARED_BOX):
                return dict(entry)
        for entry in self.entries:
            if entry["area"] == area and entry["slug"] == slug:
                return dict(entry)
        raise KeyError(f"No memory entry {area}/{slug}.")

    def list_entries(self, area=None, box=None, include_archived=False):
        """box=None: all entries (admin / export view).
        box=X: only shared + box X — i.e. what agent X can read.
        One box's work note never appears in another box's list."""
        out = []
        for entry in self.entries:
            if area is not None and entry["area"] != area:
                continue
            if entry["status"] == "archived" and not include_archived:
                continue
            if box is not None:
                entry_box = entry.get("box", SHARED_BOX)
                if entry_box != SHARED_BOX and entry_box != box:
                    continue
            out.append(dict(entry))
        return out

    def read_box(self, box):
        """One agent's read view: shared compartment + its own box.
        Another agent's box notes do not appear here."""
        if not _is_valid_box(box):
            raise ValueError(f"Unknown memory box {box!r}.")
        return self.list_entries(box=box)

    def list_own(self, box):
        """Only this box's own entries (without shared) — to check
        isolation."""
        if not _is_valid_box(box):
            raise ValueError(f"Unknown memory box {box!r}.")
        return [dict(e) for e in self.entries
                if e.get("box", SHARED_BOX) == box
                and e["status"] != "archived"]

    def search(self, query, box=None, include_archived=False):
        """Substring search over entries (Phase 1, Unified OS).

        Matches case-insensitively against text, quote, source_message,
        slug, and area. Box permission is enforced the same way as
        list_entries(): box=None searches everything (admin view);
        box=X searches only shared + box X — another box's work notes
        never appear in the results. An empty query matches nothing."""
        q = _normalize(query).lower()
        if not q:
            return []
        out = []
        for entry in self.list_entries(box=box,
                                       include_archived=include_archived):
            haystack = " ".join([
                entry.get("text", ""), entry.get("quote", ""),
                entry.get("source_message", ""), entry.get("slug", ""),
                entry.get("area", ""),
            ]).lower()
            if q in haystack:
                out.append(dict(entry))
        return out

    def edit(self, area, slug, new_text=None, quote=None,
             source_message=None, source_ref=None, status=None, box=None):
        """Change an entry. If the quote / source changes, the new quote must
        also verify — otherwise ValueError (memory cannot be changed with a
        wrong quote). Box rule: if a box is given, the entry must be in that
        box — changing another box's entry raises ValueError; without a box,
        an agent note cannot be changed (its own box must be named), but a
        shared entry can."""
        self._load()  # Fresh from disk — another instance's write is not lost.
        entry = self._find_for_write(area, slug, box)
        if entry.get("origin", "owner") == "agent":
            if box is None or box != entry.get("box", SHARED_BOX):
                raise ValueError(
                    "An agent work note can only be edited from its own "
                    f"box (entry box={entry.get('box')!r}, got box={box!r}).")
        elif box is not None and box != SHARED_BOX:
            raise ValueError(
                "The owner's shared entries cannot be edited from an agent "
                f"box (got box={box!r}).")
        if new_text is not None:
            if len(new_text) > MAX_ENTRY_CHARS:
                raise ValueError(f"Entry text exceeds {MAX_ENTRY_CHARS} chars.")
            entry["text"] = new_text
        if quote is not None or source_message is not None:
            new_quote = quote if quote is not None else entry["quote"]
            new_source = (source_message if source_message is not None
                          else entry["source_message"])
            if not quote_in_source(new_quote, new_source):
                raise ValueError(
                    "New quote not found verbatim in the source message.")
            entry["quote"] = _normalize(new_quote)
            entry["source_message"] = new_source
        if source_ref is not None:
            entry["source_ref"] = source_ref
        if status is not None:
            if status not in STATUSES:
                raise ValueError(f"Unknown status {status!r}.")
            entry["status"] = status
        entry["updated_at"] = _now_iso()
        self._save()
        return dict(entry)

    def archive(self, area, slug, box=None):
        return self.edit(area, slug, status="archived", box=box)

    def forget(self, area, slug, box=None):
        """Delete an entry (Boss's forget — it does not come back). The box rule
        is the same as edit()'s: another box's note cannot be deleted."""
        self._load()  # Fresh from disk — another instance's write is not lost.
        entry = self._find_for_write(area, slug, box)
        if entry.get("origin", "owner") == "agent":
            if box is None or box != entry.get("box", SHARED_BOX):
                raise ValueError(
                    "An agent work note can only be forgotten from its own "
                    f"box (entry box={entry.get('box')!r}, got box={box!r}).")
        elif box is not None and box != SHARED_BOX:
            raise ValueError(
                "The owner's shared entries cannot be forgotten from an "
                f"agent box (got box={box!r}).")
        self.entries.remove(entry)
        self._save()
        return dict(entry)

    def _find_for_write(self, area, slug, box):
        """Write-path lookup: if a box is given, the entry must be in that box.
        If the entry is in another box, ValueError (cross-box writing is refused);
        if it is nowhere, KeyError. box=None is the legacy lookup
        (shared first, then other boxes)."""
        if box is None:
            return self._find(area, slug)
        for entry in self.entries:
            if (entry["area"] == area and entry["slug"] == slug
                    and entry.get("box", SHARED_BOX) == box):
                return entry
        for entry in self.entries:
            if entry["area"] == area and entry["slug"] == slug:
                raise ValueError(
                    f"Entry {area}/{slug} belongs to box "
                    f"{entry.get('box', SHARED_BOX)!r}, not {box!r} — "
                    "another box's entry cannot be changed from here.")
        raise KeyError(f"No memory entry {area}/{slug} in box {box!r}.")

    def export_markdown(self, export_path=None):
        """Visible memory — Markdown by box (store/MEMORY.md).
        First the shared compartment (Boss's words — everyone reads), then
        each agent box's work notes (with the agent-note label)."""
        path = export_path or DEFAULT_EXPORT_PATH
        lines = [
            "# Owner Memory — Talvenor Master OS",
            "",
            "> Memory learns ONLY from Boss's own messages. Every entry "
            "carries its verbatim quote + source. Memory is context, "
            "NOT permission — it never authorizes an action.",
            "> One drawer, separate boxes: the shared compartment holds "
            "Boss's words (readable by every agent); each agent box holds "
            "only that agent's work notes.",
            "",
            "## Shared compartment — Boss's words (everyone reads)",
            "",
        ]
        shared = [e for e in self.list_entries(include_archived=False)
                  if e.get("box", SHARED_BOX) == SHARED_BOX]
        for area in AREAS:
            entries = [e for e in shared if e["area"] == area]
            if not entries:
                continue
            lines.append(f"### {area}")
            lines.append("")
            for entry in entries:
                lines.append(f"- **{entry['slug']}** ({entry['status']}): "
                             f"{entry['text']}")
                lines.append(f"  - Quote: \"{entry['quote']}\"")
                lines.append(f"  - Source: {entry['source_ref'] or '(no ref)'}")
            lines.append("")
        for box in BOXES:
            if box == SHARED_BOX:
                continue
            own = self.list_own(box)
            if not own:
                continue
            lines.append(f"## Box: {box} — only this agent's work notes")
            lines.append("")
            for entry in own:
                lines.append(f"- **{entry['slug']}** ({entry['area']}, "
                             f"{entry['status']}) [agent note — not Boss's words, "
                             f"not permission]: {entry['text']}")
            lines.append("")
        worker_boxes = sorted({e.get("box", SHARED_BOX) for e in self.entries
                               if e.get("box", SHARED_BOX).startswith("worker:")})
        for box in worker_boxes:
            own = self.list_own(box)
            if not own:
                continue
            lines.append(f"## Box: {box} — only this worker's work notes")
            lines.append("")
            for entry in own:
                lines.append(f"- **{entry['slug']}** ({entry['area']}, "
                             f"{entry['status']}) [agent note — not Boss's words, "
                             f"not permission]: {entry['text']}")
            lines.append("")
        text = "\n".join(lines)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def _find(self, area, slug, box=None):
        if box is not None:
            for entry in self.entries:
                if (entry["area"] == area and entry["slug"] == slug
                        and entry.get("box", SHARED_BOX) == box):
                    return entry
            raise KeyError(f"No memory entry {area}/{slug} in box {box!r}.")
        for entry in self.entries:
            if (entry["area"] == area and entry["slug"] == slug
                    and entry.get("box", SHARED_BOX) == SHARED_BOX):
                return entry
        for entry in self.entries:
            if entry["area"] == area and entry["slug"] == slug:
                return entry
        raise KeyError(f"No memory entry {area}/{slug}.")


if __name__ == "__main__":
    # Manual check: in a TEMP file, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_mem = os.path.join(tmp_dir, "memory-test.json")
    tmp_md = os.path.join(tmp_dir, "MEMORY-test.md")

    mem = OwnerMemory(memory_path=tmp_mem)
    seeded = mem.seed_defaults()
    assert len(seeded) == 3, seeded
    assert all(mem.verify(e["area"], e["slug"]) for e in seeded)

    # Nothing can be learned without a quote.
    try:
        mem.learn("preferences", "bad", "x", quote="Boss never said that",
                  source_message="Boss: today is off")
        raise SystemExit("FAIL: unverified quote was learned")
    except ValueError:
        pass

    # Learn -> verify -> edit (edit with a bad quote is refused) -> archive -> forget.
    e = mem.learn("routines", "test-rule", "Test rule.",
                  quote="test this",
                  source_message="Boss: test this, then say it",
                  source_ref="test")
    assert mem.verify("routines", "test-rule") is True
    try:
        mem.edit("routines", "test-rule", quote="invented words")
        raise SystemExit("FAIL: edit with a bad quote was allowed")
    except ValueError:
        pass
    mem.edit("routines", "test-rule", new_text="Test rule (edited).")
    assert mem.get("routines", "test-rule")["text"] == "Test rule (edited)."
    mem.archive("routines", "test-rule")
    assert mem.get("routines", "test-rule")["status"] == "archived"
    assert all(e["slug"] != "test-rule"
               for e in mem.list_entries(area="routines"))  # seed gate-words stays
    assert any(e["slug"] == "test-rule"
               for e in mem.list_entries(area="routines", include_archived=True))
    mem.forget("routines", "test-rule")
    try:
        mem.get("routines", "test-rule")
        raise SystemExit("FAIL: forgotten entry still present")
    except KeyError:
        pass

    out = mem.export_markdown(tmp_md)
    with open(out, encoding="utf-8") as f:
        md = f.read()
    assert "Mira" in md and "Bengali" in md and "post it" in md

    # Drawer: 3 seeds in the shared box; learn() takes no other box.
    assert all(e.get("box") == "shared" and e.get("origin") == "owner"
               for e in seeded)
    try:
        mem.learn("preferences", "bad-box", "x", quote="test this",
                  source_message="Boss: test this", box="dept_sales")
        raise SystemExit("FAIL: owner entry went to an agent box")
    except ValueError:
        pass

    # Work note: not to shared, not to an unknown box; to its own box.
    try:
        mem.note_work("shared", "n", "x")
        raise SystemExit("FAIL: work note went to the shared box")
    except ValueError:
        pass
    try:
        mem.note_work("no-such-box", "n", "x")
        raise SystemExit("FAIL: work note went to an unknown box")
    except ValueError:
        pass
    w = mem.note_work("dept_sales", "day-note", "Sales: 5 draft ready.",
                      area="lessons", source_ref="test")
    assert w["box"] == "dept_sales" and w["origin"] == "agent"
    assert w["slug"] == "day-note"
    # Isolation: Marketing cannot read Sales' note; Sales can.
    assert any(e["slug"] == "day-note" for e in mem.read_box("dept_sales"))
    assert all(e["slug"] != "day-note" for e in mem.read_box("dept_marketing"))
    assert all(e["slug"] != "day-note" for e in mem.list_own("dept_marketing"))
    # Shared can be read from every box.
    assert len(mem.read_box("dept_marketing")) == 3
    assert len(mem.read_box("worker:outreach-drafter")) == 3
    # An agent note is not verified; verify_all covers only the 3 owner entries.
    try:
        mem.verify("lessons", "day-note", box="dept_sales")
        raise SystemExit("FAIL: agent note was quote-verified")
    except ValueError:
        pass
    assert len(mem.verify_all()) == 3 and all(mem.verify_all().values())
    # Edit/forget from the wrong box is refused (day-note belongs only to Sales);
    # from its own box it works; a shared entry cannot be changed from an agent box.
    try:
        mem.edit("lessons", "day-note", new_text="x", box="dept_marketing")
        raise SystemExit("FAIL: wrong-box edit of a work note")
    except ValueError:
        pass
    try:
        mem.forget("lessons", "day-note", box="dept_marketing")
        raise SystemExit("FAIL: wrong-box forget of a work note")
    except ValueError:
        pass
    try:
        mem.edit("routines", "gate-words", new_text="x", box="dept_sales")
        raise SystemExit("FAIL: agent box edited a shared entry")
    except ValueError:
        pass
    mem.edit("lessons", "day-note", new_text="Sales: 6 draft ready.",
             box="dept_sales")
    assert mem.get("lessons", "day-note", box="dept_sales")["text"].startswith("Sales: 6")
    mem.note_work("dept_quality", "tmp-note", "Quality: tmp.",
                  area="lessons")
    mem.forget("lessons", "tmp-note", box="dept_quality")
    assert all(e["slug"] != "tmp-note" for e in mem.read_box("dept_quality"))
    # The same slug works in another box; not twice in the same box.
    mem.note_work("dept_marketing", "day-note", "Marketing: 2 caption ready.")
    try:
        mem.note_work("dept_sales", "day-note", "Again.")
        raise SystemExit("FAIL: duplicate work note in same box")
    except ValueError:
        pass
    out = mem.export_markdown(tmp_md)
    with open(out, encoding="utf-8") as f:
        md = f.read()
    assert "Shared compartment" in md and "Box: dept_sales" in md
    assert "Box: dept_marketing" in md and "agent note" in md

    # Maintenance repair: a tentative older than 70 days is archived;
    # a new tentative stays; stated is never auto-archived.
    old = mem.learn("lessons", "old-rule", "Old rule.",
                    quote="old words",
                    source_message="Boss: old words", status="tentative")
    assert old["status"] == "tentative"
    for e in mem.entries:
        if e["slug"] == "old-rule":
            e["learned_at"] = "2026-09-01T00:00:00+00:00"
    mem._save()
    rep = mem.maintenance_repair(
        now=datetime(2026, 11, 21, tzinfo=timezone.utc))
    assert any("old-rule" in s for s in rep["archived"]), rep
    assert mem.get("lessons", "old-rule")["status"] == "archived"
    assert mem.get("routines", "gate-words")["status"] == "stated"
    # If a duplicate (box, area, slug) exists, the later one is archived.
    mem.entries.append(dict(mem.entries[0], slug="dup-rule",
                            learned_at="2026-11-21T00:00:00+00:00"))
    mem.entries.append(dict(mem.entries[0], slug="dup-rule",
                            learned_at="2026-11-21T00:01:00+00:00"))
    mem._save()
    rep2 = mem.maintenance_repair(
        now=datetime(2026, 11, 21, tzinfo=timezone.utc))
    assert any("dup-rule" in s for s in rep2["deduped"]), rep2

    # validate_proposals: valid quote -> ready, bad quote -> rejected,
    # writes nothing.
    before = len(mem.list_entries())
    v = mem.validate_proposals([
        {"area": "preferences", "slug": "new-rule", "text": "New.",
         "quote": "new words", "source_message": "Boss: new words"},
        {"area": "preferences", "slug": "bad-rule", "text": "Bad.",
         "quote": "invented", "source_message": "Boss: other words"},
    ])
    assert len(v["ready"]) == 1 and len(v["rejected"]) == 1, v
    assert len(mem.list_entries()) == before  # nothing was written

    # context_for: 3 seeds in shared, no source_message.
    ctx = mem.context_for("main_ceo_bot")
    assert ctx["box"] == "main_ceo_bot"
    assert {"assistant-name", "reply-language", "gate-words"} <= {
        e["slug"] for e in ctx["shared"]}
    assert all("source_message" not in e for e in ctx["shared"])
    assert ctx["counts"]["shared"] == len(ctx["shared"])
    print("owner_memory: OK (seed 3 quote-verified, bad quote rejected, "
          "edit/archive/forget, markdown export, drawer boxes + isolation, "
          "maintenance repair, proposal validation, context_for)")
