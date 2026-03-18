import requests
import time
from pushbullet import Pushbullet

# ===== הגדרות =====
PUSHBULLET_API_KEY = "o.ZkUj5CKmfXmnTIfrja1Mfws7miqFcpVr"
BYBIT_URL = "https://api.bybit.com/v5/market/tickers?category=linear"

PERCENT_THRESHOLD = 10      # כמה אחוז עלייה להתרעה
CHECK_INTERVAL = 60         # כל כמה שניות לבדוק
TIME_WINDOW = 15 * 60       # 15 דקות

pb = Pushbullet(PUSHBULLET_API_KEY)
price_history = {}


def send_push(title: str, body: str) -> None:
    try:
        pb.push_note(title, body)
        print(f"נשלחה התראה: {title} | {body}", flush=True)
    except Exception as e:
        print(f"שגיאה בשליחת Pushbullet: {e}", flush=True)


def fetch_tickers():
    try:
        headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(BYBIT_URL, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"שגיאת HTTP מ-Bybit: {response.status_code}", flush=True)
            return None

        try:
            data = response.json()
        except Exception as e:
            print(f"שגיאה בפענוח JSON: {e}", flush=True)
            return None

        if not isinstance(data, dict):
            print("תגובה לא תקינה מ-Bybit", flush=True)
            return None

        if data.get("retCode") != 0:
            print(f"שגיאת API מ-Bybit: {data}", flush=True)
            return None

        result = data.get("result", {})
        ticker_list = result.get("list", [])

        if not isinstance(ticker_list, list):
            print("השדה result.list לא תקין", flush=True)
            return None

        return ticker_list

    except requests.exceptions.Timeout:
        print("Timeout בבקשה ל-Bybit", flush=True)
        return None
    except requests.exceptions.RequestException as e:
        print(f"שגיאת רשת מול Bybit: {e}", flush=True)
        return None
    except Exception as e:
        print(f"שגיאה לא צפויה ב-fetch_tickers: {e}", flush=True)
        return None


print("BOT STARTED", flush=True)

while True:
    try:
        ticker_list = fetch_tickers()

        if ticker_list is None:
            time.sleep(10)
            continue

        current_time = time.time()

        for coin in ticker_list:
            try:
                symbol = coin.get("symbol")
                last_price = coin.get("lastPrice")

                if not symbol or last_price is None:
                    continue

                price = float(last_price)

                if symbol not in price_history:
                    price_history[symbol] = [(current_time, price)]
                    continue

                price_history[symbol].append((current_time, price))

                # משאיר רק נתונים מה-15 דקות האחרונות
                price_history[symbol] = [
                    (t, p)
                    for t, p in price_history[symbol]
                    if t >= current_time - TIME_WINDOW
                ]

                if not price_history[symbol]:
                    price_history[symbol] = [(current_time, price)]
                    continue

                old_price = price_history[symbol][0][1]

                if old_price <= 0:
                    continue

                change = ((price - old_price) / old_price) * 100

                print(f"{symbol}: {change:.2f}%", flush=True)

                if change >= PERCENT_THRESHOLD:
                    send_push(
                        f"{symbol} 🔥 +{change:.2f}%",
                        f"מחיר נוכחי: {price}"
                    )

                    # מאפס היסטוריה כדי לא להציף בהתראות על אותו מטבע
                    price_history[symbol] = [(current_time, price)]

            except Exception as coin_error:
                print(f"שגיאה במטבע בודד: {coin_error}", flush=True)
                continue

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print(f"שגיאה כללית בלולאה הראשית: {e}", flush=True)
        time.sleep(10)
