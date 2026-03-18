import requests
import time
from pushbullet import Pushbullet

# ---------- הגדרות ----------
PUSHBULLET_API_KEY = "o.ZkUj5CKmfXmnTIfrja1Mfws7miqFcpVr"
pb = Pushbullet(PUSHBULLET_API_KEY)

PERCENT_THRESHOLD = 10      # אחוז עלייה להתראה
CHECK_INTERVAL = 60         # בדיקה כל 60 שניות
TIME_WINDOW = 15 * 60       # 15 דקות בשניות
price_history = {}

# ---------- פונקציה לשליחת התראה ----------
def send_push(title, body):
    pb.push_note(title, body)

# ---------- לולאת סריקה ----------
while True:
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers?category=linear").json()
        current_time = time.time()

        for coin in r["result"]["list"]:
            symbol = coin["symbol"]
            price = float(coin["lastPrice"])

            if symbol not in price_history:
                price_history[symbol] = [(current_time, price)]
                continue

            price_history[symbol].append((current_time, price))
            price_history[symbol] = [(t, p) for t, p in price_history[symbol] if t >= current_time - TIME_WINDOW]

            old_price = price_history[symbol][0][1]
            change = ((price - old_price) / old_price) * 100

            if change >= PERCENT_THRESHOLD:
                send_push(f"{symbol} 🔥 +{change:.2f}%", f"מחיר נוכחי: {price}")
                price_history[symbol] = [(current_time, price)]

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("שגיאה:", e)
        time.sleep(30)