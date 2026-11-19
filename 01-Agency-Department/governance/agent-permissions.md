# Agent Permissions — Per-Agent Permission Model

> Phase 1 — Foundation only
> Status: DRAFT — Boss-এর অনুমোদনের অপেক্ষায়
> তারিখ: 2026-11-19
> সম্পর্কিত ফাইল: `office-charter.md`, `approval-policy.md`, `security-policy.md`

## 1. মূল নীতি (Core Principles)

1. **প্রতিটি agent-এর permission তার role অনুযায়ী।** Role-এর বাইরে কোনো action করা যাবে না।
2. **Mock-brain agent শুধু draft করে।** Mock brain দিয়ে কোনো live action execute করা যায় না।
3. **কোনো agent credential ধরে না।** Password, API key, token — কোনো agent-এর কাছে থাকে না। Key শুধু connector Secure Vault-এ থাকে, transient use হয়।
4. **Manager plan/delegate করতে পারে, execute করতে পারে না।** Gated action manager নিজে execute করবে না — সেটা ApprovalGateway-তে PENDING হয়ে Boss-এর কাছে যাবে।
5. **কোনো auto-approve নেই।** Permission থাকলেই action হয়ে যায় না — gated action-এর জন্য Boss-এর gate word লাগবেই।

## 2. Permission-এর চারটি অংশ

প্রতিটি agent-এর permission এই চারটি দিয়ে বোঝা যায়:

| অংশ | মানে |
|-----|------|
| **Role** | Agent-টি কী কাজের জন্য — যেমন Sales Manager, Marketing Manager |
| **Allowed tools** | কোন tool ব্যবহার করতে পারে — যেমন file read, draft write, research |
| **Allowed actions** | কোন কাজ নিজে করতে পারে — যেমন research, draft, plan, delegate |
| **Forbidden actions** | কোন কাজ কখনো করতে পারবে না — যেমন send, publish, spend, delete, credential access |

## 3. Worker Agent — সাধারণ নিয়ম

- **Allowed tools:** File read, draft write, research/search, internal note তৈরি।
- **Allowed actions:** Research করা, draft তৈরি করা, internal report লেখা, নিজের section-এর plan সাজানো।
- **Forbidden actions:**
  - External email / DM / message পাঠানো
  - Social post publish করা
  - টাকা খরচ করা, payment করা, refund দেওয়া
  - File / record / repo delete করা
  - Production Vapi agent deploy বা বদলানো
  - Credential, password, API key দেখা বা ব্যবহার করা
  - Client-এর সাথে সরাসরি যোগাযোগ করা
  - Price quote করা

## 4. Manager Agent — সাধারণ নিয়ম

- **Allowed tools:** Worker agent-দের delegate করা, draft review করা, plan তৈরি করা, internal report লেখা।
- **Allowed actions:** Plan করা, delegate করা, draft তৈরি ও review করা, Boss-এর কাছে approval-এর জন্য পাঠানো।
- **Forbidden actions:**
  - Gated action নিজে execute করা (send / publish / spend / delete / deploy)
  - ApprovalGateway bypass করা
  - Worker-কে gated action করতে বলা
  - Credential access করা
  - Pricing বদলানো বা quote করা
  - Legal / tax filing করা

Manager-এর কাজ plan + delegate + draft — এর বেশি নয়।

## 5. 8 Manager Agent-এর Permission Table

সব manager-এর permission level একই ভিত্তিতে: **plan + delegate + draft; gated action → ApprovalGateway PENDING**। কোনো manager-এর আলাদা execute permission নেই।

| # | Manager Agent | Department | Permission Level | Gated Action হলে কী হয় |
|---|---------------|------------|------------------|------------------------|
| 01 | Sales Manager | 01 Sales & Growth | Plan + delegate + draft | ApprovalGateway PENDING → Boss-এর gate word লাগবে |
| 02 | Marketing Manager | 02 Marketing | Plan + delegate + draft | ApprovalGateway PENDING → Boss-এর gate word লাগবে |
| 03 | AI Engineering Manager | 03 AI Engineering | Plan + delegate + draft | ApprovalGateway PENDING → Boss-এর gate word লাগবে |
| 04 | Client Operations Manager | 04 Client Operations | Plan + delegate + draft | ApprovalGateway PENDING → Boss-এর gate word লাগবে |
| 05 | Research & Strategy Manager | 05 Research & Strategy | Plan + delegate + draft | ApprovalGateway PENDING → Boss-এর gate word লাগবে |
| 06 | Finance & Admin Manager | 06 Finance & Admin | Plan + delegate + draft | ApprovalGateway PENDING → Boss-এর gate word লাগবে |
| 07 | Quality & Security Manager | 07 Quality & Security | Plan + delegate + draft | ApprovalGateway PENDING → Boss-এর gate word লাগবে |
| 08 | Product & Innovation Manager | 08 Product & Innovation | Plan + delegate + draft | ApprovalGateway PENDING → Boss-এর gate word লাগবে |

**নোট:** Agency Chief wiring Phase 2-এর কাজ — এই Phase 1-এ manager-দের উপরে Chief wiring এখনো করা হয়নি। Manager-রা Phase 1-এ সরাসরি Main CEO Bot / Boss-এর কাছে report করে।

## 6. বিশেষ সীমা (Special Limits)

- **Sales Manager:** Lead research করতে পারে, email draft করতে পারে — কিন্তু email পাঠাতে পারে না। Email outreach এখন PAUSED (2026-11-14 থেকে)। Pause উঠলেও send-এর জন্য Boss-এর gate word লাগবে।
- **Marketing Manager:** Post draft করতে পারে — কিন্তু "post it" ছাড়া publish করতে পারে না।
- **AI Engineering Manager:** Vapi build plan draft করতে পারে — কিন্তু production agent (Sophia, live receptionist, +1 (947) 223-0244) deploy বা বদলাতে পারে না। Production deploy শুধু Boss-এর অনুমোদনে।
- **Finance & Admin Manager:** হিসাব draft করতে পারে — কিন্তু payment, refund, spend করতে পারে না। Spend cap $0।
- **Quality & Security Manager:** Audit করতে পারে, সমস্যা flag করতে পারে — কিন্তু access বদলাতে বা secret rotate করতে পারে না। সেটা Boss করেন।
- **Product & Innovation Manager:** Vet Kit idea draft করতে পারে — কিন্তু Gate 0 pass না হওয়া পর্যন্ত Vet Kit-এর কোনো live step নিতে পারে না।

## 7. Permission ভাঙলে কী হয়

- কোনো agent তার permission-এর বাইরে action নেওয়ার চেষ্টা করলে, সেই action block হবে।
- Block হওয়া action ApprovalGateway-তে PENDING হিসেবে record হবে — store/approvals.json-এ।
- Agent নিজে block bypass করার চেষ্টা করবে না। Bypass-এর চেষ্টা Quality & Security Manager-কে জানাতে হবে।
- Permission বদলাতে হলে Boss-এর অনুমোদন লাগবে। কোনো agent নিজের permission নিজে বাড়াতে পারবে না।

## 8. Credential নিয়ম (সংক্ষেপ)

- কোনো agent-এর কাছে password / API key / token থাকে না।
- Key শুধু connector Secure Vault-এ থাকে।
- Agent-এর tool call-এ key transient ভাবে ব্যবহার হয় — file-এ, prompt-এ, বা GitHub repo-তে key লেখা যাবে না।
- বিস্তারিত `security-policy.md`-তে আছে।
