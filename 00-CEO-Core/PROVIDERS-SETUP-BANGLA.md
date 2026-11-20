# Provider Setup — Brain-এ যেকোনো LLM লাগানো (সহজ গাইড)

Brain এখন mock। Live করতে হলে নিচের ৩টা জিনিস লাগবে — একটা provider-এর
key + config-এ সেই provider বাছা + brain "live" করা। Key কখনো কোনো
file-এ লিখবেন না — শুধু environment variable-এ।

## ১. Provider-গুলো (৭টা) — key কোথায়, env var কোনটা

| Provider | Key কোথায় পাবেন | Env var | Default model |
|---|---|---|---|
| Meta (Muse Spark) | আগেই connect করা আছে (connector) — নতুন key লাগে না | — (connector) | muse-spark-1.3 |
| OpenAI (ChatGPT) | https://platform.openai.com/api-keys | OPENAI_API_KEY | gpt-4o |
| Claude (Anthropic) | https://console.anthropic.com/settings/keys | ANTHROPIC_API_KEY | claude-sonnet-4-5 |
| Gemini (Google) | https://aistudio.google.com/apikey | GEMINI_API_KEY | gemini-2.5-flash |
| Kimi (Moonshot) | https://platform.moonshot.ai | MOONSHOT_API_KEY | kimi-k2.5 |
| Grok (xAI) | https://console.x.ai | XAI_API_KEY | grok-4 |
| OpenRouter (auto-router) | https://openrouter.ai/keys | OPENROUTER_API_KEY | openrouter/free |

## ২. Model বদলানো — config-এ এক লাইন

`00-CEO-Core/config.json`-এ `providers` section-এ প্রতিটা provider-এর
`models` list আছে। প্রথম model-টাই default। নিজের পছন্দের model
বসাতে চাইলে দুইভাবে:

- Chain-এ নাম ধরে: `"fallback_chain": ["openai:gpt-4o-mini", "meta", "mock"]`
- শুধু provider বদলে: `"brain_provider": "gemini"` (তখন default model চলে)

নতুন model-এর নাম vendor-এর model list থেকে নিন — ভুল নাম দিলে
provider "model not found" error দিয়ে পরের provider-এ যাবে, তারপর mock।

## ৩. OpenRouter — পুরো system (step by step)

OpenRouter একটা দরজা — একটা key দিয়ে অনেক model চালানো যায়।

**Step 1 — Account:** https://openrouter.ai-তে যান, Google/GitHub দিয়ে
sign up করুন (free, card লাগে না)।

**Step 2 — Key বানানো:** https://openrouter.ai/keys-তে যান → "Create API Key"
→ নাম দিন (যেমন Talvenor) → key-টা copy করুন। Key একবারই দেখায় —
হারালে আবার নতুন বানাতে হবে।

**Step 3 — Key PC-তে বসানো (file-এ নয়):** আপনার PC-তে terminal
খুলে এই command দিন (Windows PowerShell):

```
setx OPENROUTER_API_KEY "আপনার-key-এখানে"
```

তারপর terminal বন্ধ করে আবার খুলুন — নতুন terminal-এ key কাজ করবে।
(Mac/Linux হলে: `export OPENROUTER_API_KEY="আপনার-key-এখানে"` — তবে
সেটা শুধু ওই terminal-এর জন্য; স্থায়ী করতে `.bashrc`/`.zshrc`-এ লিখুন।)

**Step 4 — Model বাছা:** config-এ দুইটা উপায় আছে।

- `openrouter/free` (default) — auto-router: OpenRouter নিজে প্রতি
  request-এ একটা fitting free model বেছে নেয়। Boss-কে model-এর নাম
  মনে রাখতে হয় না।
- নাম ধরে — যেমন `nvidia/nemotron-3-ultra-550b-a55b:free`। `:free`
  দিয়ে শেষ হওয়া model-গুলো free।

**Step 5 — Free-র limit জেনে রাখুন:** free model-এ ২০ request/min,
৫০ request/day। একবার $10 lifetime credit কিনলে ১,০০০/day হয়।
Limit গোনা হয় request-এ, token-এ নয়। Free model বদলায় (আসে/যায়) —
তাই fallback chain-এ একাধিক provider রাখুন, যেমন
`["openrouter", "meta", "mock"]`।

## ৪. Brain live করা — শেষ step (শুধু Boss-এর কথায়)

১. উপরের মতো key env var-এ বসান।
২. `00-CEO-Core/config.json`-এ `"brain": "live"` করুন আর
   `"fallback_chain"`-এ পছন্দের provider সাজান।
৩. Terminal-এ `python3 scripts/check_live_brain.py --live` দিয়ে একটা
   ছোট live probe করুন — সফল হলে তবেই brain live।

## ৫. সত্য অবস্থা (এখন)

- কোনো provider-এর key-ই এখনো দেওয়া হয়নি — Meta-র key-ও প্রমাণিত নয়
  (2026-11-20-এর probe tunnel 403-এ আটকেছে)।
- Brain এখনো mock, phase 9 / v0.9.0। কোনো live call হয়নি, $0 খরচ।
- Key ছাড়া brain চালু করলে adapter চুপচাপ live সাজে না — কারণ লিখে
  mock draft দেয়।
