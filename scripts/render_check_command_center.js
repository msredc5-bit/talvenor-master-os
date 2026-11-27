// render_check_command_center.js — render verification for the
// Command Center page (FOUNDER OS F2).
//
// Executes the page's real inline script with real data under a minimal
// DOM stub and proves:
//   - The two 2026-11-27 fixes hold (module 1 Voice card renders
//     voice.label + voice.detail; module 6 CEO Tasks breakdown renders
//     nested objects as small lists) — no "[object Object]" anywhere.
//   - The F2 batch-3 modules render honestly: chat shows a disabled
//     send and no fake conversation; voice shows the loop state with
//     the mic off; personas render the 3 real profiles; execution
//     shows recent records (not a live stream); memory shows entry
//     metadata only (no quote text); library lists real files;
//     integrations call only the probed n8n MCP "connected".
//
// Usage: node scripts/render_check_command_center.js [html-path]
//   Default html-path is dashboards/command-center.html. A preview
//   file (with window.__PREVIEW_STATUS__ inlined) is detected and
//   run with its inlined data instead of the fetch stub.
// Called by scripts/check_command_center.py. Stdlib only (node).
"use strict";
const fs = require("fs");
const path = require("path");

const BASE = path.resolve(__dirname, "..");
const DIR = path.join(BASE, "dashboards");
const htmlPath = process.argv[2] || path.join(DIR, "command-center.html");
const html = fs.readFileSync(htmlPath, "utf8");
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (!blocks.length) { console.error("FAIL: no inline script found"); process.exit(1); }
const isPreview = html.includes("window.__PREVIEW_STATUS__");

function makeEl(tag) {
  const el = {
    tagName: String(tag || "div").toUpperCase(),
    children: [],
    _text: "",
    className: "",
    id: "",
    hidden: false,
    disabled: false,
    value: "",
    style: {},
    appendChild(c) { this.children.push(c); return c; },
    addEventListener() {},
    setAttribute() {},
    querySelector() { return null; },
    querySelectorAll() { return []; },
    get textContent() {
      let t = this._text;
      for (const c of this.children) t += c.textContent;
      return t;
    },
    set textContent(v) { this._text = String(v == null ? "" : v); this.children = []; },
    set innerHTML(v) { this._text = ""; this.children = []; },
    get innerHTML() { return ""; },
  };
  return el;
}
const byId = {};
globalThis.document = {
  getElementById(id) {
    if (!byId[id]) { byId[id] = makeEl("div"); byId[id].id = id; }
    return byId[id];
  },
  createElement(tag) { return makeEl(tag); },
};
globalThis.window = {};
const status = JSON.parse(fs.readFileSync(path.join(DIR, "status.json"), "utf8"));
const ceo = JSON.parse(fs.readFileSync(path.join(DIR, "ceo-report.json"), "utf8"));
globalThis.fetch = (url) => {
  const u = String(url);
  if (u.includes("status.json")) return Promise.resolve({ ok: true, json: async () => status });
  if (u.includes("ceo-report.json")) return Promise.resolve({ ok: true, json: async () => ceo });
  return Promise.reject(new Error("taskboard not running (stub)"));
};
globalThis.setInterval = () => 0; // keep the process from hanging on the 60s ticker

function serialize(el) {
  let t = el._text || "";
  for (const c of el.children) t += serialize(c);
  return t;
}

(async () => {
  // Preview files have a data script first, then the main script.
  // The live page has only the main script.
  for (const block of blocks) eval(block);
  await new Promise((r) => setTimeout(r, 1500)); // let the fetch chain settle
  const failures = [];
  const check = (name, cond) => {
    console.log((cond ? "PASS" : "FAIL") + " " + name);
    if (!cond) failures.push(name);
  };
  let all = "";
  for (const id of Object.keys(byId)) all += "\n[" + id + "]\n" + serialize(byId[id]);

  check("no '[object Object]' anywhere in rendered page", !all.includes("[object Object]"));
  const ov = serialize(byId["overview-cards"] || makeEl("div"));
  check("Voice card shows label REAL", ov.includes("REAL"));
  check("Voice card shows detail text", ov.includes("Jarvis voice") && ov.includes("Piper TTS"));
  const ceoBody = serialize(byId["ceo-body"] || makeEl("div"));
  check("CEO Tasks by_business renders as list (agency: 1)", ceoBody.includes("agency: 1"));
  check("CEO Tasks by_status renders as list (done: 1)", ceoBody.includes("done: 1"));
  check("CEO Tasks by_type renders as list (research: 1)", ceoBody.includes("research: 1"));
  check("CEO Tasks scalars still present (total, status ok)", ceoBody.includes("total") && ceoBody.includes("ok"));

  // ---- F2 batch 3: the 7 new modules render honestly ----
  const section = (ids) => ids.map((id) => serialize(byId[id] || makeEl("div"))).join("\n");
  const chat = section(["chat-cards", "chat-persona-line", "chat-transcript"]);
  check("Chat shows no transcript (not a live chat)", chat.includes("No transcript"));
  check("Chat shows the default persona (Mira)", chat.includes("Speaking as: Mira"));
  check("Chat send is disabled, with the reason", chat.includes("disabled") && chat.includes("live dev brain runs on Boss"));
  check("Chat has no fake conversation (no typing indicator)", !chat.includes("typing"));
  const voice = section(["voice-cards", "voice-gate-body"]);
  check("Voice shows the loop is not live in the browser", voice.includes("PC-side Python process"));
  check("Voice shows Bengali prompts regressed", voice.includes("regressed"));
  check("Voice gate phrases render (send / publish)", voice.includes("send") && voice.includes("publish"));
  const personas = section(["persona-grid"]);
  check("Personas render the 3 real profiles", personas.includes("Mira") && personas.includes("Main CEO Bot") && personas.includes("Chief of Staff (Agency)"));
  check("Personas mark the default", personas.includes("Default persona"));
  const exec = section(["exec-cards", "exec-server-line", "exec-recent-body", "exec-calls-body"]);
  check("Execution says it is not a live stream", exec.includes("No live stream"));
  // The recent-8 window moves as skills execute, so check the
  // rendered table against the data's own last record, not a
  // hardcoded skill name. In preview mode the data is the inlined
  // snapshot (the disk file may have been republished since).
  const dataStatus = isPreview ? globalThis.window.__PREVIEW_STATUS__ : status;
  const dataRecent = (dataStatus.execution
    && dataStatus.execution.skill_executions
    && dataStatus.execution.skill_executions.recent) || [];
  const lastRecent = dataRecent[dataRecent.length - 1] || {};
  check("Execution shows recent skill records",
    dataRecent.length > 0
    && exec.includes(String(lastRecent.skill || ""))
    && exec.includes(String(lastRecent.event || "")));
  const dataCalls = (dataStatus.execution
    && dataStatus.execution.dev_brain_calls
    && dataStatus.execution.dev_brain_calls.records) || [];
  const lastCall = dataCalls[dataCalls.length - 1] || {};
  check("Execution shows dev brain calls",
    dataCalls.length > 0
    && exec.includes(String(lastCall.model || ""))
    && exec.includes(String(lastCall.provider || "")));
  check("Execution server line says not running (stub has no server)", exec.includes("not running"));
  const mem = section(["memory-cards", "memory-entry-body", "memory-box-body"]);
  check("Memory lists the 3 entry slugs (metadata only)", mem.includes("assistant-name") && mem.includes("reply-language") && mem.includes("gate-words"));
  check("Memory lists all 13 boxes", mem.includes("main_ceo_bot") && mem.includes("dept_sales") && mem.includes("content"));
  check("Memory shows NO quote text", !mem.includes("Your name is Mira") && !mem.includes("তুমি এখন থেকে বাংলায় কথা বলবা"));
  const lib = section(["library-cards", "library-groups"]);
  check("Library lists real repo files", lib.includes("live-brain-proof-2026-11-26.md") && lib.includes("README.md") && lib.includes("TALVENOR_CHANGELOG.md"));
  check("Library lists the VM-only reports group", lib.includes("unified-business-os/"));
  const integ = section(["integ-cards", "integ-body", "integ-wf-body"]);
  check("Integrations call n8n Cloud MCP connected (probed)", integ.includes("n8n Cloud MCP") && integ.includes("connected") && integ.includes("75"));
  check("Integrations show workflows NOT LIVE", integ.includes("NOT LIVE"));
  check("Integrations show Meta unreachable, Vapi unknown", integ.includes("unreachable from this VM") && integ.includes("unknown"));
  if (failures.length) { console.error("RENDER CHECK FAILED: " + failures.join("; ")); process.exit(1); }
  console.log("RENDER CHECK: ALL PASS (" + (isPreview ? "preview" : "live page") + ")");
})();
