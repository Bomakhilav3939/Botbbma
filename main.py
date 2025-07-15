import time
from config import SYMBOLS, TIMEFRAMES
from bbma import fetch_data, parse_indicators, detect_signal
from utils import send_telegram_message

def run():
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            print(f"Cek {symbol} TF {tf}")
            data = fetch_data(symbol, tf)
            if not data:
                continue
            parsed = parse_indicators(data)
            signal = detect_signal(parsed)
            if signal:
                msg = f"<b>{symbol}</b> - <b>{tf}</b>\nSinyal: <b>{signal}</b>"
                send_telegram_message(msg)

if __name__ == "__main__":
    while True:
        run()
        time.sleep(1800)