# Approval Policy — Gate-Word System

> Phase 1 — Foundation only
> Status: DRAFT — Boss-এর অনুমোদনের অপেক্ষায়
> তারিখ: 2026-11-19
> সম্পর্কিত ফাইল: `office-charter.md`, `agent-permissions.md`, `security-policy.md`

## 1. মূল নীতি

- **Boss-এর exact gate word ছাড়া কিছুই send / publish / spend / delete হয় না।**
- **কোনো auto-approve path কোথাও নেই।** কোনো agent, manager, বা system নিজে নিজে approve করতে পারে না।
- Approval দেওয়ার কাজ শুধু Boss-এর। ApprovalGateway শুধু request-টি PENDING হিসেবে ধরে রাখে — approve করে না।
- Approval-এর record JSON store-এ থাকে — `store/approvals.json`।

## 2. Gate-Word System

| Gate Word | মানে | কী approve হয় |
|-----------|------|---------------|
| **ok** | Plan / asset approval | Plan, draft, design, asset — Boss দেখে "ok" বললে plan approve হলো |
| **"post it"** | Publish | Social post publish করা যাবে — একটা post-এর জন্য একবার |
| **send** | Send | Email / message পাঠানো যাবে — যে batch-এর জন্য বলা হয়েছে, শুধু সেটা |
| **go** | Advance build phase | পরের build phase-এ যাওয়া যাবে |
| **"upload it"** | Upload video | Video upload করা যাবে |

**নিয়ম:**

- Gate word exact হতে হবে। কাছাকাছি শব্দ approve নয়।
- একটা gate word একটা কাজের জন্য। "ok" দিয়ে publish হয় না, "post it" দিয়ে send হয় না।
- Gate word-এর scope Boss যেটা বলেছেন, শুধু সেটাই। এক batch-এর send approval দিয়ে অন্য batch পাঠানো যাবে না।
- Approval card expire হতে পারে — expire হলে আবার Boss-এর কাছে যেতে হবে, নিজে retry করা যাবে না।

## 3. Approval Table (CORRECTED)

অন্য AI-এর brief-এর approval table-এ ভুল ছিল। নিচের table-টাই সঠিক:

| কাজ | Approval Level | বর্তমান অবস্থা |
|-----|---------------|----------------|
| Lead research | Autonomous | Agent নিজে করতে পারে — research-এ কোনো gate লাগে না |
| Internal report | Autonomous | Agent নিজে লিখতে পারে — Boss-কে দেখানোর জন্য draft হিসেবে |
| Draft email | Autonomous | Draft তৈরি করা যায় — পাঠানো যায় না |
| External email sending | Approval / Controlled policy | Boss-এর "send" gate word লাগবে — **এবং বর্তমানে PAUSED (2026-11-14 থেকে, SPF/DMARC DNS fix pending)** |
| CRM update | Restricted automation | CRM (n8n Cloud Data Tables) এখনো live নয় — update করার মতো কিছুই নেই। CRM live হলে restricted automation নিয়মে চলবে |
| Production agent deployment | Founder approval | Sophia (live receptionist) deploy / বদল — শুধু Boss-এর অনুমোদনে |
| Client pricing change | Founder approval | Pricing LOCKED — বদলাতে হলে Boss-এর সিদ্ধান্ত লাগবে; prospect-কে quote করা যাবে না |
| Refund / payment | Human approval | টাকা সংক্রান্ত সব কাজে Boss-এর অনুমোদন লাগবে; spend cap $0 |
| Legal / tax filing | Human professional review | Lawyer / tax professional-এর review ছাড়া করা যাবে না |
| Security / access change | Restricted approval | Access বদল, secret rotate — শুধু Boss করেন, restricted approval-এ |

## 4. Approval Flow — কীভাবে কাজ করে

1. Agent draft / plan তৈরি করে।
2. Agent ApprovalGateway-তে request পাঠায় — status PENDING।
3. Request `store/approvals.json`-এ record হয়।
4. Boss request দেখে gate word দেন — অথবা দেন না।
5. Gate word পেলে তবেই action execute হয়। Gate word না পেলে action হয় না।
6. Execute হওয়ার পর result record হয় — কী করা হলো, কখন, কার approval-এ।

**যা করা যাবে না:**

- PENDING request নিজে approve করা
- Boss-এর gate word অনুমান করা বা ধরে নেওয়া
- একটা approval দিয়ে অন্য কাজ করা
- Approval ছাড়া "পরে Boss-কে জানাবো" বলে action করা

## 5. Email PAUSED — বিশেষ নোট

- Email outreach PAUSED 2026-11-14 থেকে। SPF-এ Gmail include নেই, DMARC missing — DNS fix Boss-এর কাছ থেকে pending।
- Pause থাকা অবস্থায় "send" gate word দিলেও email যাবে না — আগে DNS fix verify করতে হবে, তারপর Boss restart বলবেন।
- First mails এখন 162 — pause-এর মধ্যে এই সংখ্যা বাড়বে না।
- Day 4 / Day 5 draft READY আছে, unsent — restart না হওয়া পর্যন্ত পাঠানো যাবে না।

## 6. কোনো Auto-Approve নেই

- কোনো agent-এর permission-এ auto-approve নেই।
- কোনো workflow-তে auto-approve step নেই।
- কোনো cron / trigger নিজে approve করতে পারে না।
- "Boss ব্যস্ত, তাই নিজে approve করে নিলাম" — এটা কখনো বৈধ নয়।

## 7. Approval বদল

- এই approval policy বদলাতে হলে Boss-এর অনুমোদন লাগবে।
- Pricing, gate word, approval level — কোনোটাই agent নিজে বদলাতে পারবে না।
