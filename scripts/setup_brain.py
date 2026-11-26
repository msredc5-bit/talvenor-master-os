#!/usr/bin/env python3
"""setup_brain.py — make ANY free AI key work as the dev brain.

Boss's problem: the dev brain had a model name hard-coded in
00-CEO-Core/config.json (gemini-2.5-flash-lite). Google stopped serving
that model to new keys (HTTP 404), so the live probe failed even though
the key was valid — and fixing it meant editing JSON by hand.

This script removes the hand-editing. Run it after setting a key:

    setx GEMINI_API_KEY "paste-key-here"        (Windows, new terminal)
    python scripts\\setup_brain.py
    python scripts\\check_live_brain.py --live

Or with NO key at all — a local Ollama model (qwen2.5-coder:1.5b on Boss's PC):

    ollama pull qwen2.5-coder:1.5b
    python scripts\\setup_brain.py
    python scripts\\check_live_brain.py --live

What it does:
  0. First checks the LOCAL Ollama server (http://localhost:11434):
     no key needed. Lists installed models, keeps chat models, sends
     ONE tiny test call (max 30 tokens, no retries) per candidate.
     The first model that answers wins.
  1. Then looks for free-tier keys in the environment (GEMINI_API_KEY,
     OPENROUTER_API_KEY). Paid keys (META_API_KEY, OPENAI_API_KEY,
     ANTHROPIC_API_KEY, MOONSHOT_API_KEY, XAI_API_KEY) are listed but
     NEVER used for the dev brain — the dev brain is free-only.
  2. Asks the provider which models exist (its models-list endpoint),
     keeps only chat models the free-only guard allows, and SKIPS
     Gemini 2.5 models (Google returns 404 for them on new keys).
  3. Sends ONE tiny test call (max 30 tokens, no retries) per
     candidate. The first model that answers wins.
  4. Saves the winner into 00-CEO-Core/config.json development_brain
     (provider + model + fallback_chain). Nothing else in the file
     changes. The production brain is never touched, and the top-level
     "brain" flag is never flipped — the brain stays mock until the
     probe (check_live_brain.py --live) passes.

If no Ollama server answers and no free key is set, it prints the
setup steps and exits non-zero WITHOUT any network call and WITHOUT
changing config.json.

Safety: a key is never printed, never logged, never written to any
file. Keys are read only from environment variables.

Stdlib only. Windows + Linux. No pip.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
CONFIG_PATH = os.path.join(CEO_CORE_DIR, "config.json")

FREE_KEY_VARS = ("GEMINI_API_KEY", "OPENROUTER_API_KEY")
PAID_KEY_VARS = ("META_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                 "MOONSHOT_API_KEY", "XAI_API_KEY")

GEMINI_LIST_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_CHAT_URL = ("https://generativelanguage.googleapis.com/v1beta/openai/"
                   "chat/completions")
OPENROUTER_LIST_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

# Ollama — local server on Boss's PC. No key, no account, $0.
# OLLAMA_HOST only changes the server address (default localhost).
OLLAMA_DEFAULT_HOST = "http://localhost:11434"

# Preferred local models, in order. F1: gemma4:12b was removed — it
# cannot run on an 8 GB PC (llama-server OOM crash, verified twice
# 2026-11-26), so the chain no longer tries it and no longer wastes
# a 5-minute timeout on it. qwen2.5-coder:1.5b is the proven model
# (live probe 1.9s, 2026-11-26).
OLLAMA_PREFERENCE = ("qwen2.5-coder:1.5b",)

PROMPT = "Reply with the single word: ok"
TIMEOUT = 30
# Ollama gets 5 minutes, not 30 seconds: a cold local model load on
# an 8 GB PC can take minutes (first load reads gigabytes off disk).
# Honest limit (verified 2026-11-26): this does NOT make gemma4:12b
# run — it cannot start at all on 8 GB (llama-server init crashes,
# out of memory). It gives LOADABLE models (qwen2.5-coder:1.5b) a fair
# chance on a cold start instead of timing out mid-load.
OLLAMA_TIMEOUT = 300
MAX_OPENROUTER_CANDIDATES = 5

# Preferred Gemini free models, in order. gemini-2.5-flash-lite is
# deliberately NOT here: Google serves 2.5 models only to projects
# that used them before, so new keys get HTTP 404 on them.
GEMINI_PREFERENCE = ("gemini-3.5-flash-lite", "gemini-2.0-flash")

# The free-only guard (00-CEO-Core/free_only_guard.py) is the single
# source of truth for what is free-only. If it cannot be imported,
# this local set is the fallback — same ids the guard lists.
_FALLBACK_FREE_GEMINI = frozenset({
    "gemini-2.5-flash-lite", "gemini-3.5-flash-lite", "gemini-2.0-flash"})

try:
    if CEO_CORE_DIR not in sys.path:
        sys.path.insert(0, CEO_CORE_DIR)
    from free_only_guard import is_free_model as _guard_is_free_model
except Exception:  # noqa: BLE001 — guard import must never break setup
    _guard_is_free_model = None


def _is_free_model(provider, model):
    """True only if (provider, model) is free-only (guard, or fallback)."""
    if _guard_is_free_model is not None:
        try:
            return bool(_guard_is_free_model(provider, model))
        except Exception:  # noqa: BLE001 — fall through to local set
            pass
    if provider == "gemini":
        return model in _FALLBACK_FREE_GEMINI
    if provider == "openrouter":
        return model == "openrouter/free" or model.endswith(":free")
    if provider == "ollama":
        # Local server — any installed model is free ($0, no key).
        return bool(model and model.strip())
    return False


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def _get_json(url, headers=None):
    """GET a URL, parse the JSON body. One request, no retries."""
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.build_opener(_NoRedirect()).open(
            req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post_chat(url, headers, model):
    """One tiny chat call (max 30 tokens). Returns the reply text."""
    body = {"model": model,
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": 30}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.build_opener(_NoRedirect()).open(
            req, timeout=TIMEOUT) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if isinstance(payload, dict) and "error" in payload:
        raise RuntimeError(f"API error: {payload['error']}")
    text = payload["choices"][0]["message"].get("content") or ""
    return text.strip()


# --- Model-list parsing (pure functions — tested offline) ---

def parse_gemini_models(payload):
    """Model ids from a Gemini models-list response that can generate text."""
    ids = []
    if not isinstance(payload, dict):
        return ids
    for entry in payload.get("models", []) or []:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name") or ""
        methods = entry.get("supportedGenerationMethods") or []
        if not name.startswith("models/"):
            continue
        if "generateContent" not in methods:
            continue
        ids.append(name[len("models/"):])
    return ids


def pick_gemini_candidates(model_ids):
    """Ordered, usable Gemini candidates: free-only, no 2.5 models."""
    usable = [m for m in model_ids
              if "2.5" not in m and _is_free_model("gemini", m)]
    preferred = [m for m in GEMINI_PREFERENCE if m in usable]
    rest = [m for m in usable if m not in preferred]
    return preferred + rest


def parse_openrouter_models(payload):
    """Free text model ids from an OpenRouter models-list response."""
    ids = []
    if not isinstance(payload, dict):
        return ids
    for entry in payload.get("data", []) or []:
        if not isinstance(entry, dict):
            continue
        model_id = entry.get("id") or ""
        if not model_id.endswith(":free"):
            continue
        arch = entry.get("architecture") or {}
        modality = arch.get("modality") if isinstance(arch, dict) else None
        if modality is not None and modality != "text->text":
            continue
        ids.append(model_id)
    return ids


def _openrouter_rank(model_id):
    """Small/fast free models first (stable sort keeps list order)."""
    lowered = model_id.lower()
    for rank, word in enumerate(("flash", "lite", "mini", "haiku")):
        if word in lowered:
            return rank
    return 99


def pick_openrouter_candidates(model_ids):
    """Ordered OpenRouter candidates: auto-router first, then listed free models."""
    listed = sorted(set(model_ids), key=_openrouter_rank)
    return ["openrouter/free"] + listed[:MAX_OPENROUTER_CANDIDATES - 1]


def _ollama_host():
    """Ollama server base URL — OLLAMA_HOST, or localhost by default."""
    return os.environ.get("OLLAMA_HOST", "").strip() or OLLAMA_DEFAULT_HOST


def parse_ollama_models(payload):
    """Model names from an Ollama /api/tags response."""
    names = []
    if not isinstance(payload, dict):
        return names
    for entry in payload.get("models", []) or []:
        if isinstance(entry, dict) and entry.get("name"):
            names.append(str(entry["name"]))
    return names


def pick_ollama_candidates(model_ids):
    """Ordered local candidates: preferred models first, then the rest.

    Embedding-only models (names containing "embed") cannot chat,
    so they are dropped. Duplicates are removed, order kept.
    """
    usable = [m for m in model_ids if "embed" not in m.lower()]
    preferred = [m for m in OLLAMA_PREFERENCE if m in usable]
    rest = [m for m in usable if m not in preferred]
    return preferred + rest


def discover_ollama():
    """(candidates, error): usable local Ollama models, or ([], reason)."""
    try:
        payload = _get_json(_ollama_host().rstrip("/") + "/api/tags")
    except Exception as exc:  # noqa: BLE001 — server down / not installed
        return [], f"Ollama server not reachable: {type(exc).__name__}"
    return pick_ollama_candidates(parse_ollama_models(payload)), None


def probe_ollama(model, key=None):
    """Tiny test call on the same path the Ollama provider uses.

    key is accepted and ignored (try_provider calls every probe with
    (model, key); local Ollama needs no key)."""
    body = {"model": model,
            "messages": [{"role": "user", "content": PROMPT}],
            "stream": False,
            "options": {"num_predict": 30}}
    req = urllib.request.Request(
        _ollama_host().rstrip("/") + "/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.build_opener(_NoRedirect()).open(
            req, timeout=OLLAMA_TIMEOUT) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if isinstance(payload, dict) and "error" in payload:
        raise RuntimeError(f"API error: {payload['error']}")
    text = payload["message"].get("content") or ""
    return text.strip()


# --- Discovery + probe (one request per candidate, no retries) ---

def discover_gemini(key):
    """(candidates, error): usable Gemini models for this key."""
    try:
        url = (GEMINI_LIST_URL + "?pageSize=100&key="
               + urllib.parse.quote(key))
        payload = _get_json(url)
    except Exception as exc:  # noqa: BLE001 — the URL holds the key, never print it
        return [], f"models list failed: {type(exc).__name__}"
    return pick_gemini_candidates(parse_gemini_models(payload)), None


def discover_openrouter():
    """(candidates, error): usable OpenRouter free models."""
    try:
        payload = _get_json(OPENROUTER_LIST_URL)
    except Exception as exc:  # noqa: BLE001
        return [], f"models list failed: {type(exc).__name__}: {exc}"
    return pick_openrouter_candidates(parse_openrouter_models(payload)), None


def probe_gemini(model, key):
    """Tiny test call on the same path the Gemini provider uses."""
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + key}
    return _post_chat(GEMINI_CHAT_URL, headers, model)


def probe_openrouter(model, key):
    """Tiny test call on the same path the OpenRouter provider uses."""
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + key,
               "HTTP-Referer": "https://talvenorai.agency",
               "X-Title": "Talvenor Master OS"}
    return _post_chat(OPENROUTER_CHAT_URL, headers, model)


def try_provider(provider, key):
    """(model, reply) for the first working model, or (None, reason)."""
    if provider == "ollama":
        candidates, error = discover_ollama()
        probe = probe_ollama
    elif provider == "gemini":
        candidates, error = discover_gemini(key)
        probe = probe_gemini
    else:
        candidates, error = discover_openrouter()
        probe = probe_openrouter
    if error is not None:
        return None, error
    if not candidates:
        return None, "no usable free model found in the models list"
    failures = []
    for model in candidates:
        try:
            reply = probe(model, key)
        except Exception as exc:  # noqa: BLE001 — try the next candidate
            failures.append(f"{model}: {type(exc).__name__}")
            continue
        if reply:
            return model, reply
        failures.append(f"{model}: empty reply")
    return None, "all candidates failed (" + "; ".join(failures) + ")"


# --- Config save (dev brain only — production is never touched) ---

def save_dev_brain(provider, model, config_path=None):
    """Write the winner into config.json development_brain.

    Sets provider + model and puts "provider:model" first in
    fallback_chain, keeping the other entries as fallback. Returns the
    new chain. The top-level "brain" flag and "production_brain" are
    never changed. Refuses to save a model that is not free-only.
    """
    path = config_path or CONFIG_PATH
    if not _is_free_model(provider, model):
        raise RuntimeError(
            f"{provider}:{model} is not free-only — refusing to save")
    if provider == "gemini" and "2.5" in model:
        raise RuntimeError(
            f"{provider}:{model} is a Gemini 2.5 model — Google returns "
            "HTTP 404 for it on new keys, refusing to save")
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    dev = cfg.get("development_brain")
    if not isinstance(dev, dict):
        raise RuntimeError("development_brain block missing from config.json")
    winner = f"{provider}:{model}"
    old_chain = [str(e) for e in dev.get("fallback_chain") or []]
    chain = [winner] + [e for e in old_chain if e != winner]
    dev["provider"] = provider
    dev["model"] = model
    dev["fallback_chain"] = chain
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    return chain


# --- No-key path (no network, no config change) ---

def detect_keys():
    """Which provider keys are set — names only, never values."""
    found = {}
    for var in FREE_KEY_VARS + PAID_KEY_VARS:
        found[var] = bool(os.environ.get(var))
    return found


def print_no_key_steps(found):
    print("[setup-brain] No local Ollama model answered and no free AI "
          "key is set — no call was made and config was not changed.")
    paid = [v for v in PAID_KEY_VARS if found.get(v)]
    if paid:
        print("[setup-brain] These keys ARE set, but they are paid — "
              "the free dev brain never uses them:")
        for var in paid:
            print(f"[setup-brain]   - {var} (paid, not used for the dev brain)")
    print("[setup-brain] Setup steps (Boss's PC, Windows — free, no card, "
          "no billing):")
    print("[setup-brain] LOCAL (no key at all): install Ollama from "
          "https://ollama.com, then pull a model and run again:")
    print("[setup-brain]   ollama pull qwen2.5-coder:1.5b")
    print("[setup-brain]   (do NOT pull gemma4:12b — it cannot run on "
          "an 8 GB PC, verified twice)")
    print("[setup-brain] CLOUD (free key): get a free Gemini key: "
          "https://aistudio.google.com/apikey")
    print('[setup-brain] 2. Set it, then open a NEW terminal: '
          'setx GEMINI_API_KEY "paste-key-here"')
    print("[setup-brain]    (or an OpenRouter key: https://openrouter.ai/keys "
          '-> setx OPENROUTER_API_KEY "paste-key-here")')
    print("[setup-brain] 3. Run again: python scripts\\setup_brain.py")
    print("[setup-brain] 4. Then prove it: "
          "python scripts\\check_live_brain.py --live")


def main(argv=None):
    # Local first: Ollama needs no key at all. If a local model
    # answers, it wins — $0, private, no account.
    print("[setup-brain] Trying local Ollama (no key needed)...")
    model, outcome = try_provider("ollama", None)
    if model is not None:
        print(f"[setup-brain] ollama answered with model {model} — "
              "saving it as the dev brain.")
        try:
            chain = save_dev_brain("ollama", model)
        except Exception as exc:  # noqa: BLE001
            print(f"[setup-brain] ERROR: could not save config: {exc}")
            return 1
        print(f"[setup-brain] DONE: dev brain is now ollama:{model}.")
        print(f"[setup-brain] fallback_chain: {chain}")
        print("[setup-brain] Next command (proves it live): "
              "python scripts\\check_live_brain.py --live")
        print("[setup-brain] The production brain was not touched and "
              "is still locked.")
        return 0
    print(f"[setup-brain] ollama: no working model ({outcome}).")
    found = detect_keys()
    free_vars = [v for v in FREE_KEY_VARS if found.get(v)]
    if not free_vars:
        print_no_key_steps(found)
        return 1
    for var in FREE_KEY_VARS:
        if not found.get(var):
            continue
        provider = "gemini" if var == "GEMINI_API_KEY" else "openrouter"
        key = os.environ.get(var)
        print(f"[setup-brain] Trying {provider} (key {var} is set)...")
        model, outcome = try_provider(provider, key)
        if model is None:
            print(f"[setup-brain] {provider}: no working model ({outcome}).")
            continue
        print(f"[setup-brain] {provider} answered with model {model} — "
              "saving it as the dev brain.")
        try:
            chain = save_dev_brain(provider, model)
        except Exception as exc:  # noqa: BLE001
            print(f"[setup-brain] ERROR: could not save config: {exc}")
            return 1
        print(f"[setup-brain] DONE: dev brain is now {provider}:{model}.")
        print(f"[setup-brain] fallback_chain: {chain}")
        print("[setup-brain] Next command (proves it live): "
              "python scripts\\check_live_brain.py --live")
        print("[setup-brain] The production brain was not touched and "
              "is still locked.")
        return 0
    print("[setup-brain] FAILED: no free provider answered. "
          "Config was not changed.")
    print("[setup-brain] Check the key (a wrong key fails every model) "
          "and your internet, then run again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
