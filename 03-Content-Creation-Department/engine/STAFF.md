# Content Engine — Staff Roster (STAFF.md)

**Engine:** Content Creation Engine (Creator OS) — `03-Content-Creation-Department/engine/`
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Chief:** `../chief_of_staff_content.py` — REAL (Phase 3), ৬ task type → ৬ Creator OS worker
**Brain:** MockLLM (mock brain, $0) — সব output `[MOCK DRAFT]`, DRAFT ONLY
**১৩ stage:** REAL **0** / MOCK **10** / BLOCKED **3** (stage 4 video, stage 5 edit, stage 9 upload)

**নিয়ম (সবার জন্য):** কোনো staff publish করে না, upload করে না, mail পাঠায় না, খরচ করে না, delete করে না। Gate word শুধু Boss-এর মুখে — "ok" / "post it" / "upload it" / "send" / "go"। কোনো auto-approve নেই। $0 spend cap। কোনো invented client / stat / testimonial / price নয়। Brand শুধু Talvenor।

---

## 1. Topic Researcher (TopicResearcher)

- **Worker:** `TopicResearcher` — `~/workspace/creator-os-combined/src/creator_workers.py` (task_kind `topic_research`, gate `ok`)
- **কী করে:** CEO-র সিদ্ধান্ত নিয়ে niche + audience-এর জন্য ৩টি content topic বাছে — প্রতিটার angle, কেন fit করে, আর পরের research step কী। Stage 1-research + 0a-niche (`tools/niche_score.py`, ৪ axis-এ ১–১০ score) + 2a-concept (`tools/concept_score.py`, ৩–৫ concept, ১–১০ score)।
- **Input:** niche (যেমন "AI Tools & Tutorials"), audience (US viewers), Boss-এর দেওয়া trend/topic থাকলে সেটা।
- **Output:** ৩টি topic draft — angle + fit + next-research-step সহ, `[MOCK DRAFT]` লেবেল।
- **Gate:** `ok` — Boss-এর "ok" ছাড়া topic final নয়।
- **সৎ সীমা:** Mock brain — আসল trend data পড়ে না; score scaffold মাত্র। Niche জানা থাকলে 0a stage skip হয়।

## 2. Script Writer (ScriptWriter)

- **Worker:** `ScriptWriter` — `~/workspace/creator-os-combined/src/creator_workers.py` (task_kind `script_write`, gate `ok`)
- **কী করে:** বাছা topic-কে script বানায় — প্রথম ২ সেকেন্ডে hook, একটা পরিষ্কার idea, simple CTA। Method: `youtube-skills/yt-script/` — ২১ formula থেকে ৫টি hook লেখা, `hookscore.py` দিয়ে score করা, সেরা ২টি দেখানো; প্রথম ১৫ সেকেন্ডে title-এর promise confirm + একটা খোলা প্রশ্ন + payoff-এর প্রমাণ।
- **Input:** topic, format (short video / long video), VOICE.md।
- **Output:** Script draft — hook options (score সহ) + full spoken script, `[MOCK DRAFT]`।
- **Gate:** `ok` — Boss-এর "ok" ছাড়া script ব্যবহার করা যাবে না।
- **⚠️ সৎ সীমা — VOICE.md DRAFT:** `~/workspace/creator-os-combined/youtube-skills/VOICE.md` এখনো DRAFT — Boss ঠিক না করা পর্যন্ত কোনো script-ই "final" নয়। Boss-এর কোনো YouTube video এখনো নেই, তাই copy করার মতো আসল transcript-ও নেই। Boss live English বলেন না — read-aloud script-এ প্রতিটা English line-এর নিচে Bengali transliteration লাগে। Week 1 long video ("Google's Nano Banana 2 Is Free - But Is It Good?") READY TO RECORD, কিন্তু verdict **[FILL AFTER TEST]** — Boss-এর OBS recording-এর ৫ test না দেখে verdict লেখা হবে না।

## 3. Visual Producer (VisualProducer)

- **Worker:** `VisualProducer` — `~/workspace/creator-os-combined/src/creator_workers.py` (task_kind `visual_produce`, gate `ok`)
- **কী করে:** Visual plan বানায় — shot list, thumbnail idea, on-screen text (verbatim, ছোট, readable)। Stage 3-visual-pack (`youtube-skills/yt-package/title.py` — title + thumbnail একসাথে lint করা) আর stage 4-video-র production plan + missing-inputs checklist।
- **Input:** topic, format, script (থাকলে), footage / voiceover line / GPU নাম (থাকলে)।
- **Output:** Visual plan draft + stage 4-এর missing-inputs list। `video_file` সবসময় **None** — এই role video file বানায় না।
- **Gate:** `ok`।
- **সৎ সীমা:** Stage 4 **BLOCKED** — real footage / OBS recording নেই, Boss-এর PC GPU-র নাম **2026-11-01 থেকে জানা যায়নি** (true AI video motion-এর জন্য লাগে), AI video generation এখানে **REGION-BLOCKED — retry করা হয় না**। Default stills + Ken Burns motion = সত্যিকারের motion নয়। কোনো shot film করা না গেলে সেটা বলতে হয়, fake করা যাবে না।

## 4. Caption Writer (CaptionWriter)

- **Worker:** `CaptionWriter` — `~/workspace/creator-os-combined/src/creator_workers.py` (task_kind `caption_write`, gate `ok`)
- **কী করে:** Platform অনুযায়ী caption + hashtag pack লেখে — প্রথম line-এ hook, একটা CTA, hashtag (Instagram ৫–৮, LinkedIn ৩, Facebook ০–২)। Stage 6-caption-seo (`youtube-skills/yt-seo/` — description + tags, আসল search query-এর জন্য)।
- **Input:** topic, platform (YouTube / Facebook / Instagram / LinkedIn), video/post-এর draft।
- **Output:** Caption pack draft — platform-wise caption + hashtag + CTA, `[MOCK DRAFT]`।
- **Gate:** `ok`।
- **সৎ সীমা:** Caption **line-level** — word-level karaoke নয় (Creator OS-এর সীমা)। কোনো platform-এ post করা এই role-এর কাজ নয়।

## 5. Publish Prep (PublishPrep)

- **Worker:** `PublishPrep` — `~/workspace/creator-os-combined/src/creator_workers.py` (task_kind `publish_prep`, gate `post it`)
- **কী করে:** Post-টা publish-এর জন্য তৈরি করে — final checklist: hook, readable text, কোনো invented claim নেই, platform, best posting time। Stage 7-publish-prep। Publish করে না — শুধু checklist draft দেয়।
- **Input:** finished post/video draft, caption pack, platform, posting time।
- **Output:** Publish-prep checklist draft, `ready_to_publish: False`।
- **Gate:** **`post it`** (video upload-এর জন্য **`upload it`**) — Boss-এর exact word ছাড়া কিছু publish/upload হয় না, আর সেটাও Boss নিজে করেন।
- **সৎ সীমা:** Upload stage 9 **DEFAULT OFF** — লাগে তিনটাই: Boss-এর "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর নিজের YouTube credential (OAuth)। এই engine কখনো `upload_youtube.py` চালায় না। LinkedIn = Boss নিজে post করেন (personal profile)।

## 6. Performance Tracker (PerformanceTracker)

- **Worker:** `PerformanceTracker` — `~/workspace/creator-os-combined/src/creator_workers.py` (task_kind `performance_track`, gate `ok`)
- **কী করে:** Performance report-এর **template/setup** বানায় — কোন metric কোথা থেকে নিতে হবে, best/worst comparison, পরের সপ্তাহে একটা change। Stage 8-report (`youtube-skills/yt-retention/retention.py` — retention CSV পড়ে hook leak খোঁজা)।
- **Input:** topic/video, Boss-এর পাঠানো আসল platform সংখ্যা (থাকলে)।
- **Output:** Report template draft — metric-এর list + comparison format + একটা change, `[MOCK DRAFT]`।
- **Gate:** `ok`।
- **সৎ সীমা:** কোনো video এখনো publish হয়নি — metric **0** (subs 0, hours 0, videos 0)। সংখ্যা কখনো estimate করা হয় না — শুধু Boss-এর পাঠানো আসল platform সংখ্যা ব্যবহার করা হয়। Performance Analyst-এর থেকে আলাদা: Tracker setup/template বানায়, Analyst আসল সংখ্যা বিশ্লেষণ করে।

## 7. Content Planner (ContentPlanner)

- **Worker:** no worker — Chief-level role। Method-এর source: `youtube-skills/yt-plan/SKILL.md` (সপ্তাহের plan — anchor video + cheap video, Boss-এর আসল ঘণ্টা জিজ্ঞেস করে) + `scripts/loop_next.py` (stage 10-next-plan — আগের report পড়ে পরের brief) + `../pipeline.md`।
- **কী করে:** Weekly / monthly content plan বানায় — কী post হবে, কখন, কোন order-এ, Boss-এর আসল capacity অনুযায়ী। Talvenor weekly social plan (৫ post) আর ToolPilot-এর rhythm (১ long/week + ২ Shorts/week) — দুটোই এই role-এর কাজ।
- **Input:** আগের সপ্তাহের report (থাকলে), Boss-এর দেওয়া ঘণ্টা, half-made content-এর list, niche/topic।
- **Output:** Weekly plan draft — pillar + format + platform + posting time-এর table, `[MOCK DRAFT]`।
- **Gate:** `ok` — Boss-এর "ok" বা edit ছাড়া plan চলে না।
- **সৎ সীমা:** **Nov 16–22 Talvenor weekly plan (৫ post: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn) 2026-11-15 18:00-তে দেওয়া হয়েছে — Boss-এর "ok" এখনো বাকি।** Nov 9–15-এ কিছু post হয়নি (plan approve হয়নি)। Plan-এর ভেতরে কোনো metric/claim invent করা হয় না।

## 8. Performance Analyst (PerformanceAnalyst)

- **Worker:** no worker — Chief-level role। Method-এর source: `youtube-skills/yt-retention/SKILL.md` (retention graph — hook leak, প্রথম ৩০ সেকেন্ডে ২৫%-এর নিচে healthy) + `youtube-skills/yt-audit/` + PerformanceTracker-এর template + `../pipeline.md` stage 8-report।
- **কী করে:** **Publish হওয়া** content-এর আসল performance বিশ্লেষণ করে — Boss-এর পাঠানো আসল metric (views, retention, CTR, subs) পড়ে কোথায় viewer ছাড়ে, কেন ছাড়ে, আর পরের video-তে ঠিক কী বদলাতে হবে, সেটা লেখে।
- **Input:** Boss-এর পাঠানো আসল platform সংখ্যা / retention CSV / YouTube Studio export।
- **Output:** Analysis draft — কোথায় leak, কারণ, আর পরের সপ্তাহের একটা concrete change।
- **Gate:** `ok` — analysis Boss-কে দেখানো হয়, Boss সিদ্ধান্ত নেন।
- **সৎ সীমা:** **কোনো video এখনো publish হয়নি, তাই বিশ্লেষণ করার মতো আসল metric 0 — এই role-এর এখনো কোনো আসল কাজ হয়নি।** সংখ্যা ছাড়া analysis লেখা হয় না; Boss metric না পাঠালে role শুধু "metric বাকি" বলে থামে। Performance Tracker-এর থেকে আলাদা: Tracker tracking-এর setup/template বানায়, Analyst আসল সংখ্যা থেকে সিদ্ধান্ত বের করে।

---

## Role → Chief task type map

| Staff | Chief task type | Worker |
|---|---|---|
| Topic Researcher | `content_plan` | TopicResearcher |
| Script Writer | `script_write` | ScriptWriter |
| Visual Producer | `video_produce` | VisualProducer |
| Caption Writer | `caption_write` | CaptionWriter |
| Publish Prep | `publish_prep` | PublishPrep |
| Performance Tracker | `performance_track` | PerformanceTracker |
| Content Planner | — (Chief-level) | no worker |
| Performance Analyst | — (Chief-level) | no worker |

**Staff সংখ্যা: ৮।** Worker আছে ৬ জনের, Chief-level role ২টি (Content Planner, Performance Analyst)।
