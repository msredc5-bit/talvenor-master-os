# Data Isolation Policy — Talvenor Unified OS

> Status: DRAFT — awaiting Boss's approval
> Date: 2026-11-19
> Type: POLICY ONLY — this file creates no new data, moves no data, changes no file. Rules only.
> Basis: the brief's architecture rule — "There will be one central HQ, but no Business Unit may enter another Business Unit's private Client Data, Orders, or Financial Records without permission."

## 1. DATA areas — 4

| DATA area | Folder / file | Owner (who reads/writes) | What is inside |
|---|---|---|---|
| DATA/central | `store/tasks.json`, `store/approvals.json`, `store/vault/`, `00-CEO-Core/config.json` | HQ only (Main CEO Bot + Boss) | Task record, approval record, shared vault, system config |
| DATA/agency | `01-Agency-Department/` | Agency Chief only | Lead, prospect research, outreach draft, client intake, delivery, finance record |
| DATA/commerce | `02-Digital-Product-Department/` | Products Chief only | PA vet list (`pa-vet-list/pa-vet-clinics.csv`), kit blueprint (`kit-outline.md`), gate0-status (`gate0-status.md`) |
| DATA/media | `03-Content-Creation-Department/` | Content Chief only | Pipeline (`pipeline.md`), VOICE.md, ToolPilot status (`toolpilot-status.md`), Creator OS worker output |

## 2. Reading rules

1. **A business reads only its own department + the shared vault.** Agency reads `01-Agency-Department/` + `store/vault/`. Commerce reads `02-Digital-Product-Department/` + `store/vault/`. Media reads `03-Content-Creation-Department/` + `store/vault/`.
2. **HQ (Main CEO Bot) can read everything** — because routing, approval, and reporting are HQ's jobs. But HQ also never executes a gated action itself.
3. **Boss can read everything** — Founder, final decision-maker.

## 3. Isolation rules (strict)

| Rule | Details |
|---|---|
| Client records separate | The Agency's lead/client records belong to the Agency only. Commerce or Media cannot read them. |
| Financial records separate | Each business's revenue, expense, and invoice records are its own only. A combined picture exists only in HQ's Finance Intelligence (with real numbers, `shared-services.md` §7). |
| Order / sale records separate | Commerce's order/sale records belong to Commerce only. |
| To read another business's data | Boss's explicit permission is needed — not a verbal hint, clear permission. No cross-read without permission. |
| If a cross-business read happens | It must be logged as an internal project — which business, what was read, why, under which permission from Boss. No cross-read without a log. |
| What goes in the shared vault | Only what all three businesses need (e.g. booking link, brand line, gate word rules). No client's personal information goes in the vault. |
| Research notes | `~/workspace/research_notes/` shared, read-only source — everyone can read, nobody can change. |

## 4. Secret rules

- **No secret (API key, password, token) may be written in a prompt or in the repo.**
- Keys only via the connector Secure Vault — transient use, saved nowhere.
- No agent holds a credential — details in `01-Agency-Department/governance/security-policy.md`.
- If a secret leaks, Boss must be told — it must not be covered up.

## 5. What happens on a violation

- If a cross-read without permission is caught, work stops, Boss is told, and Boss decides.
- Changing this policy needs Boss's approval. No agent can change the policy itself.

## 6. Current state (true)

- Policy: DRAFT (this file) — Boss's review remaining.
- Enforcement: no automated enforcement built — GAP. For now, humans + the Main CEO Bot's routing follow the rules; there is no code to block violations.
- Amount of client data: paying clients in the Agency are 0 — there are no client records to separate yet; the rules were written in advance so nothing goes wrong when clients come.
