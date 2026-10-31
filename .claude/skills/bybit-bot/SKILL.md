---
name: bybit-bot
description: Work on the Bybit price-alert bot in this repo (bybit_alert.py). Use when changing alert logic, thresholds, time window, Pushbullet notifications, adding features (drops, filters, cooldowns), checking the Bybit API, or preparing a deploy of the worker.
---

# Bybit alert bot

## What the bot does
`bybit_alert.py` is a single long-running worker (`Procfile`: `worker: python bybit_alert.py`):
1. Every `CHECK_INTERVAL` seconds (60) it fetches all linear (USDT perpetual) tickers from
   `https://api.bybit.com/v5/market/tickers?category=linear`.
2. For each symbol it keeps `(time, price)` samples in `price_history`, trimmed to `TIME_WINDOW` (15 min).
3. It compares the current price to the oldest sample in the window. If the rise is ≥ `PERCENT_THRESHOLD` (10%),
   it sends a Pushbullet note and resets that symbol's history so the same move doesn't alert again.

History is in memory only, so after every restart the bot needs a full `TIME_WINDOW` before it can alert.
Dependencies are in `requirements.txt` (`requests`, `pushbullet.py`).

## Rules when changing the code
- **Secrets:** never put API keys in the code or in commits. Read them from environment variables, e.g.
  `os.environ["PUSHBULLET_API_KEY"]`, and set them in the hosting platform's config vars.
  If a key appears hard-coded, move it to an env var and tell the user to **revoke and regenerate** it,
  because it is already in git history.
- Keep the bot a single worker process with `flush=True` prints (hosting logs depend on it).
- Keep every network call wrapped with a timeout and a try/except so one bad response can't kill the loop.
- Settings belong in the "הגדרות" block at the top of the file. Prefer env-var overrides with the current values as defaults.
- Bybit returns `retCode` / `retMsg` in the JSON. A `retCode` other than 0 is an error even with HTTP 200.
- Don't send a push for every coin on every loop. Keep the reset/cooldown behaviour that prevents alert spam.
- Don't print every symbol on every loop unless the user wants it: with hundreds of symbols it floods the logs.

## Testing without sending notifications
- Syntax check: `python -m py_compile bybit_alert.py`
- API check (no push): `python .claude/skills/bybit-bot/scripts/check_bybit.py [top_n]`
  prints the symbol count and the top movers by 24h change.
  In a cloud session, api.bybit.com may be blocked by the network policy. If it is, say so and don't treat it as a bug in the code.
- For logic changes, test the change-calculation / history-trimming logic with fake price data
  (patch `requests.get` and `Pushbullet`) instead of calling the real APIs.

## Deploy
Push to the branch the hosting service deploys from (the Procfile targets Heroku/Railway-style worker dynos).
Make sure the env vars exist there before deploying code that reads them.

## Communicating
The user writes in Hebrew, so answer in Hebrew. Existing log/alert strings in the code are in Hebrew. Keep that style.
