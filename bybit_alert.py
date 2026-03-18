import requests
import time
from pushbullet import Pushbullet

# ===== הגדרות =====
PUSHBULLET_API_KEY = "o.ZkUj5CKmfXmnTIfrja1Mfws7miqFcpVr"
BYBIT_URL = "https://api.bybit.com/v5/market/tickers?category=linear"

PERCENT_THRESHOLD = 10
CHECK_INTERVAL = 60
TIME_WINDOW = 15 * 60

pb = Pushbullet(PUSHBULLET_API_KEY)
price_history = {}

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send_push(title, body):
    try:
        pb.push_note(title, body)
        print("התראה נשלחה:", title, flush=True)
    except Exception as e:
        print("שגיאה בפוש:", e, flush=True)

print("BOT STARTED", flush=True)

while True:
    try:
        response = requests.get(BYBIT_URL, headers=headers, timeout=15)

        if response.status_code != 200:
            print("שגיאת HTTP:", response.status_code, flush=True)
            time.sleep(10)
            continue

        try:
            data = response.json()
        except:
            print("שגיאה ב-JSON", flush=True)
            time.sleep(10)
            continue

        coins = data["result"]["list"]
        current_time = time.time()

        for coin in coins:
            try:
                symbol = coin["symbol"]
                price = float(coin["lastPrice"])

                if symbol not in price_history:
                    price_history[symbol] = [(current_time, price)]
                    continue

                price_history[symbol].append((current_time, price))

                price_history[symbol] = [
                    (t, p) for t, p in price_history[symbol]
                    if t >= current_time - TIME_WINDOW
                ]

                old_price = price_history[symbol][0][1]
                change = ((price - old_price) / old_price) * 100

                print(f"{symbol}: {change:.2f}%", flush=True)

                if change >= PERCENT_THRESHOLD:
                    send_push(f"{symbol} 🔥 +{change:.2f}%", f"מחיר: {price}")
                    price_history[symbol] = [(current_time, price)]

            except Exception as coin_error:
                print("שגיאה במטבע:", coin_error, flush=True)

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("שגיאה כללית:", e, flush=True)
        time.sleep(10)
