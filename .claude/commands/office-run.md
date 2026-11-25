---
description: Run one Talvenor Master OS office task (draft only, never sends)
---

Run one office task through the Main CEO Bot. Usage:

```
/office-run agency caption_write {"title": "Caption for Monday reel"}
```

Arguments: `$ARGUMENTS` = `<business> <task> <json-input>`. Business is
`agency`, `products`, or `content`. If any argument is missing, ask Boss
for it in Bengali (one question) instead of guessing.

Steps:
1. Run from the repo folder:
   `python scripts\run_office.py --business <business> --task <task> --input '<json>'`
2. Show Boss the result in Bengali, short.
3. If the result is a draft awaiting approval, say so and stop. Never
   send, publish, or schedule it — that needs Boss's exact gate word
   (`post it`, `send`, `pathao`).
4. If the runner reports an error, show the error in one line and stop.
   Do not retry with different arguments.
