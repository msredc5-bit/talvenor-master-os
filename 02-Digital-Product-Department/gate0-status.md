# Gate 0 — Lemon Squeezy Signup Test

**Status: NOT PASSED (2026-11-16)**

## Gate 0 কী

Vet Kit বানানোর আগে প্রথমে যাচাই করতে হবে: Lemon Squeezy-তে
Bangladesh থেকে individual হিসেবে signup + payout হয় কি না।
নতুন signup-দের triage করা হয় — Stripe Managed Payments-এর দিকে
পাঠাতে পারে, যেখানে Bangladesh বাদ। তাই আগে test, তারপর build।

## Boss-এর step (~15 min, $0)

1. lemonsqueezy.com-এ যান।
2. Individual হিসেবে signup করুন (MAINUDDIN LLC নয় — LLC US-registered,
   US bank নেই বলে individual-ই সঠিক পথ)।
3. Payout method দেখুন — BD bank payout দেখা যায় কি না।
4. ফলাফল জানান: পাস / ফেল / কী বলল (screenshot দিলে ভালো হয়)।

## ফলাফল রেকর্ড করা (Boss-এর কাজ)

- **3D office dashboard** (`ceo-office-dashboard` artifact) — Gate 0-র
  ঘরে ফলাফল লেখা যায়। Boss সেখানে জানালে Elora এই ফাইল + Chief
  module-এর Gate 0 state আপডেট করবে।
- এই ফাইলের উপরের **Status লাইনে** PASSED লেখা থাকলেই Chief Gate 0
  পাস ধরবে — নইলে fail-closed: NOT PASSED। Chief-এর কোড নিজে থেকে
  Gate 0 পাস বলে ধরে না।

## ফলাফল অনুযায়ী

- **পাস:** Phase 2-র বাকি কাজ শুরু — PA list 100-এ পূর্ণ করা, Gate 1
  (cadence AAHA/PetDesk যাচাই), kit-এর ৬ অংশ বানানো, store listing,
  launch।
- **ফেল (triage/blocked):** Backup rail test — **Polar** (BD seller/payout
  list-এ আছে, Stripe Connect Express)। Polar-ও না হলে **Gumroad**
  (BD bank payout আছে, individual হিসেবে register করতে হবে)।
- **সব rail বন্ধ:** Product track পুরো KILL — kit বানানো হবে না, Boss-কে
  জানানো হবে। টাকা পাওয়ার উপায় ছাড়া product বানানো যাবে না।

## সত্য অবস্থা (2026-11-16)

- Gate 0 NOT PASSED — test হয়নি।
- তবু Phase 2-এ যা করা গেছে (Gate 0-র বাইরে, honest কাজ): kit
  **blueprint** (`kit-outline.md` — নকশা, kit নয়), PA list **39/100**
  (যাচাই করা), Products Chief module REAL।
- Kit-এর ৬ অংশ বানানো হয়নি, sale 0, launch হয়নি — Gate 0-র পরে।
