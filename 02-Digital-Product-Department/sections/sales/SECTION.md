# Sales Section — Kit Outreach DRAFTs

**Purpose (উদ্দেশ্য):** যাচাই করা PA clinic-দের জন্য Vet Kit outreach email-এর DRAFT লেখা — শুধু DRAFT, পাঠানো নয়।

## Staff roster (কর্মী তালিকা)

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Kit Sales | `agents/kit_sales.py` (`KitSalesAgent`, task `kit_sales`) | `skills/kit-sales.md` | `send` | **NEW** role (Phase 7) |

## How work flows (কাজের ধারা)

1. Main CEO Bot → Products Chief → `kit_sales` (Chief-এর `SECTION_ROUTING` branch, Phase 7, নতুন) → `KitSalesAgent`।
2. Agent `pa-vet-clinics.csv` (read-only) থেকে verified clinic নেয়: payload-এ `clinic_name` থাকলে CSV-তে মিলিয়ে দেখা; না থাকলে প্রথম emailable row (public email আছে) ব্যবহার করা — এখন Indy Veterinary Care, Philadelphia।
3. Draft লেখা (plain US English): pain (AAHA ~11% × AVMA ~$200), kit-এর ৬ অংশের নাম, CTA (booking link + phone)। Price জায়গায় placeholder — Boss confirm না করলে $49 লেখা হয় না।
4. প্রতিটা output-এর মাথায় prominent warning: "DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go"।
5. Gated `send` চাইলে agent চালানো হয় না — ApprovalGateway-এ PENDING request লেখা হয়।

## Gates (গেট)

- পাঠাতে Boss-এর `send` লাগে — exact word ছাড়া কিছু পাঠানো হয় না।
- Email channel এখন **PAUSED** (2026-11-14 থেকে — SPF/DMARC DNS fix Boss-এর হাতে বাকি)।

## Honest limits (সৎ সীমা)

- **Gate 0 NOT PASSED** — kit বানানো হয়নি (0/6), sale 0। Draft launch-এর পরে ব্যবহারের জন্য।
- **PA list 39/100** — 39-এর মধ্যে public email আছে 8টার; public email না থাকলে ("Not publicly listed") addressed email draft লেখা যায় না।
- কোনো clinic-কে দুইবার মেইল করা যাবে না (launch-এর সময়)।
- কোনো agent মেইল পাঠায় না, sale চিহ্নিত করে না, contact details বানায় না, file লেখে না, network ছোঁয় না।
