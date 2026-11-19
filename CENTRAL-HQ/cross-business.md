# Cross-Business Collaboration — Talvenor Unified OS

> Status: DRAFT — Boss-এর অনুমোদনের অপেক্ষায়
> তারিখ: 2026-11-19
> মূল নিয়ম: এক business অন্য business-কে সাহায্য করতে পারে — কিন্তু সাহায্য মানেই data ভাগাভাগি নয়। প্রতিটি cross-business কাজ আলাদা internal project, আলাদা track।

## 1. কে কাকে কীভাবে সাহায্য করে

| সেবা দেয় | সেবা পায় | কী সেবা |
|---|---|---|
| Content Studio (03 Media) | Agency (01) | Talvenor social post, Reel script, caption pack, ad creative — Agency-র marketing-এর জন্য |
| Content Studio (03 Media) | Commerce (02) | Vet Kit-এর product creative, sales page copy draft, launch post draft |
| Agency AI Engineering (01) | Commerce (02) | Support automation (যেমন Vet Kit buyer-দের সাধারণ প্রশ্নের উত্তর draft) — শুধু Boss-এর কথায় |
| Central Research Intelligence | তিনটি business | Shared research notes (`~/workspace/research_notes/`) থেকে market research — সবার জন্য একই source |

## 2. প্রতিটি cross-business কাজের নিয়ম

1. **Internal project হিসেবে track:** কাজ + খরচ (সময়/টাকা — এখন $0 spend cap, তাই সময়) প্রতিটি project-এ আলাদা লেখা হয়। যাতে প্রতিটি business-এর আসল খরচ ও লাভ আলাদা বোঝা যায়।
2. **Receiving Chief-এর routing লাগবে:** যে business সেবা পাবে, তার Chief-কে কাজটি route করতে হবে। Chief না জানিয়ে কোনো cross-business কাজ শুরু হয় না।
3. **Gated action-এ Boss-এর gate word লাগবে:** কাজের মধ্যে send / publish / spend / delete থাকলে Boss-এর exact gate word (`ok` / `"post it"` / `send` / `go` / `"upload it"`) ছাড়া তা হয় না — cross-business হলেও নয়।
4. **Data শেয়ার নয়, output শেয়ার:** সেবা দেওয়া business শুধু finished output (যেমন caption, creative, draft) দেয় — অন্য business-এর ভেতরের client data, order বা financial record পড়ে না। নিয়ম: `data-isolation.md`।
5. **DRAFT only, যতক্ষণ approval না হয়:** Cross-business output-ও draft — Boss-এর `ok` ছাড়া publish/send হয় না।

## 3. উদাহরণ (সবই internal project, কখনো automatic নয়)

### উদাহরণ A — Talvenor social post (Agency-র জন্য)

- Content Studio Reel script + caption draft বানায় → Agency Chief-এর কাছে যায় → Boss `ok` দিলে PublishPrep করে → Boss `"post it"` দিলে main chat থেকে post হয়।
- Status: এই flow-এর অংশগুলো BUILT (ContentPlanner, CaptionWriter, VideoProducer, PublishPrep — সব draft-only); post কখনো automatic নয়।

### উদাহরণ B — Vet Kit-এর product creative (Commerce-র জন্য)

- Content Studio Vet Kit-এর creative draft বানায় → Products Chief-এর কাছে যায় → Boss `ok` দিলে ব্যবহার হয়।
- Status: NOT STARTED — Gate 0 NOT passed বলে kit-এর কাজই BLOCKED; creative-এর কাজ Gate 0-এর পর।

### উদাহরণ C — Support automation (Commerce-র জন্য)

- Agency AI Engineering Commerce-র support automation draft বানায় — শুধু Boss-এর কথায়।
- Status: NOT STARTED — Boss-এর নির্দেশ বাকি; কোনো automation live নয় (n8n READY NOT LIVE)।

## 4. যা করা যাবে না (NOT ALLOWED)

| নিষেধ | কেন |
|---|---|
| Silent cross-read (চুপচাপ অন্য business-এর data পড়া) | Data isolation ভাঙে — Boss-এর explicit permission ছাড়া নয়। |
| Cross-business send (এক business থেকে অন্য business-এর নামে পাঠানো) | Send gate Boss-এর — কোনো business নিজে অন্যের হয়ে পাঠাতে পারে না। |
| Automatic data sharing (এক business-এর client/order/finance record অন্য business-এ copy করা) | প্রতিটি business-এর record আলাদা থাকবে — `data-isolation.md` §3। |
| Cross-business publish (এক business-এর content অন্য business-এর channel-এ publish করা) | Publish gate Boss-এর `"post it"` — channel যারই হোক, Boss-এর কথায় হয়। |
| খরচ লুকানো (cross-business কাজের খরচ এক business-এর হিসাবে চাপানো) | প্রতিটি project-এর খরচ আলাদা track হয় — §2.1। |

## 5. বর্তমান অবস্থা (সত্য)

- Cross-business কাজের কোনো live উদাহরণ এখনো হয়নি — সব উদাহরণ উপরে DRAFT/plan হিসেবে লেখা।
- Content Studio Agency-কে সাহায্য করার flow-এর অংশগুলো BUILT (draft-only); Commerce-কে সাহায্য করার কাজ NOT STARTED (Gate 0 BLOCKED)।
- কোনো cross-business automation live নয়।
