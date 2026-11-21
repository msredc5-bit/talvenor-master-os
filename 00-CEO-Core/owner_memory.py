"""Owner memory — quote-verified memory, owner-messages-only
(Improvement Phase 2, Nod memory.ts-এর আদলে).

Nod-এর pattern (~/workspace/nod-reverse/reverse-engineering.md,
memory.ts + memory-learning.ts):
  - Memory শুধু owner-এর নিজের message থেকে শেখে — কখনো tool result,
    web page, বা email থেকে নয়।
  - প্রতিটা note-এর একটা verbatim quote থাকে; server সেই quote-টা
    owner-এর message-এ সত্যিই আছে কি না যাচাই করে রাখে।
  - একটা private JSON doc (256 KiB cap), ৫টা area (about / preferences /
    people / routines / lessons), প্রতিটা entry ≤ 4,000 chars, status
    tentative / observed / stated / archived।
  - Memory context, NOT permission — memory-তে লেখা থাকলেই কোনো কাজের
    অনুমোদন হয় না; অনুমোদন শুধু trust_gate + ApprovalGateway-এ।
  - সব note visible + editable: দেখা / বদলানো / archive / ভুলে যাওয়া
    (forget) — export Markdown-এ।

এই ফাইলে (Python, stdlib only, কোনো network / live call নেই):
  - OwnerMemory: learn / verify / get / list / edit / archive /
    forget / export_markdown।
  - learn() quote ছাড়া entry নেয় না: quote-টা source_message-এ
    verbatim থাকতেই হবে, নইলে ValueError (Nod: quote না থাকলে note
    রাখা হয় না)।
  - Seed: ৩টা entry — Boss-এর রেকর্ড করা সঠিক কথা থেকে (MEMORY.md
    2026-11-21 + human_approval_gateway.py), প্রতিটার quote +
    source_message সহ। Seed শুধু seed_defaults() ডাকলে হয় — module
    নিজে থেকে store-এ কিছু লেখে না।

ব্যবহার:
  mem = OwnerMemory()  # store/memory.json
  mem.seed_defaults()  # প্রথমবার — ৩টা Boss-এর কথা
  mem.learn("preferences", "reply-language", "Boss-কে বাংলায় উত্তর দাও।",
            quote="তুমি এখন থেকে বাংলায় কথা বলবা",
            source_message="Boss (voice call 2026-11-21): তুমি এখন থেকে বাংলায় কথা বলবা",
            source_ref="MEMORY.md 2026-11-21")
  mem.verify("preferences", "reply-language")  # True — quote এখনো মেলে
  mem.export_markdown()  # store/MEMORY.md

Status: REAL (Improvement Phase 2, 2026-11-21) — mock brain-এ চলে।

Structure — DECIDED on merit (2026-11-21,
00-CEO-Core/MEMORY-STRUCTURE-DECISION-2026-11-21.md — Boss-এর rule:
analogy থেকে নয়, merit-এ decide):
  - একটাই drawer = একটাই store file (store/memory.json) — একজন owner
    → একটাই memory doc (Nod §4); ৭৯ agent-এর জন্য ৭৯টা file নয়
    (bot-hq-র per-bot file ওদের আলাদা Hermes home-এর জন্য, আমাদের
    agent-রা এক repo-র module)।
  - Drawer-এর ভেতরে আলাদা box: "shared" (Boss-এর কথা — সবাই পড়ে)
    + প্রত্যেক agent-এর নিজের box (main_ceo_bot, chief_of_staff_agency,
    dept_sales / dept_marketing / dept_engineering / dept_operations /
    dept_strategy / dept_finance / dept_quality / dept_innovation,
    worker:<specialist-slug>)।
  - Boss-এর কথা শুধু shared box-এ যায় (learn() অন্য box নেয় না)।
  - Agent-দের কাজের note শুধু তাদের নিজের box-এ যায় (note_work()) —
    এক box-এর note অন্য box পড়তে পারে না; shared box-এ কাজের note
    লেখা যায় না।
  - Work note-এ Boss-এর quote থাকে না — এটা agent-এর লেখা, owner
    memory নয়, permission নয়। verify() শুধু owner entry-তে চলে।
  - পুরোনো entry (box/origin ছাড়া) load-এ migrate হয়: box="shared",
    origin="owner" — text/quote/source অপরিবর্তিত থাকে।
  - Maintenance (Nod-এর repair, no-model): maintenance_repair() —
    ৬০ দিনের বেশি পুরোনো tentative entry archive + duplicate archive।
    Reflect শুধু proposal: validate_proposals() — quote-verify পাস
    করা candidate "ready", বাকি "rejected"; কিছু লেখে না।
  - context_for(box) — CEO/Chief routing-এ attach করার compact view।
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
MAX_DOC_BYTES = 256 * 1024  # Nod-এর মতো 256 KiB cap
MAX_ENTRY_CHARS = 4000
STALE_TENTATIVE_DAYS = 60  # Nod: ৬০ দিন unrepeated tentative entry stale

# Drawer boxes — একটাই drawer (store/memory.json), ভেতরে আলাদা box।
# "shared": Boss-এর কথা — প্রত্যেক agent পড়ে। বাকিগুলো একেক agent-এর
# নিজের box; worker box-এর নাম "worker:<specialist-slug>"।
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
)


def _is_valid_box(box):
    """Fixed box, বা worker:<slug> — অন্য নাম নয়।"""
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
    """Quote-টা source message-এ verbatim আছে কি না। খালি quote নয়।"""
    q = _normalize(quote)
    if not q:
        return False
    return q in _normalize(source_message)


# Seed entries — Boss-এর রেকর্ড করা সঠিক কথা (verbatim quote সহ)।
# Source: MEMORY.md 2026-11-21 + human_approval_gateway.py।
SEED_ENTRIES = [
    {
        "area": "about",
        "slug": "assistant-name",
        "text": "Assistant-এর নাম Mira — Boss 2026-11-21-এ স্থায়ীভাবে বদলেছেন।",
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
        "text": "Boss-কে বাংলায় উত্তর দিতে হবে; client-facing copy US English।",
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
                 "send = send; go = phase advance; upload it = video upload।"),
        "quote": "post it",
        "source_message": ("Gate words (Boss-এর সিদ্ধান্ত): ok = plan / finished "
                           "asset approval; post it = publish; upload it = "
                           "upload a video; send = send a message or email; "
                           "go = advance a build phase"),
        "source_ref": "00-CEO-Core/human_approval_gateway.py",
        "status": "stated",
    },
]


class OwnerMemory:
    """Boss-এর কথা থেকে শেখা memory — quote-verified, visible, editable।"""

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
        # Drawer migration: box/origin ছাড়া পুরোনো entry shared + owner
        # হয় — text/quote/source অপরিবর্তিত থাকে।
        for entry in self.entries:
            entry.setdefault("box", SHARED_BOX)
            entry.setdefault("origin", "owner")

    def migrate_legacy(self):
        """box/origin ছাড়া entry থাকলে (disk-এর file-এ) ভরে save করে —
        বদল না থাকলে file ছোঁয়া হয় না। আসল store-এ একবারই চালাতে হয়।
        (_load() memory-তে default ভরে দেয়, তাই disk-এর আসল file-টা
        আলাদা করে পড়ে দেখা হয় — নইলে migration কখনো save করত না।)"""
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False
        raw_entries = raw.get("entries", []) if isinstance(raw, dict) else []
        needs = any("box" not in e or "origin" not in e
                    for e in raw_entries)
        needs = needs or "boxes" not in raw
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
        """৩টা seed entry (Boss-এর রেকর্ড করা কথা) — শুধু খালি memory-তে।"""
        self._load()  # Disk থেকে fresh — অন্য instance-এর লেখা হারায় না।
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
        """Owner-এর message থেকে নতুন entry। Quote verbatim না থাকলে
        ValueError — quote ছাড়া note রাখা হয় না।
        Boss-এর কথা সবসময় shared box-এ যায় — অন্য box দিলে ValueError
        (এক agent-এর box-এ Boss-এর কথা আটকে রাখা যায় না)।"""
        self._load()  # Disk থেকে fresh — অন্য instance-এর লেখা হারায় না।
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
        """Agent-এর নিজের কাজের note — শুধু তার নিজের box-এ।
        Boss-এর quote লাগে না (এটা owner memory নয়), তবে:
          - box অবশ্যই agent-এর নিজের box হতে হবে — "shared" নয়,
            অচেনা box নয় (ValueError)।
          - একই (box, area, slug) দুবার নয় — edit করতে হবে।
        Note-এ origin="agent" লেখা থাকে — এটা Boss-এর কথা নয়,
        কখনো permission হিসেবে গণ্য হয় না।"""
        self._load()  # Disk থেকে fresh — অন্য instance-এর লেখা হারায় না।
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
        """এই entry-র quote এখনো তার source message-এ verbatim আছে কি না।
        Agent work note-এর কোনো owner quote নেই — verify() সেখানে
        ValueError (কাজের note কখনো Boss-এর কথা হিসেবে verify হয় না)।"""
        entry = self.get(area, slug, box=box)
        if entry.get("origin", "owner") != "owner":
            raise ValueError(
                "Agent work notes carry no owner quote — they cannot be "
                "quote-verified as the owner's words.")
        return quote_in_source(entry["quote"], entry["source_message"])

    def verify_all(self):
        """সব active OWNER entry verify — {area/slug: bool}। Agent work
        note এখানে আসে না (তাদের quote নেই)।"""
        return {f"{e['area']}/{e['slug']}": self.verify(e["area"], e["slug"])
                for e in self.entries
                if e["status"] != "archived"
                and e.get("origin", "owner") == "owner"}

    def maintenance_repair(self, now=None):
        """Nod-style repair — কোনো model নয়, কোনো live call নয়।

        - ৬০ দিনের বেশি পুরোনো tentative entry (একবার বলা, আর repeat
          হয়নি) archive হয়। Stated/observed কখনো auto-archive হয় না
          (ওগুলো confirmed/learned)।
        - একই (box, area, slug)-এর দুটো active entry থাকলে পরেরটা
          archive হয় (duplicate)।
        - কিছু বদলালে তবেই save হয়। ফেরত: {"archived": [...],
          "deduped": [...]} — "box:area/slug" আকারে।"""
        self._load()  # Disk থেকে fresh — অন্য instance-এর লেখা হারায় না।
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
        """Reflect proposal — শুধু যাচাই, কখনো লেখা নয়।

        Candidate: {"area", "slug", "text", "quote", "source_message",
        "source_ref"?} — proposal লেখে ভবিষ্যৎ live brain / Mira;
        server শুধু quote-verify পাস করা candidate-ই "ready" বলে।
        ফেরত: {"ready": [...], "rejected": [{"candidate": ..., "reason": ...}]}।
        Store-এ কিছু বদলায় না — ready candidate শেখাতে learn() ডাকতে হয়।"""
        self._load()  # Disk থেকে fresh — duplicate check সঠিক থাকে।
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
        """CEO/Chief routing-এ attach করার compact view: shared owner
        entry + এই box-এর নিজের note। source_message নেই — ছোট রাখার
        জন্য। অন্য box-এর note এখানে আসে না।"""
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
        """box=None: shared-এ আগে খোঁজা হয়, তারপর অন্য box (পুরোনো
        caller-দের জন্য)। box দিলে শুধু সেই box-এই খোঁজা হয়।"""
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
        """box=None: সব entry (admin / export view)।
        box=X: শুধু shared + X box — অর্থাৎ X agent যা পড়তে পারে।
        এক box-এর কাজের note অন্য box-এর list-এ কখনো আসে না।"""
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
        """এক agent-এর পড়ার view: shared compartment + নিজের box।
        অন্য agent-এর box-এর note এখানে আসে না।"""
        if not _is_valid_box(box):
            raise ValueError(f"Unknown memory box {box!r}.")
        return self.list_entries(box=box)

    def list_own(self, box):
        """শুধু এই box-এর নিজের entry (shared ছাড়া) — isolation
        যাচাইয়ের জন্য।"""
        if not _is_valid_box(box):
            raise ValueError(f"Unknown memory box {box!r}.")
        return [dict(e) for e in self.entries
                if e.get("box", SHARED_BOX) == box
                and e["status"] != "archived"]

    def edit(self, area, slug, new_text=None, quote=None,
             source_message=None, source_ref=None, status=None, box=None):
        """Entry বদলানো। Quote / source বদলালে নতুন quote-ও verify হতে
        হবে — নইলে ValueError (ভুল quote দিয়ে memory বদলানো যায় না)।
        Box নিয়ম: box দিলে entry সেই box-এই থাকতে হবে — অন্য box-এর
        entry বদলাতে গেলে ValueError; box না দিলে agent note বদলানো
        যায় না (নিজের box বলতে হবে), shared entry বদলানো যায়।"""
        self._load()  # Disk থেকে fresh — অন্য instance-এর লেখা হারায় না।
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
        """Entry মুছে ফেলা (Boss-এর forget — ফেরত আসে না)। Box নিয়ম
        edit()-এর মতোই: অন্য box-এর note মোছা যায় না।"""
        self._load()  # Disk থেকে fresh — অন্য instance-এর লেখা হারায় না।
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
        """Write-path lookup: box দিলে entry সেই box-এই থাকতে হবে।
        Entry অন্য box-এ থাকলে ValueError (cross-box লেখা বারণ);
        কোথাও না থাকলে KeyError। box=None হলে legacy lookup
        (shared আগে, তারপর অন্য box)।"""
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
        """Visible memory — box অনুযায়ী Markdown (store/MEMORY.md)।
        প্রথমে shared compartment (Boss-এর কথা — সবাই পড়ে), তারপর
        প্রত্যেক agent box-এর কাজের note (agent note লেবেল সহ)।"""
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
            "## Shared compartment — Boss-এর কথা (সবাই পড়ে)",
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
            lines.append(f"## Box: {box} — শুধু এই agent-এর কাজের note")
            lines.append("")
            for entry in own:
                lines.append(f"- **{entry['slug']}** ({entry['area']}, "
                             f"{entry['status']}) [agent note — Boss-এর কথা "
                             f"নয়, permission নয়]: {entry['text']}")
            lines.append("")
        worker_boxes = sorted({e.get("box", SHARED_BOX) for e in self.entries
                               if e.get("box", SHARED_BOX).startswith("worker:")})
        for box in worker_boxes:
            own = self.list_own(box)
            if not own:
                continue
            lines.append(f"## Box: {box} — শুধু এই worker-এর কাজের note")
            lines.append("")
            for entry in own:
                lines.append(f"- **{entry['slug']}** ({entry['area']}, "
                             f"{entry['status']}) [agent note — Boss-এর কথা "
                             f"নয়, permission নয়]: {entry['text']}")
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
    # হাতে চেক: TEMP file-এ, আসল store ছোঁয়া হয় না।
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_mem = os.path.join(tmp_dir, "memory-test.json")
    tmp_md = os.path.join(tmp_dir, "MEMORY-test.md")

    mem = OwnerMemory(memory_path=tmp_mem)
    seeded = mem.seed_defaults()
    assert len(seeded) == 3, seeded
    assert all(mem.verify(e["area"], e["slug"]) for e in seeded)

    # Quote ছাড়া শেখা যায় না।
    try:
        mem.learn("preferences", "bad", "x", quote="Boss কখনো বলেনি",
                  source_message="Boss: আজ ছুটি")
        raise SystemExit("FAIL: unverified quote was learned")
    except ValueError:
        pass

    # শেখা -> verify -> edit (ভুল quote-এ edit বারণ) -> archive -> forget।
    e = mem.learn("routines", "test-rule", "Test rule.",
                  quote="test করো",
                  source_message="Boss: test করো, তারপর বলো",
                  source_ref="test")
    assert mem.verify("routines", "test-rule") is True
    try:
        mem.edit("routines", "test-rule", quote="বানানো কথা")
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
    assert "Mira" in md and "বাংলায়" in md and "post it" in md

    # Drawer: shared box-এ ৩ seed; learn() অন্য box নেয় না।
    assert all(e.get("box") == "shared" and e.get("origin") == "owner"
               for e in seeded)
    try:
        mem.learn("preferences", "bad-box", "x", quote="test করো",
                  source_message="Boss: test করো", box="dept_sales")
        raise SystemExit("FAIL: owner entry went to an agent box")
    except ValueError:
        pass

    # Work note: shared-এ যায় না, অচেনা box-এ যায় না; নিজের box-এ যায়।
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
    # Isolation: Sales-এর note Marketing পড়তে পারে না, Sales পারে।
    assert any(e["slug"] == "day-note" for e in mem.read_box("dept_sales"))
    assert all(e["slug"] != "day-note" for e in mem.read_box("dept_marketing"))
    assert all(e["slug"] != "day-note" for e in mem.list_own("dept_marketing"))
    # Shared সব box থেকে পড়া যায়।
    assert len(mem.read_box("dept_marketing")) == 3
    assert len(mem.read_box("worker:outreach-drafter")) == 3
    # Agent note verify হয় না; verify_all শুধু owner ৩টা।
    try:
        mem.verify("lessons", "day-note", box="dept_sales")
        raise SystemExit("FAIL: agent note was quote-verified")
    except ValueError:
        pass
    assert len(mem.verify_all()) == 3 and all(mem.verify_all().values())
    # ভুল box থেকে edit/forget বারণ (day-note শুধু Sales-এর);
    # নিজের box থেকে চলে; shared entry agent box থেকে বদলানো যায় না।
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
    # একই slug অন্য box-এ চলে; একই box-এ দুবার নয়।
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

    # Maintenance repair: ৭০ দিনের পুরোনো tentative archive হয়;
    # নতুন tentative থাকে; stated কখনো auto-archive হয় না।
    old = mem.learn("lessons", "old-rule", "Old rule.",
                    quote="পুরোনো কথা",
                    source_message="Boss: পুরোনো কথা", status="tentative")
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
    # Duplicate (box, area, slug) থাকলে পরেরটা archive হয়।
    mem.entries.append(dict(mem.entries[0], slug="dup-rule",
                            learned_at="2026-11-21T00:00:00+00:00"))
    mem.entries.append(dict(mem.entries[0], slug="dup-rule",
                            learned_at="2026-11-21T00:01:00+00:00"))
    mem._save()
    rep2 = mem.maintenance_repair(
        now=datetime(2026, 11, 21, tzinfo=timezone.utc))
    assert any("dup-rule" in s for s in rep2["deduped"]), rep2

    # validate_proposals: valid quote -> ready, bad quote -> rejected,
    # কিছু লেখে না।
    before = len(mem.list_entries())
    v = mem.validate_proposals([
        {"area": "preferences", "slug": "new-rule", "text": "New.",
         "quote": "নতুন কথা", "source_message": "Boss: নতুন কথা"},
        {"area": "preferences", "slug": "bad-rule", "text": "Bad.",
         "quote": "বানানো", "source_message": "Boss: অন্য কথা"},
    ])
    assert len(v["ready"]) == 1 and len(v["rejected"]) == 1, v
    assert len(mem.list_entries()) == before  # কিছু লেখা হয়নি

    # context_for: shared-এ ৩ seed আছে, source_message নেই।
    ctx = mem.context_for("main_ceo_bot")
    assert ctx["box"] == "main_ceo_bot"
    assert {"assistant-name", "reply-language", "gate-words"} <= {
        e["slug"] for e in ctx["shared"]}
    assert all("source_message" not in e for e in ctx["shared"])
    assert ctx["counts"]["shared"] == len(ctx["shared"])
    print("owner_memory: OK (seed 3 quote-verified, bad quote rejected, "
          "edit/archive/forget, markdown export, drawer boxes + isolation, "
          "maintenance repair, proposal validation, context_for)")
