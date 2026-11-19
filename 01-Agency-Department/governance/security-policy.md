# Security Policy

> Phase 1 — Foundation only
> Status: DRAFT — Boss-এর অনুমোদনের অপেক্ষায়
> তারিখ: 2026-11-19
> সম্পর্কিত ফাইল: `office-charter.md`, `agent-permissions.md`, `approval-policy.md`

## 1. মূল নীতি

- **কোনো secret কোথাও লেখা যাবে না।** Password, API key, token — prompt-এ নয়, file-এ নয়, GitHub repo-তে নয়।
- **কোনো agent credential ধরে না।** Key শুধু connector Secure Vault-এ থাকে।
- **$0 spend cap।** Boss-এর অনুমতি ছাড়া কোনো খরচ নয়।
- **সন্দেহ হলে Boss-কে জানাও, নিজে ঠিক করার চেষ্টা করো না।**

## 2. Secret কোথায় থাকে, কোথায় থাকে না

**থাকে:**

- Connector Secure Vault-এ — সেখানেই key সংরক্ষণ করা হয়।
- Transient use — tool call-এর সময় key সাময়িকভাবে ব্যবহার হয়, তারপর আর থাকে না।

**থাকে না:**

- Prompt-এ password / API key লেখা যাবে না।
- File-এ (`.md`, `.json`, `.py`, `.env`, যেকোনো file) key লেখা যাবে না।
- GitHub repo-তে (talvenor-master-os বা অন্য কোনো repo) key commit করা যাবে না।
- Chat-এ, draft-এ, report-এ key paste করা যাবে না।
- Screenshot-এ key দেখানো যাবে না।

**Checked rule — repo-তে কোনো secret নেই:** এই নিয়মটি checked rule হিসেবে ধরা হয় — repo-তে secret থাকলে সেটা violation। কোনো agent repo-তে secret লিখবে না, এবং secret দেখলে সঙ্গে সঙ্গে Boss-কে জানাবে।

## 3. Per-Agent API Permission ও Log

- প্রতিটি agent শুধু তার role-এর জন্য অনুমোদিত API / tool ব্যবহার করতে পারে। Role-এর বাইরের API call করা যাবে না।
- সব tool call-এর log থাকে — কোন agent, কখন, কোন tool, কী কাজে ব্যবহার করলো।
- Log-এ কখনো secret লেখা যাবে না। Log-এ শুধু action-এর বিবরণ থাকবে, key নয়।
- কোনো agent অন্য agent-এর permission ব্যবহার করে API call করতে পারবে না।
- API permission বদলাতে হলে Boss-এর অনুমোদন লাগবে।

## 4. Task Boundary

- প্রতিটি agent শুধু নিজের task-এর ভেতরে কাজ করে।
- নিজের task-এর বাইরের file, record, বা system-এ হাত দেওয়া যাবে না।
- অন্য department-এর কাজে হস্তক্ষেপ করা যাবে না — প্রয়োজন হলে নিজের manager-কে জানাতে হবে।
- Boss-এর personal account, personal message, personal file — agent-এর task-এর বাইরে। Boss না বললে সেখানে যাওয়া যাবে না।
- Client-এর data agent নিজে তৈরি করবে না — নিচের data নিয়ম দেখুন।

## 5. Data নিয়ম

- **কখনো client data invent করা যাবে না।** Client, testimonial, case study, review, statistic — যা নেই, তা বানানো যাবে না।
- **Missing fact-এর নিয়ম:** কোনো তথ্য জানা না থাকলে অনুমান করা যাবে না। সেখানে লিখতে হবে: **"BOSS INPUT REQUIRED"**।
- **dental/medical কখনো target করা যাবে না** — dental/medical/patient-health business সম্পূর্ণ বাদ। এই exclusion সবসময় প্রযোজ্য।
- Prospect-এর email, phone, address অনুমান করে লেখা যাবে না — শুধু verified তথ্য ব্যবহার করা যাবে।
- Pricing internal record only — prospect-কে quote করা যাবে না। Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build — এই তথ্য public content-এ বা prospect reply-তে দেওয়া যাবে না।

## 6. $0 Spend Cap

- Spend cap $0 — Boss-এর explicit অনুমতি ছাড়া কোনো খরচ নয়।
- কোনো agent payment করতে পারবে না, subscription কিনতে পারবে না, paid tool চালু করতে পারবে না।
- Free tier-এর বাইরে যাওয়ার মতো কোনো action নেওয়া যাবে না।
- খরচের প্রয়োজন হলে Boss-কে জানাতে হবে — Boss সিদ্ধান্ত নেবেন।

## 7. সন্দেহজনক Leak হলে কী করতে হবে

কোনো secret leak হয়েছে বলে সন্দেহ হলে — যেমন key ভুল করে file-এ লেখা হয়েছে, repo-তে commit হয়েছে, বা chat-এ paste হয়েছে:

1. **সঙ্গে সঙ্গে Boss-কে জানাও।** দেরি করো না, লুকিও না।
2. **নিজে silently fix করো না।** Key rotate করা, file delete করা, commit revert করা — এগুলো Boss-এর সিদ্ধান্তে হবে।
3. **Rotate via Boss।** Key rotate করতে হলে Boss করবেন বা Boss যাকে বলবেন সে করবে — agent নিজে rotate করবে না।
4. **Leak-এর বিবরণ record করো।** কী leak হয়েছে, কোথায় হয়েছে, কখন ধরা পড়েছে — Boss-কে জানানোর জন্য লিখে রাখো।
5. **একই ভুল আবার যাতে না হয়, সেটা Quality & Security Manager-কে জানাও।**

**মনে রাখবে:** Leak লুকানো leak-এর চেয়ে বড় সমস্যা। Boss-কে জানানোই সঠিক কাজ।

## 8. Voice ও Production সুরক্ষা

- **Live voice stack:** Vapi — Sophia, live receptionist, +1 (947) 223-0244। Production agent-এর prompt বা setting বদলাতে Boss-এর অনুমোদন লাগবে।
- Retell DROPPED 2026-10-26 — Retell-কে production হিসেবে দেখানো যাবে না, Retell-এর credential ব্যবহার করা যাবে না।
- Production deploy, access change, security change — সব restricted approval-এ চলে (`approval-policy.md` দেখুন)।

## 9. এই Policy বদল

- এই security policy বদলাতে হলে Boss-এর অনুমোদন লাগবে।
- কোনো agent নিজে security policy বদলাতে বা শিথিল করতে পারবে না।
