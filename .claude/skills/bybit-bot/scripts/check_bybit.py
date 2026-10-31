"""Dry-run check: fetch Bybit linear tickers once and print the biggest movers.

Sends no Pushbullet notifications. Uses Bybit's own 24h change field
(price24hPcnt), since a single fetch has no 15-minute history.

Usage: python .claude/skills/bybit-bot/scripts/check_bybit.py [top_n]
"""
import sys

import requests

URL = "https://api.bybit.com/v5/market/tickers?category=linear"


def main():
    top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    try:
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    except requests.exceptions.RequestException as e:
        sys.exit(
            f"Could not reach api.bybit.com ({type(e).__name__}).\n"
            "In a cloud session the network policy may block this host; "
            "allow api.bybit.com in the environment's network settings, or run locally."
        )
    print("HTTP", r.status_code)
    r.raise_for_status()
    data = r.json()
    if data.get("retCode") != 0:
        sys.exit(f"Bybit error: {data.get('retCode')} {data.get('retMsg')}")

    coins = data["result"]["list"]
    print(f"{len(coins)} symbols returned")

    movers = []
    for c in coins:
        try:
            movers.append((float(c["price24hPcnt"]) * 100, c["symbol"], c["lastPrice"]))
        except (KeyError, ValueError):
            continue
    movers.sort(reverse=True)

    print(f"\nTop {top_n} by 24h change:")
    for pct, sym, price in movers[:top_n]:
        print(f"  {sym:<20} {pct:+7.2f}%  price={price}")


if __name__ == "__main__":
    main()
