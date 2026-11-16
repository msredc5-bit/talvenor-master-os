# Research Section — PA Vet Clinic List

**Purpose (উদ্দেশ্য):** PA vet list-কে ১০০টি যাচাই করা independent clinic-এর দিকে বাড়ানো — official website প্রথমে, নইলে directory listing; contact details কখনো বানানো হয় না।

## Staff roster (কর্মী তালিকা)

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Clinic Researcher | `agents/clinic_researcher.py` (`ClinicResearcherAgent`, task `clinic_research`) | `skills/clinic-researcher.md` | — (none) | Existing role — section agent হিসেবে নতুন file |

## How work flows (কাজের ধারা)

1. Main CEO Bot → Products Chief → `clinic_research` (existing ROUTING branch)।
2. Section agent `ClinicResearcherAgent` `pa-vet-clinics.csv` (read-only) পড়ে অবস্থা জানায়: row সংখ্যা, শহর ভাগ, কয়টার public email আছে; যাচাইয়ের নিয়ম লেখে (official website প্রথমে, chain বাদ, "Not publicly listed")।
3. নতুন clinic যাচাইয়ের plan: README-র শহর plan (Pittsburgh আশেপাশে, Harrisburg আশেপাশে, Lehigh Valley, Bucks/Montgomery, Pittsburgh suburbs, Central PA ছোট শহর)।
4. এই section কাউকে মেইল/ফোন করে না — এটা শুধু list, outreach নয়।

## Gates (গেট)

- List বানানোয় কোনো gate নেই — এটা নিরাপদ কাজ।
- কিন্তু list থেকে কাউকে মেইল করতে Boss-এর `send` লাগে, আর email channel এখন PAUSED।

## Honest limits (সৎ সীমা)

- **PA list 39/100** (যাচাই করা, 2026-11-16) — বাকি 61 Gate 0-র পরে পূর্ণ করা হবে।
- 39-এর মধ্যে public email আছে 8টার; বাকিদের "Not publicly listed"।
- Chain বাদ: Banfield, VCA, Vetco, BluePearl, Thrive, PetVet365, PetVet Care Centers network।
- **Gate 0 NOT PASSED, kit 0/6 built, sale 0** — list বাড়ানো Gate 0-র বাইরে করা যায়, তবে plan অনুযায়ী বাকি 61 Gate 0-র পরে।
- কোনো agent file লেখে না (CSV overwrite নয়), network ছোঁয় না, contact details বানায় না।
