// render_check_command_center.js — render verification for the
// Command Center page (FOUNDER OS F2).
//
// Executes the page's real inline script with real data under a minimal
// DOM stub and proves the two 2026-11-27 fixes hold:
//   - Module 1 Voice card renders voice.label + voice.detail
//     (not fmt(s.voice) on the voice object -> "[object Object]").
//   - Module 6 CEO Tasks breakdown renders nested objects
//     (by_business / by_status / by_type) as small lists, not
//     String(ceo.tasks[k]) -> "[object Object]".
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
  if (failures.length) { console.error("RENDER CHECK FAILED: " + failures.join("; ")); process.exit(1); }
  console.log("RENDER CHECK: ALL PASS (" + (isPreview ? "preview" : "live page") + ")");
})();
